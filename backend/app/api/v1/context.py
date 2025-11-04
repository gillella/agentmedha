"""
Context API Endpoints

Test and debug context retrieval system.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.base import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.services.context_manager import get_context_manager
from app.services.embedding import get_embedding_service
from app.services.cache import cache
from app.models.semantic_layer import Metric, BusinessGlossary, BusinessRule
import structlog

logger = structlog.get_logger()

router = APIRouter()


# Request/Response Schemas

class ContextRequest(BaseModel):
    """Request for context retrieval"""
    query: str = Field(..., description="User's query text")
    database_id: int = Field(..., description="Database connection ID")
    tables: List[str] = Field(default=[], description="Relevant table names")
    max_tokens: int = Field(default=8000, description="Maximum tokens for context")
    include_examples: bool = Field(default=True, description="Include similar query examples")
    use_cache: bool = Field(default=True, description="Use cached context if available")


class ContextResponse(BaseModel):
    """Response with context and metadata"""
    context: str = Field(..., description="Assembled context string")
    metadata: dict = Field(..., description="Information about included items")
    stats: dict = Field(..., description="Token counts and performance stats")


class SimilaritySearchRequest(BaseModel):
    """Request for similarity search"""
    query: str = Field(..., description="Search query")
    namespace: str = Field(..., description="Namespace to search (metrics, glossary, etc.)")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results")
    threshold: float = Field(default=0.5, ge=0, le=1, description="Minimum similarity score")


class SimilaritySearchResult(BaseModel):
    """Similarity search result item"""
    object_id: str
    content: str
    metadata: dict
    similarity: float


class MetricResponse(BaseModel):
    """Business metric response"""
    id: int
    name: str
    display_name: str
    description: Optional[str]
    sql_definition: str
    certified: bool
    owner: Optional[str]
    tags: List[str]
    typical_questions: List[str]


class GlossaryTermResponse(BaseModel):
    """Glossary term response"""
    id: int
    term: str
    definition: str
    category: Optional[str]
    synonyms: List[str]
    examples: List[str]


class BusinessRuleResponse(BaseModel):
    """Business rule response"""
    id: int
    rule_type: str
    name: str
    definition: dict
    applies_to: List[str]
    active: bool


# API Endpoints

@router.post("/retrieve", response_model=ContextResponse)
async def retrieve_context(
    request: ContextRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve optimized context for a query
    
    This is the main endpoint for testing context retrieval.
    """
    try:
        logger.info(
            "context.retrieve",
            user_id=current_user.id,
            query=request.query[:100],
            database_id=request.database_id
        )
        
        # Get context manager
        context_mgr = get_context_manager(db, cache)
        
        # Get user permissions
        user_permissions = {
            "user_id": current_user.id,
            "role": current_user.role,
            "can_query": True  # TODO: Get from actual permissions
        }
        
        # Retrieve context
        result = await context_mgr.get_context_for_query(
            query=request.query,
            database_id=request.database_id,
            tables=request.tables,
            user_permissions=user_permissions,
            max_tokens=request.max_tokens,
            include_examples=request.include_examples,
            use_cache=request.use_cache
        )
        
        logger.info(
            "context.retrieved",
            context_tokens=result["stats"]["context_tokens"],
            items_included=result["metadata"]["items_included"],
            cache_hit=result["stats"]["cache_hit"]
        )
        
        return ContextResponse(**result)
        
    except Exception as e:
        logger.error("context.retrieve_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve context: {str(e)}"
        )


