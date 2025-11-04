"""Context Manager

Orchestrates context retrieval, optimization, and delivery.
This is the main entry point for all context engineering operations.
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.services.context_retriever import ContextRetriever, get_context_retriever
from app.services.context_optimizer import ContextOptimizer, get_context_optimizer
from app.services.cache import CacheService
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Orchestrate context retrieval, optimization, and delivery
    
    This is the main service that agents will use to get context
    for their queries. It handles:
    - Retrieving relevant context from multiple sources
    - Optimizing context to fit within token budgets
    - Caching assembled context for performance
    - Logging and monitoring
    """
    
    def __init__(
        self,
        db: Session,
        retriever: Optional[ContextRetriever] = None,
        optimizer: Optional[ContextOptimizer] = None,
        cache: Optional[CacheService] = None
    ):
        self.db = db
        self.retriever = retriever or get_context_retriever(db, cache)
        self.optimizer = optimizer or get_context_optimizer()
        self.cache = cache
    
    async def get_context_for_query(
        self,
        query: str,
        database_id: int,
        tables: List[str],
        user_permissions: Dict,
        max_tokens: int = 8000,
        include_examples: bool = True,
        use_cache: bool = True
    ) -> Dict:
        """
        Get optimized context for a query
        
        This is the main entry point that agents will call.
        
        Args:
            query: User's query text
            database_id: Database connection ID
            tables: List of relevant table names
            user_permissions: User's access permissions
            max_tokens: Maximum tokens for context
            include_examples: Whether to include similar query examples
            use_cache: Whether to use cached context
            
        Returns:
            Dict with:
                - context: Assembled context string
                - metadata: Info about what was included
                - stats: Token counts, cache hit, etc.
        """
        # Generate cache key
        cache_key = self._generate_cache_key(
            query, database_id, tables, max_tokens
        )
        
        # Try cache first
        if use_cache and self.cache:
            cached = await self._get_from_cache(cache_key)
            if cached:
                logger.info(f"Context cache HIT for query")
                return cached
        
        logger.info(f"Context cache MISS, retrieving fresh context")
        
        # Retrieve all relevant context
        context_dict = await self.retriever.retrieve_all_context(
            query=query,
            database_id=database_id,
            tables=tables,
            user_permissions=user_permissions,
            include_examples=include_examples
        )
        
        # Convert to list of items for optimization
        context_items = self._flatten_context(context_dict)
        
        # Count query tokens
        query_tokens = self.optimizer.count_tokens(query)
        
        # Optimize to fit budget
        optimized_context = self.optimizer.optimize(
            context_items=context_items,
            query_tokens=query_tokens,
            reserved_for_response=1000
        )
        
        # Count final tokens
        context_tokens = self.optimizer.count_tokens(optimized_context)
        
        # Build result
        result = {
            "context": optimized_context,
            "metadata": {
                "items_available": len(context_items),
                "items_included": self._count_included_items(
                    optimized_context, context_dict
                ),
                "metrics_count": len(context_dict.get("metrics", [])),
                "examples_count": len(context_dict.get("examples", [])),
                "rules_count": len(context_dict.get("rules", [])),
                "glossary_count": len(context_dict.get("glossary", [])),
            },
            "stats": {
                "query_tokens": query_tokens,
                "context_tokens": context_tokens,
                "total_tokens": query_tokens + context_tokens,
                "max_tokens": max_tokens,
                "utilization": context_tokens / max_tokens * 100,
                "cache_hit": False
            }
        }
        
        # Cache result
        if use_cache and self.cache:
            await self._save_to_cache(cache_key, result)
        
        logger.info(
            f"Context assembled: {context_tokens} tokens "
            f"({result['stats']['utilization']:.1f}% of budget), "
            f"{result['metadata']['items_included']} items included"
        )
        
        return result
    
    async def get_context_for_follow_up(
        self,
        query: str,
        previous_context: Dict,
        conversation_history: List[Dict],
        max_tokens: int = 8000
    ) -> Dict:
        """
        Get context for a follow-up question
        
        This optimizes for conversational queries by reusing
        relevant context from previous turns.
        
        Args:
            query: Follow-up query
            previous_context: Context from previous query
            conversation_history: Previous turns in conversation
            max_tokens: Maximum tokens for context
            
        Returns:
            Dict with context and metadata
        """
        logger.info("Getting context for follow-up question")
        
        # Extract relevant context from previous turn
        previous_items = previous_context.get("items", [])
        
        # Add conversation history as context
        history_items = []
        for turn in conversation_history[-3:]:  # Last 3 turns
            history_items.append({
                "type": "history",
                "content": f"Q: {turn['question']}\nA: {turn['answer']}",
                "relevance": 0.8
            })
        
        # Combine with previous context (but reduce relevance)
        for item in previous_items:
            item["relevance"] = item.get("relevance", 0.5) * 0.8  # Decay
        
        all_items = history_items + previous_items
        
        # Optimize
        query_tokens = self.optimizer.count_tokens(query)
        optimized_context = self.optimizer.optimize(
            context_items=all_items,
            query_tokens=query_tokens,
            reserved_for_response=1000
        )
        
        context_tokens = self.optimizer.count_tokens(optimized_context)
        
        return {
            "context": optimized_context,
            "metadata": {
                "items_included": len(history_items) + len(previous_items),
                "history_turns": len(history_items)
            },
            "stats": {
                "query_tokens": query_tokens,
                "context_tokens": context_tokens,
                "total_tokens": query_tokens + context_tokens,
                "max_tokens": max_tokens
            }
        }
    
    def _flatten_context(self, context_dict: Dict) -> List[Dict]:
        """
        Convert nested context dict to flat list of items
        
        Each item has: type, content, relevance
        """
        items = []
        
        # Schema items (always highest relevance)
        if "schema" in context_dict:
            for table, info in context_dict["schema"].items():
                items.append({
                    "type": "schema",
                    "table": table,
                    "columns": info.get("columns", []),
                    "primary_keys": info.get("primary_keys", []),
                    "foreign_keys": info.get("foreign_keys", []),
                    "relevance": 1.0  # Always include schema
                })
        
        # Metric items
        for metric in context_dict.get("metrics", []):
            items.append({
                "type": "metric",
                **metric,
                "relevance": metric.get("similarity", 0.8)
            })
        
        # Glossary items
        for term in context_dict.get("glossary", []):
            items.append({
                "type": "glossary",
                **term,
                "relevance": term.get("similarity", 0.6)
            })
        
        # Example query items
        for example in context_dict.get("examples", []):
            items.append({
                "type": "example",
                **example,
                "relevance": example.get("similarity", 0.7)
            })
        
        # Business rule items
        for rule in context_dict.get("rules", []):
            items.append({
                "type": "rule",
                **rule,
                "relevance": 0.9  # Rules are important
            })
        
        # Permissions (always include)
        if "permissions" in context_dict:
            items.append({
                "type": "permissions",
                "content": json.dumps(context_dict["permissions"], indent=2),
                "relevance": 1.0
            })
        
        return items
    
    def _count_included_items(
        self,
        optimized_context: str,
        original_context: Dict
    ) -> int:
        """Count how many items were included in optimized context"""
        # Simple heuristic: count section headers
        sections = [
            "## Database Schema",
            "## Business Metrics",
            "## Business Rules",
            "## Example Queries",
            "## Business Glossary"
        ]
        return sum(1 for s in sections if s in optimized_context)
    
    def _generate_cache_key(
        self,
        query: str,
        database_id: int,
        tables: List[str],
        max_tokens: int
    ) -> str:
        """
        Generate cache key for context
        
        Note: We hash the query to handle variations
        """
        # Normalize query (lowercase, strip whitespace)
        normalized_query = ' '.join(query.lower().split())
        
        key_components = [
            normalized_query,
            str(database_id),
            ':'.join(sorted(tables)),
            str(max_tokens)
        ]
        key_str = '|'.join(key_components)
        
        # Hash to fixed length
        hash_hex = hashlib.md5(key_str.encode()).hexdigest()
        return f"context:v1:{hash_hex}"
    
    async def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get context from cache"""
        try:
            cached_str = await self.cache.get(cache_key)
            if cached_str:
                result = json.loads(cached_str)
                result["stats"]["cache_hit"] = True
                return result
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")
        return None
    
    async def _save_to_cache(self, cache_key: str, result: Dict) -> None:
        """Save context to cache"""
        try:
            # Cache for 1 hour
            await self.cache.set(
                cache_key,
                json.dumps(result),
                ttl=3600
            )
            logger.debug(f"Saved context to cache: {cache_key}")
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    async def invalidate_cache(
        self,
        database_id: Optional[int] = None,
        pattern: Optional[str] = None
    ) -> int:
        """
        Invalidate cached context
        
        Args:
            database_id: Invalidate for specific database
            pattern: Custom pattern to match
            
        Returns:
            Number of keys invalidated
        """
        if not self.cache:
            return 0
        
        try:
            if pattern:
                return await self.cache.delete_pattern(pattern)
            elif database_id:
                pattern = f"context:v1:*{database_id}*"
                return await self.cache.delete_pattern(pattern)
            else:
                pattern = "context:v1:*"
                return await self.cache.delete_pattern(pattern)
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return 0


def get_context_manager(
    db: Session,
    cache_service: Optional[CacheService] = None,
    max_tokens: int = 8000
) -> ContextManager:
    """Factory function to create ContextManager"""
    return ContextManager(
        db=db,
        retriever=get_context_retriever(db, cache_service),
        optimizer=get_context_optimizer(max_tokens),
        cache=cache_service
    )












