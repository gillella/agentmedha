"""
Tests for Context Engineering System

Tests cover:
- EmbeddingService
- ContextRetriever
- ContextOptimizer
- ContextManager
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session

from app.services.embedding import EmbeddingService
from app.services.context_retriever import ContextRetriever
from app.services.context_optimizer import ContextOptimizer
from app.services.context_manager import ContextManager
from app.models.semantic_layer import Metric, BusinessGlossary, BusinessRule


class TestEmbeddingService:
    """Test embedding generation and similarity search"""
    
    def test_generate_embedding(self):
        """Test basic embedding generation"""
        service = EmbeddingService()
        
        text = "What is our total revenue?"
        embedding = service.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
        assert all(isinstance(x, float) for x in embedding)
    
    def test_generate_embedding_empty_text(self):
        """Test embedding with empty text"""
        service = EmbeddingService()
        
        embedding = service.generate_embedding("")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(x == 0.0 for x in embedding)
    
    def test_generate_embeddings_batch(self):
        """Test batch embedding generation"""
        service = EmbeddingService()
        
        texts = [
            "What is our revenue?",
            "Show me customer churn",
            "Top products by sales"
        ]
        embeddings = service.generate_embeddings_batch(texts)
        
        assert len(embeddings) == 3
        assert all(len(e) == 384 for e in embeddings)
    
    @pytest.mark.asyncio
    async def test_store_and_search_embedding(self, db_session):
        """Test storing and searching embeddings"""
        service = EmbeddingService()
        
        # Store test embeddings
        await service.store_embedding(
            db=db_session,
            namespace="test_metrics",
            object_id="revenue_001",
            content="Total revenue from all sources",
            metadata={"metric_name": "revenue"}
        )
        
        await service.store_embedding(
            db=db_session,
            namespace="test_metrics",
            object_id="profit_001",
            content="Net profit after expenses",
            metadata={"metric_name": "profit"}
        )
        
        # Search for similar
        query = "What is our total revenue?"
        results = await service.similarity_search(
            db=db_session,
            query=query,
            namespace="test_metrics",
            top_k=2,
            threshold=0.3
        )
        
        assert len(results) > 0
        assert results[0]["object_id"] in ["revenue_001", "profit_001"]
        assert 0 <= results[0]["similarity"] <= 1
    
    @pytest.mark.asyncio
    async def test_delete_embeddings(self, db_session):
        """Test deleting embeddings"""
        service = EmbeddingService()
        
        # Store test embedding
        await service.store_embedding(
            db=db_session,
            namespace="test_delete",
            object_id="test_001",
            content="Test content"
        )
        
        # Delete
        deleted = await service.delete_embeddings(
            db=db_session,
            namespace="test_delete",
            object_ids=["test_001"]
        )
        
        assert deleted >= 0


class TestContextOptimizer:
    """Test context optimization and token management"""
    
    def test_token_counting(self):
        """Test token counting"""
        optimizer = ContextOptimizer(max_tokens=8000)
        
        text = "This is a test sentence."
        tokens = optimizer.count_tokens(text)
        
        assert tokens > 0
        assert tokens < 20  # Should be around 6-7 tokens
    
    def test_token_counting_empty(self):
        """Test token counting with empty string"""
        optimizer = ContextOptimizer()
        
        tokens = optimizer.count_tokens("")
        assert tokens == 0
    
    def test_context_optimization_within_budget(self):
        """Test fitting context within token budget"""
        optimizer = ContextOptimizer(max_tokens=1000)
        
        items = [
            {
                "type": "schema",
                "content": "Table: users\nColumns: id, name, email",
                "relevance": 1.0
            },
            {
                "type": "metric",
                "content": "Revenue = SUM(orders.total)",
                "relevance": 0.9
            },
            {
                "type": "example",
                "content": "SELECT * FROM users WHERE active = true",
                "relevance": 0.5
            }
        ]
        
        result = optimizer.optimize(
            context_items=items,
            query_tokens=50,
            reserved_for_response=100
        )
        
        assert isinstance(result, str)
        tokens = optimizer.count_tokens(result)
        assert tokens <= (1000 - 50 - 100)  # Within budget
        assert "Table: users" in result  # High priority included
    
    def test_priority_ordering(self):
        """Test that high priority items are selected first"""
        optimizer = ContextOptimizer(max_tokens=500)
        
        items = [
            {
                "type": "glossary",  # Low priority (20)
                "content": "x" * 200,
                "relevance": 1.0
            },
            {
                "type": "schema",  # High priority (100)
                "content": "y" * 100,
                "relevance": 1.0
            }
        ]
        
        result = optimizer.optimize(
            context_items=items,
            query_tokens=10,
            reserved_for_response=100
        )
        
        # Schema should be included, glossary maybe not
        assert "y" in result
    
    def test_format_metric(self):
        """Test formatting metric items"""
        optimizer = ContextOptimizer()
        
        metric = {
            "type": "metric",
            "name": "revenue",
            "display_name": "Total Revenue",
            "description": "Sum of all sales",
            "sql_definition": "SUM(orders.total)",
            "certified": True
        }
        
        formatted = optimizer._format_metric(metric)
        
        assert "Total Revenue" in formatted
        assert "SUM(orders.total)" in formatted
        assert "Certified" in formatted
    
    def test_cost_estimation(self):
        """Test API cost estimation"""
        optimizer = ContextOptimizer()
        
        costs = optimizer.estimate_cost(
            context_tokens=2000,
            query_tokens=100,
            response_tokens=500
        )
        
        assert "gpt-4-turbo" in costs
        assert "gpt-3.5-turbo" in costs
        assert costs["gpt-4-turbo"]["total_cost"] > 0
        assert costs["gpt-4-turbo"]["total_tokens"] == 2600


class TestContextRetriever:
    """Test context retrieval"""
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_metrics(self, db_session):
        """Test metric retrieval"""
        # Create test metrics
        metric = Metric(
            name="revenue",
            display_name="Total Revenue",
            description="Sum of all sales",
            sql_definition="SUM(orders.total)",
            certified=True,
            owner="CFO"
        )
        db_session.add(metric)
        db_session.commit()
        
        # Create embeddings
        embedding_service = EmbeddingService()
        await embedding_service.store_embedding(
            db=db_session,
            namespace="metrics",
            object_id=str(metric.id),
            content=f"{metric.display_name} {metric.description}"
        )
        
        # Retrieve
        retriever = ContextRetriever(db=db_session)
        results = await retriever.retrieve_relevant_metrics(
            query="What is our total revenue?",
            top_k=1
        )
        
        assert len(results) > 0
        assert results[0]["name"] == "revenue"
        assert "similarity" in results[0]
    
    @pytest.mark.asyncio
    async def test_retrieve_business_rules(self, db_session):
        """Test business rule retrieval"""
        # Create test rule
        rule = BusinessRule(
            rule_type="fiscal_calendar",
            name="Fiscal Year",
            definition={"start": "November 1"},
            active=True
        )
        db_session.add(rule)
        db_session.commit()
        
        # Retrieve
        retriever = ContextRetriever(db=db_session)
        results = await retriever.retrieve_business_rules(
            rule_types=["fiscal_calendar"]
        )
        
        assert len(results) > 0
        assert results[0]["rule_type"] == "fiscal_calendar"
    
    @pytest.mark.asyncio
    async def test_retrieve_all_context(self, db_session):
        """Test retrieving all context types"""
        retriever = ContextRetriever(db=db_session)
        
        context = await retriever.retrieve_all_context(
            query="Show me revenue",
            database_id=1,
            tables=["orders"],
            user_permissions={"can_query": True},
            include_examples=True
        )
        
        assert isinstance(context, dict)
        assert "metrics" in context
        assert "glossary" in context
        assert "rules" in context
        assert "permissions" in context


class TestContextManager:
    """Test context orchestration"""
    
    @pytest.mark.asyncio
    async def test_get_context_for_query(self, db_session):
        """Test end-to-end context retrieval"""
        manager = ContextManager(db=db_session)
        
        result = await manager.get_context_for_query(
            query="What is our total revenue?",
            database_id=1,
            tables=["orders", "customers"],
            user_permissions={"can_query": True},
            max_tokens=8000,
            use_cache=False  # Don't cache in tests
        )
        
        assert "context" in result
        assert "metadata" in result
        assert "stats" in result
        
        # Check stats
        assert result["stats"]["query_tokens"] > 0
        assert result["stats"]["context_tokens"] >= 0
        assert result["stats"]["utilization"] >= 0
        assert result["stats"]["cache_hit"] == False
    
    @pytest.mark.asyncio
    async def test_context_caching(self, db_session):
        """Test context caching"""
        # Mock cache service
        mock_cache = AsyncMock()
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock()
        
        manager = ContextManager(db=db_session, cache=mock_cache)
        
        # First call - should save to cache
        result1 = await manager.get_context_for_query(
            query="Show me revenue",
            database_id=1,
            tables=["orders"],
            user_permissions={},
            use_cache=True
        )
        
        # Cache.set should be called
        assert mock_cache.set.called
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, db_session):
        """Test cache key generation"""
        manager = ContextManager(db=db_session)
        
        key1 = manager._generate_cache_key(
            query="What is revenue?",
            database_id=1,
            tables=["orders"],
            max_tokens=8000
        )
        
        key2 = manager._generate_cache_key(
            query="what is revenue?",  # Different case
            database_id=1,
            tables=["orders"],
            max_tokens=8000
        )
        
        # Should be same (case insensitive)
        assert key1 == key2
        
        key3 = manager._generate_cache_key(
            query="What is revenue?",
            database_id=2,  # Different database
            tables=["orders"],
            max_tokens=8000
        )
        
        # Should be different
        assert key1 != key3
    
    @pytest.mark.asyncio
    async def test_flatten_context(self, db_session):
        """Test context flattening"""
        manager = ContextManager(db=db_session)
        
        context_dict = {
            "metrics": [
                {
                    "name": "revenue",
                    "display_name": "Revenue",
                    "similarity": 0.9
                }
            ],
            "glossary": [
                {
                    "term": "churn",
                    "definition": "Customer loss",
                    "similarity": 0.7
                }
            ],
            "permissions": {"can_query": True}
        }
        
        items = manager._flatten_context(context_dict)
        
        assert len(items) == 3  # metric, glossary, permissions
        assert all("type" in item for item in items)
        assert all("relevance" in item for item in items)


class TestIntegration:
    """Integration tests for the full context system"""
    
    @pytest.mark.asyncio
    async def test_full_context_pipeline(self, db_session):
        """Test complete context retrieval pipeline"""
        # 1. Create test data
        metric = Metric(
            name="arr",
            display_name="Annual Recurring Revenue",
            description="Recurring revenue annualized",
            sql_definition="SUM(subscriptions.amount * 12)",
            certified=True
        )
        db_session.add(metric)
        db_session.commit()
        
        # 2. Create embeddings
        embedding_service = EmbeddingService()
        await embedding_service.store_embedding(
            db=db_session,
            namespace="metrics",
            object_id=str(metric.id),
            content=f"{metric.display_name} {metric.description}"
        )
        
        # 3. Use context manager
        manager = ContextManager(db=db_session)
        
        result = await manager.get_context_for_query(
            query="What is our ARR?",
            database_id=1,
            tables=["subscriptions"],
            user_permissions={"role": "analyst"},
            max_tokens=8000,
            use_cache=False
        )
        
        # 4. Verify
        assert result["context"]  # Not empty
        assert result["stats"]["context_tokens"] > 0
        assert result["metadata"]["items_included"] > 0
    
    @pytest.mark.asyncio
    async def test_token_budget_enforcement(self, db_session):
        """Test that token budget is respected"""
        manager = ContextManager(db=db_session)
        
        # Very small budget
        result = await manager.get_context_for_query(
            query="What is our revenue?",
            database_id=1,
            tables=["orders"],
            user_permissions={},
            max_tokens=200,  # Very small
            use_cache=False
        )
        
        # Should respect budget
        total_tokens = (
            result["stats"]["query_tokens"] +
            result["stats"]["context_tokens"]
        )
        assert total_tokens <= 200


# Pytest fixtures

@pytest.fixture
def db_session():
    """Create a test database session"""
    # This would use your test database
    # For now, return a mock
    session = MagicMock(spec=Session)
    session.execute = MagicMock()
    session.commit = MagicMock()
    session.add = MagicMock()
    return session


if __name__ == "__main__":
    pytest.main([__file__, "-v"])












