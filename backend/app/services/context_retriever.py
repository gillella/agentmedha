"""Context Retriever Service

Retrieves relevant context for queries using multiple strategies:
- Semantic search for metrics, glossary terms, similar queries
- Schema retrieval for relevant tables
- Business rules retrieval
- User permissions

This is a key component of our context engineering system.
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.services.embedding import EmbeddingService, get_embedding_service
from app.services.cache import CacheService
from app.models.semantic_layer import Metric, BusinessGlossary, BusinessRule, DataLineage
from app.models.database import DatabaseConnection
import logging
import json

logger = logging.getLogger(__name__)


class ContextRetriever:
    """
    Retrieve relevant context for a query using multiple strategies
    
    This class is responsible for finding all relevant information
    needed to generate accurate SQL queries with business context.
    """
    
    def __init__(
        self,
        db: Session,
        embedding_service: Optional[EmbeddingService] = None,
        cache_service: Optional[CacheService] = None
    ):
        self.db = db
        self.embeddings = embedding_service or get_embedding_service()
        self.cache = cache_service
    
    async def retrieve_schema_context(
        self,
        database_id: int,
        tables: List[str]
    ) -> Dict:
        """
        Retrieve schema information for specific tables
        
        Args:
            database_id: Database connection ID
            tables: List of table names
            
        Returns:
            Dict with schema information
        """
        cache_key = f"schema:{database_id}:{':'.join(sorted(tables))}"
        
        # Try cache first
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"Schema context cache hit for {cache_key}")
                return json.loads(cached)
        
        # Fetch from database connection's schema manager
        # This would integrate with your existing schema_manager service
        schema_context = await self._fetch_schema_from_db(database_id, tables)
        
        # Cache for 1 hour
        if self.cache:
            await self.cache.set(cache_key, json.dumps(schema_context), ttl=3600)
        
        return schema_context
    
    async def _fetch_schema_from_db(
        self,
        database_id: int,
        tables: List[str]
    ) -> Dict:
        """
        Fetch schema from database
        
        TODO: Integrate with existing schema_manager service
        """
        # Placeholder - would integrate with your schema manager
        schema = {}
        for table in tables:
            schema[table] = {
                "columns": [],  # Would be filled by schema manager
                "primary_keys": [],
                "foreign_keys": [],
                "indexes": []
            }
        return schema
    
    async def retrieve_relevant_metrics(
        self,
        query: str,
        top_k: int = 3,
        include_uncertified: bool = True
    ) -> List[Dict]:
        """
        Find business metrics relevant to the query
        
        Args:
            query: User's query text
            top_k: Number of metrics to return
            include_uncertified: Whether to include uncertified metrics
            
        Returns:
            List of relevant metrics with similarity scores
        """
        try:
            # Semantic search in embeddings
            similar = await self.embeddings.similarity_search(
                self.db,
                query=query,
                namespace="metrics",
                top_k=top_k * 2,  # Get more, filter later
                threshold=0.5
            )
            
            if not similar:
                logger.info("No similar metrics found")
                return []
            
            # Fetch full metric details
            metric_ids = [s["object_id"] for s in similar]
            stmt = select(Metric).where(Metric.id.in_(metric_ids))
            
            if not include_uncertified:
                stmt = stmt.where(Metric.certified == True)
            
            result = self.db.execute(stmt)
            metrics = result.scalars().all()
            
            # Build result with similarity scores
            metric_dict = {str(m.id): m for m in metrics}
            results = []
            
            for sim in similar:
                metric_id = sim["object_id"]
                if metric_id in metric_dict:
                    m = metric_dict[metric_id]
                    results.append({
                        "id": str(m.id),
                        "name": m.name,
                        "display_name": m.display_name,
                        "description": m.description,
                        "sql_definition": m.sql_definition,
                        "data_sources": m.data_sources,
                        "format": m.format,
                        "filters": m.filters,
                        "certified": m.certified,
                        "owner": m.owner,
                        "typical_questions": m.typical_questions,
                        "related_metrics": m.related_metrics,
                        "similarity": sim["similarity"]
                    })
            
            # Sort by similarity
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            logger.info(f"Found {len(results)} relevant metrics")
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error retrieving relevant metrics: {e}")
            return []
    
    async def retrieve_glossary_terms(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find relevant business glossary terms
        
        Args:
            query: User's query text
            top_k: Number of terms to return
            
        Returns:
            List of relevant glossary terms
        """
        try:
            similar = await self.embeddings.similarity_search(
                self.db,
                query=query,
                namespace="glossary",
                top_k=top_k,
                threshold=0.6  # Higher threshold for glossary
            )
            
            if not similar:
                return []
            
            # Fetch full glossary details
            term_ids = [s["object_id"] for s in similar]
            stmt = select(BusinessGlossary).where(BusinessGlossary.id.in_(term_ids))
            result = self.db.execute(stmt)
            terms = result.scalars().all()
            
            term_dict = {str(t.id): t for t in terms}
            results = []
            
            for sim in similar:
                term_id = sim["object_id"]
                if term_id in term_dict:
                    t = term_dict[term_id]
                    results.append({
                        "term": t.term,
                        "definition": t.definition,
                        "category": t.category,
                        "synonyms": t.synonyms,
                        "examples": t.examples,
                        "similarity": sim["similarity"]
                    })
            
            logger.info(f"Found {len(results)} relevant glossary terms")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving glossary terms: {e}")
            return []
    
    async def retrieve_similar_queries(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.7
    ) -> List[Dict]:
        """
        Find similar successful historical queries (RAG approach)
        
        Args:
            query: User's query text
            top_k: Number of queries to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similar queries with SQL and explanations
        """
        try:
            similar = await self.embeddings.similarity_search(
                self.db,
                query=query,
                namespace="successful_queries",
                top_k=top_k,
                threshold=min_similarity
            )
            
            # Filter for successful queries only
            results = [
                {
                    "question": s["metadata"].get("question", s["content"]),
                    "sql": s["metadata"].get("sql", ""),
                    "explanation": s["metadata"].get("explanation", ""),
                    "database": s["metadata"].get("database", ""),
                    "similarity": s["similarity"],
                    "success_rate": s["metadata"].get("success_rate", 1.0)
                }
                for s in similar
                if s["metadata"].get("success", True)
            ]
            
            logger.info(f"Found {len(results)} similar historical queries")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving similar queries: {e}")
            return []
    
    async def retrieve_business_rules(
        self,
        rule_types: Optional[List[str]] = None,
        applies_to: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Retrieve business rules
        
        Args:
            rule_types: Optional list of rule types to retrieve
            applies_to: Optional list of databases/tables the rules apply to
            
        Returns:
            List of business rules
        """
        cache_key = f"rules:{':'.join(sorted(rule_types or []))}"
        
        # Try cache
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"Business rules cache hit")
                return json.loads(cached)
        
        try:
            stmt = select(BusinessRule).where(BusinessRule.active == True)
            
            if rule_types:
                stmt = stmt.where(BusinessRule.rule_type.in_(rule_types))
            
            result = self.db.execute(stmt)
            rules = result.scalars().all()
            
            results = [
                {
                    "rule_type": r.rule_type,
                    "name": r.name,
                    "definition": r.definition,
                    "applies_to": r.applies_to
                }
                for r in rules
            ]
            
            # Cache for 24 hours
            if self.cache:
                await self.cache.set(cache_key, json.dumps(results), ttl=86400)
            
            logger.info(f"Retrieved {len(results)} business rules")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving business rules: {e}")
            return []
    
    async def retrieve_data_lineage(
        self,
        database: str,
        table: str,
        direction: str = "both"
    ) -> Dict:
        """
        Retrieve data lineage for a table
        
        Args:
            database: Database name
            table: Table name
            direction: 'upstream', 'downstream', or 'both'
            
        Returns:
            Dict with upstream and/or downstream lineage
        """
        try:
            lineage = {"upstream": [], "downstream": []}
            
            if direction in ["upstream", "both"]:
                stmt = select(DataLineage).where(
                    DataLineage.target_database == database,
                    DataLineage.target_table == table
                )
                result = self.db.execute(stmt)
                upstream = result.scalars().all()
                lineage["upstream"] = [
                    {
                        "database": l.source_database,
                        "table": l.source_table,
                        "relationship_type": l.relationship_type,
                        "transformation": l.transformation_logic
                    }
                    for l in upstream
                ]
            
            if direction in ["downstream", "both"]:
                stmt = select(DataLineage).where(
                    DataLineage.source_database == database,
                    DataLineage.source_table == table
                )
                result = self.db.execute(stmt)
                downstream = result.scalars().all()
                lineage["downstream"] = [
                    {
                        "database": l.target_database,
                        "table": l.target_table,
                        "relationship_type": l.relationship_type,
                        "transformation": l.transformation_logic
                    }
                    for l in downstream
                ]
            
            logger.info(
                f"Retrieved lineage for {database}.{table}: "
                f"{len(lineage['upstream'])} upstream, "
                f"{len(lineage['downstream'])} downstream"
            )
            return lineage
            
        except Exception as e:
            logger.error(f"Error retrieving data lineage: {e}")
            return {"upstream": [], "downstream": []}
    
    async def retrieve_all_context(
        self,
        query: str,
        database_id: int,
        tables: List[str],
        user_permissions: Dict,
        include_examples: bool = True
    ) -> Dict:
        """
        Retrieve all relevant context for a query
        
        This is the main entry point that orchestrates all context retrieval.
        
        Args:
            query: User's query text
            database_id: Database connection ID
            tables: List of table names mentioned/relevant
            user_permissions: User's access permissions
            include_examples: Whether to include similar query examples
            
        Returns:
            Dict with all context organized by type
        """
        logger.info(f"Retrieving context for query: {query[:100]}...")
        
        context = {}
        
        try:
            # 1. Schema context (CRITICAL)
            if tables:
                context["schema"] = await self.retrieve_schema_context(
                    database_id, tables
                )
            
            # 2. Business metrics (CRITICAL)
            context["metrics"] = await self.retrieve_relevant_metrics(
                query, top_k=3
            )
            
            # 3. Glossary terms (MEDIUM priority)
            context["glossary"] = await self.retrieve_glossary_terms(
                query, top_k=5
            )
            
            # 4. Similar queries (MEDIUM priority - only if enabled)
            if include_examples:
                context["examples"] = await self.retrieve_similar_queries(
                    query, top_k=3
                )
            
            # 5. Business rules (HIGH priority)
            context["rules"] = await self.retrieve_business_rules(
                rule_types=["fiscal_calendar", "data_retention"]
            )
            
            # 6. User permissions (CRITICAL)
            context["permissions"] = user_permissions
            
            # Log context summary
            logger.info(
                f"Context retrieved: "
                f"metrics={len(context.get('metrics', []))}, "
                f"glossary={len(context.get('glossary', []))}, "
                f"examples={len(context.get('examples', []))}, "
                f"rules={len(context.get('rules', []))}"
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return context  # Return partial context


def get_context_retriever(
    db: Session,
    cache_service: Optional[CacheService] = None
) -> ContextRetriever:
    """Factory function to create ContextRetriever"""
    return ContextRetriever(
        db=db,
        embedding_service=get_embedding_service(),
        cache_service=cache_service
    )