@router.post("/search", response_model=List[SimilaritySearchResult])
async def similarity_search(
    request: SimilaritySearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform similarity search in embeddings
    
    Search for similar items in a specific namespace.
    """
    try:
        logger.info(
            "context.similarity_search",
            user_id=current_user.id,
            namespace=request.namespace,
            query=request.query[:100]
        )
        
        # Get embedding service
        embedding_service = get_embedding_service()
        
        # Search
        results = await embedding_service.similarity_search(
            db=db,
            query=request.query,
            namespace=request.namespace,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        logger.info(
            "context.search_complete",
            namespace=request.namespace,
            results_count=len(results)
        )
        
        return [SimilaritySearchResult(**r) for r in results]
        
    except Exception as e:
        logger.error("context.search_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Similarity search failed: {str(e)}"
        )


@router.get("/metrics", response_model=List[MetricResponse])
async def list_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    certified_only: bool = False,
    limit: int = 20
):
    """
    List available business metrics
    """
    try:
        query = db.query(Metric)
        
        if certified_only:
            query = query.filter(Metric.certified == True)
        
        metrics = query.limit(limit).all()
        
        return [
            MetricResponse(
                id=m.id,
                name=m.name,
                display_name=m.display_name,
                description=m.description,
                sql_definition=m.sql_definition,
                certified=m.certified or False,
                owner=m.owner,
                tags=m.tags or [],
                typical_questions=m.typical_questions or []
            )
            for m in metrics
        ]
        
    except Exception as e:
        logger.error("context.list_metrics_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list metrics: {str(e)}"
        )


@router.get("/glossary", response_model=List[GlossaryTermResponse])
async def list_glossary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category: Optional[str] = None,
    limit: int = 20
):
    """
    List business glossary terms
    """
    try:
        query = db.query(BusinessGlossary)
        
        if category:
            query = query.filter(BusinessGlossary.category == category)
        
        terms = query.limit(limit).all()
        
        return [
            GlossaryTermResponse(
                id=t.id,
                term=t.term,
                definition=t.definition,
                category=t.category,
                synonyms=t.synonyms or [],
                examples=t.examples or []
            )
            for t in terms
        ]
        
    except Exception as e:
        logger.error("context.list_glossary_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list glossary: {str(e)}"
        )


@router.get("/rules", response_model=List[BusinessRuleResponse])
async def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rule_type: Optional[str] = None,
    active_only: bool = True
):
    """
    List business rules
    """
    try:
        query = db.query(BusinessRule)
        
        if active_only:
            query = query.filter(BusinessRule.active == True)
        
        if rule_type:
            query = query.filter(BusinessRule.rule_type == rule_type)
        
        rules = query.all()
        
        return [
            BusinessRuleResponse(
                id=r.id,
                rule_type=r.rule_type,
                name=r.name,
                definition=r.definition or {},
                applies_to=r.applies_to or [],
                active=r.active or False
            )
            for r in rules
        ]
        
    except Exception as e:
        logger.error("context.list_rules_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list rules: {str(e)}"
        )


@router.delete("/cache")
async def clear_context_cache(
    database_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Clear context cache
    
    Invalidate cached context for a specific database or all databases.
    """
    try:
        # Check if user is admin
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can clear cache"
            )
        
        context_mgr = get_context_manager(get_db(), cache)
        
        deleted_count = await context_mgr.invalidate_cache(database_id=database_id)
        
        logger.info(
            "context.cache_cleared",
            user_id=current_user.id,
            database_id=database_id,
            deleted_count=deleted_count
        )
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Cleared {deleted_count} cache entries"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("context.cache_clear_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.get("/stats")
async def get_context_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about the context system
    """
    try:
        # Count items in semantic layer
        metrics_count = db.query(Metric).count()
        glossary_count = db.query(BusinessGlossary).count()
        rules_count = db.query(BusinessRule).count()
        
        # Count embeddings by namespace
        from sqlalchemy import text, func
        
        embeddings_query = text("""
            SELECT namespace, COUNT(*) as count
            FROM embeddings
            GROUP BY namespace
        """)
        
        embeddings_result = db.execute(embeddings_query)
        embeddings_by_namespace = {
            row.namespace: row.count
            for row in embeddings_result
        }
        
        # Cache stats (if available)
        cache_stats = {}
        if cache._connected:
            cache_stats = {
                "connected": True,
                "info": "Redis cache operational"
            }
        
        return {
            "semantic_layer": {
                "metrics": metrics_count,
                "glossary_terms": glossary_count,
                "business_rules": rules_count
            },
            "embeddings": embeddings_by_namespace,
            "cache": cache_stats,
            "status": "operational"
        }
        
    except Exception as e:
        logger.error("context.stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


