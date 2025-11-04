# Sprint 1: Context Engineering Foundation
## Week 1-2 of 18-Sprint Roadmap

> **Goal**: Build the context system that powers everything else

---

## 🎯 Sprint Objectives

By the end of Sprint 1, we will have:

1. ✅ **Semantic layer database schema** designed and deployed
2. ✅ **Context retrieval system** operational with semantic search
3. ✅ **Multi-level caching** implemented (Redis + in-memory)
4. ✅ **Token optimizer** managing LLM context budgets
5. ✅ **Tests passing** with >80% coverage
6. ✅ **Documentation** complete

**Success Criteria**:
- Context can be retrieved in <100ms (P95)
- Cache hit rate >60%
- Context quality score >85%
- All tests green

---

## 📋 Detailed Task Breakdown

### Day 1-2: Database Schema Design

#### Task 1.1: Semantic Layer Tables
**Owner**: Backend Developer  
**Effort**: 4 hours  
**Priority**: Critical

**Files to Create**:
- `backend/app/models/semantic_layer.py`
- `backend/alembic/versions/003_semantic_layer.py`

**Tables to Create**:

```sql
-- Business Metrics
CREATE TABLE metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    sql_definition TEXT NOT NULL,
    data_sources JSONB,  -- List of tables/columns used
    aggregation VARCHAR(50),  -- sum, avg, count, etc.
    format VARCHAR(50),  -- currency, percentage, number
    filters JSONB,  -- Default filters
    owner VARCHAR(255),
    certified BOOLEAN DEFAULT FALSE,
    certification_date TIMESTAMP,
    tags TEXT[],
    typical_questions TEXT[],
    related_metrics TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

-- Business Glossary
CREATE TABLE business_glossary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    term VARCHAR(255) NOT NULL UNIQUE,
    definition TEXT NOT NULL,
    category VARCHAR(100),
    synonyms TEXT[],
    related_terms TEXT[],
    examples TEXT[],
    owner VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Business Rules
CREATE TABLE business_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_type VARCHAR(100) NOT NULL,  -- fiscal_calendar, data_retention, etc.
    name VARCHAR(255) NOT NULL,
    definition JSONB NOT NULL,
    applies_to TEXT[],  -- Which databases/tables
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Data Lineage
CREATE TABLE data_lineage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_table VARCHAR(255) NOT NULL,
    source_database VARCHAR(255) NOT NULL,
    target_table VARCHAR(255) NOT NULL,
    target_database VARCHAR(255) NOT NULL,
    relationship_type VARCHAR(50),  -- upstream, downstream, derived
    transformation_logic TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Context Cache (for performance)
CREATE TABLE context_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    context_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    relevance_score FLOAT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast retrieval
CREATE INDEX idx_metrics_name ON metrics(name);
CREATE INDEX idx_metrics_tags ON metrics USING GIN(tags);
CREATE INDEX idx_glossary_term ON business_glossary(term);
CREATE INDEX idx_rules_type ON business_rules(rule_type);
CREATE INDEX idx_lineage_source ON data_lineage(source_database, source_table);
CREATE INDEX idx_lineage_target ON data_lineage(target_database, target_table);
```

**Acceptance Criteria**:
- [ ] Migration file created
- [ ] Schema documented
- [ ] Indexes defined
- [ ] Can run `alembic upgrade head` successfully

---

#### Task 1.2: SQLAlchemy Models
**Owner**: Backend Developer  
**Effort**: 3 hours  
**Priority**: Critical

**File**: `backend/app/models/semantic_layer.py`

```python
from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from app.models.base import Base
import uuid

class Metric(Base):
    """Business metric definition"""
    __tablename__ = "metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    sql_definition = Column(Text, nullable=False)
    data_sources = Column(JSONB)
    aggregation = Column(String(50))
    format = Column(String(50))
    filters = Column(JSONB)
    owner = Column(String(255))
    certified = Column(Boolean, default=False)
    certification_date = Column(TIMESTAMP)
    tags = Column(ARRAY(Text))
    typical_questions = Column(ARRAY(Text))
    related_metrics = Column(ARRAY(Text))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey('users.id'))

class BusinessGlossary(Base):
    """Business terminology definitions"""
    __tablename__ = "business_glossary"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    term = Column(String(255), unique=True, nullable=False)
    definition = Column(Text, nullable=False)
    category = Column(String(100))
    synonyms = Column(ARRAY(Text))
    related_terms = Column(ARRAY(Text))
    examples = Column(ARRAY(Text))
    owner = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class BusinessRule(Base):
    """Business rules and policies"""
    __tablename__ = "business_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_type = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    definition = Column(JSONB, nullable=False)
    applies_to = Column(ARRAY(Text))
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class DataLineage(Base):
    """Data lineage tracking"""
    __tablename__ = "data_lineage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_table = Column(String(255), nullable=False)
    source_database = Column(String(255), nullable=False)
    target_table = Column(String(255), nullable=False)
    target_database = Column(String(255), nullable=False)
    relationship_type = Column(String(50))
    transformation_logic = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
```

**Acceptance Criteria**:
- [ ] Models defined with proper types
- [ ] Relationships configured
- [ ] Validators added
- [ ] Can import without errors

---

### Day 3-4: Vector Store Setup

#### Task 1.3: pgvector Extension
**Owner**: Backend Developer  
**Effort**: 2 hours  
**Priority**: Critical

**Actions**:
1. Add pgvector to PostgreSQL
2. Create embeddings table
3. Set up embedding model

**Migration File**: `backend/alembic/versions/004_vector_store.py`

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Embeddings table
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    namespace VARCHAR(100) NOT NULL,  -- 'metrics', 'queries', 'tables', etc.
    object_id VARCHAR(255) NOT NULL,  -- ID of the object
    content TEXT NOT NULL,  -- Original content
    embedding vector(384),  -- 384-dim for all-MiniLM-L6-v2
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(namespace, object_id)
);

-- Indexes for fast similarity search
CREATE INDEX idx_embeddings_vector ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX idx_embeddings_namespace ON embeddings(namespace);
```

**Acceptance Criteria**:
- [ ] pgvector installed
- [ ] Embeddings table created
- [ ] Can insert and query vectors
- [ ] Similarity search works

---

#### Task 1.4: Embedding Service
**Owner**: Backend Developer  
**Effort**: 3 hours  
**Priority**: Critical

**File**: `backend/app/services/embedding.py`

```python
from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.semantic_layer import Embedding

class EmbeddingService:
    """
    Service for generating and managing embeddings
    """
    
    def __init__(self):
        # Use all-MiniLM-L6-v2: fast, good quality, 384 dimensions
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    async def store_embedding(
        self,
        db: Session,
        namespace: str,
        object_id: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Store embedding in database"""
        embedding = self.generate_embedding(content)
        
        # Upsert
        query = text("""
            INSERT INTO embeddings (namespace, object_id, content, embedding, metadata)
            VALUES (:namespace, :object_id, :content, :embedding::vector, :metadata)
            ON CONFLICT (namespace, object_id) 
            DO UPDATE SET 
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata,
                created_at = NOW()
        """)
        
        await db.execute(query, {
            "namespace": namespace,
            "object_id": object_id,
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {}
        })
        await db.commit()
    
    async def similarity_search(
        self,
        db: Session,
        query: str,
        namespace: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Find similar items using cosine similarity
        """
        query_embedding = self.generate_embedding(query)
        
        sql = text("""
            SELECT 
                object_id,
                content,
                metadata,
                1 - (embedding <=> :query_embedding::vector) as similarity
            FROM embeddings
            WHERE namespace = :namespace
                AND 1 - (embedding <=> :query_embedding::vector) > :threshold
            ORDER BY embedding <=> :query_embedding::vector
            LIMIT :top_k
        """)
        
        result = await db.execute(sql, {
            "query_embedding": query_embedding,
            "namespace": namespace,
            "threshold": threshold,
            "top_k": top_k
        })
        
        return [
            {
                "object_id": row.object_id,
                "content": row.content,
                "metadata": row.metadata,
                "similarity": float(row.similarity)
            }
            for row in result
        ]
```

**Acceptance Criteria**:
- [ ] Can generate embeddings
- [ ] Can store embeddings
- [ ] Similarity search works
- [ ] Tests pass

---

### Day 5-7: Context Retrieval System

#### Task 1.5: ContextRetriever Class
**Owner**: Backend Developer  
**Effort**: 8 hours  
**Priority**: Critical

**File**: `backend/app/services/context_retriever.py`

```python
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.services.embedding import EmbeddingService
from app.services.cache import CacheService
from app.models.semantic_layer import Metric, BusinessGlossary, BusinessRule
import logging

logger = logging.getLogger(__name__)

class ContextRetriever:
    """
    Retrieve relevant context for a query using multiple strategies
    """
    
    def __init__(
        self,
        db: Session,
        embedding_service: EmbeddingService,
        cache_service: CacheService
    ):
        self.db = db
        self.embeddings = embedding_service
        self.cache = cache_service
    
    async def retrieve_schema_context(
        self,
        tables: List[str],
        database_id: int
    ) -> Dict:
        """
        Retrieve schema information for specific tables
        """
        cache_key = f"schema:{database_id}:{':'.join(sorted(tables))}"
        
        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"Schema context cache hit for {cache_key}")
            return cached
        
        # Fetch from database
        # (Implementation depends on your schema_manager)
        schema_context = await self._fetch_schema_from_db(database_id, tables)
        
        # Cache for 1 hour
        await self.cache.set(cache_key, schema_context, ttl=3600)
        
        return schema_context
    
    async def retrieve_relevant_metrics(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Find business metrics relevant to the query
        """
        # Semantic search in embeddings
        similar = await self.embeddings.similarity_search(
            self.db,
            query=query,
            namespace="metrics",
            top_k=top_k
        )
        
        # Fetch full metric details
        metric_ids = [s["object_id"] for s in similar]
        metrics = await self.db.query(Metric).filter(
            Metric.id.in_(metric_ids)
        ).all()
        
        return [
            {
                "name": m.name,
                "display_name": m.display_name,
                "description": m.description,
                "sql_definition": m.sql_definition,
                "format": m.format,
                "certified": m.certified,
                "similarity": next(
                    s["similarity"] for s in similar 
                    if s["object_id"] == str(m.id)
                )
            }
            for m in metrics
        ]
    
    async def retrieve_glossary_terms(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find relevant business glossary terms
        """
        similar = await self.embeddings.similarity_search(
            self.db,
            query=query,
            namespace="glossary",
            top_k=top_k
        )
        
        return similar
    
    async def retrieve_similar_queries(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Find similar successful historical queries (RAG)
        """
        similar = await self.embeddings.similarity_search(
            self.db,
            query=query,
            namespace="successful_queries",
            top_k=top_k,
            threshold=0.7  # Only high similarity
        )
        
        return similar
    
    async def retrieve_business_rules(
        self,
        rule_types: List[str]
    ) -> List[Dict]:
        """
        Retrieve specific business rules
        """
        cache_key = f"rules:{':'.join(sorted(rule_types))}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        rules = await self.db.query(BusinessRule).filter(
            BusinessRule.rule_type.in_(rule_types),
            BusinessRule.active == True
        ).all()
        
        result = [
            {
                "rule_type": r.rule_type,
                "name": r.name,
                "definition": r.definition
            }
            for r in rules
        ]
        
        # Cache for 24 hours
        await self.cache.set(cache_key, result, ttl=86400)
        
        return result
    
    async def retrieve_all_context(
        self,
        query: str,
        database_id: int,
        tables: List[str],
        user_permissions: Dict
    ) -> Dict:
        """
        Retrieve all relevant context for a query
        """
        context = {}
        
        # Schema context (critical)
        if tables:
            context["schema"] = await self.retrieve_schema_context(
                tables, database_id
            )
        
        # Business metrics (critical)
        context["metrics"] = await self.retrieve_relevant_metrics(query)
        
        # Glossary terms (medium priority)
        context["glossary"] = await self.retrieve_glossary_terms(query)
        
        # Similar queries (medium priority)
        context["examples"] = await self.retrieve_similar_queries(query)
        
        # Business rules (high priority)
        context["rules"] = await self.retrieve_business_rules([
            "fiscal_calendar",
            "data_retention"
        ])
        
        # User permissions (critical)
        context["permissions"] = user_permissions
        
        return context
```

**Acceptance Criteria**:
- [ ] Can retrieve schema context
- [ ] Can find relevant metrics
- [ ] Can search similar queries
- [ ] Caching works
- [ ] Tests pass (>80% coverage)

---

### Day 8-10: Context Management & Optimization

#### Task 1.6: ContextOptimizer
**Owner**: Backend Developer  
**Effort**: 6 hours  
**Priority**: High

**File**: `backend/app/services/context_optimizer.py`

```python
from typing import List, Dict
import tiktoken

class ContextOptimizer:
    """
    Optimize context to fit within token budget
    """
    
    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def optimize(
        self,
        context_items: List[Dict],
        query_tokens: int,
        reserved_for_response: int = 1000
    ) -> str:
        """
        Select and fit context items within token budget
        
        Priority order:
        1. Schema (critical)
        2. Metrics (critical)
        3. Business rules (high)
        4. Examples (medium)
        5. Glossary (low)
        """
        available_tokens = self.max_tokens - query_tokens - reserved_for_response
        
        # Priority scores
        priority_map = {
            "schema": 100,
            "metric": 90,
            "rule": 70,
            "example": 40,
            "glossary": 20
        }
        
        # Calculate token count and priority for each item
        scored_items = []
        for item in context_items:
            content = self._format_item(item)
            tokens = self.count_tokens(content)
            priority = priority_map.get(item["type"], 10)
            
            # Boost by relevance score
            relevance = item.get("relevance", 0.5)
            score = priority * relevance
            
            scored_items.append({
                "content": content,
                "tokens": tokens,
                "score": score,
                "type": item["type"]
            })
        
        # Sort by score (descending)
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        
        # Greedy selection
        selected = []
        used_tokens = 0
        
        for item in scored_items:
            if used_tokens + item["tokens"] <= available_tokens:
                selected.append(item)
                used_tokens += item["tokens"]
            else:
                # Try to fit summary if available
                if "summary" in item:
                    summary_tokens = self.count_tokens(item["summary"])
                    if used_tokens + summary_tokens <= available_tokens:
                        selected.append({
                            **item,
                            "content": item["summary"]
                        })
                        used_tokens += summary_tokens
        
        # Assemble final context
        return self._assemble_context(selected)
    
    def _format_item(self, item: Dict) -> str:
        """Format context item as string"""
        if item["type"] == "schema":
            return f"Table: {item['table']}\nColumns: {item['columns']}"
        elif item["type"] == "metric":
            return f"Metric: {item['name']}\nDefinition: {item['definition']}\nSQL: {item['sql']}"
        # ... etc
        return str(item.get("content", ""))
    
    def _assemble_context(self, items: List[Dict]) -> str:
        """Assemble selected items into coherent context"""
        sections = []
        
        # Group by type
        by_type = {}
        for item in items:
            by_type.setdefault(item["type"], []).append(item)
        
        # Build sections
        if "schema" in by_type:
            sections.append("## Database Schema")
            sections.extend([i["content"] for i in by_type["schema"]])
        
        if "metric" in by_type:
            sections.append("\n## Business Metrics")
            sections.extend([i["content"] for i in by_type["metric"]])
        
        if "rule" in by_type:
            sections.append("\n## Business Rules")
            sections.extend([i["content"] for i in by_type["rule"]])
        
        if "example" in by_type:
            sections.append("\n## Example Queries")
            sections.extend([i["content"] for i in by_type["example"]])
        
        return "\n\n".join(sections)
```

**Acceptance Criteria**:
- [ ] Fits context within token budget
- [ ] Respects priority ordering
- [ ] Tests pass

---

#### Task 1.7: ContextManager (Orchestrator)
**Owner**: Backend Developer  
**Effort**: 4 hours  
**Priority**: Critical

**File**: `backend/app/services/context_manager.py`

```python
from typing import Dict, List
from app.services.context_retriever import ContextRetriever
from app.services.context_optimizer import ContextOptimizer
from app.services.cache import CacheService
import logging

logger = logging.getLogger(__name__)

class ContextManager:
    """
    Orchestrate context retrieval, optimization, and delivery
    """
    
    def __init__(
        self,
        retriever: ContextRetriever,
        optimizer: ContextOptimizer,
        cache: CacheService
    ):
        self.retriever = retriever
        self.optimizer = optimizer
        self.cache = cache
    
    async def get_context_for_query(
        self,
        query: str,
        database_id: int,
        tables: List[str],
        user_permissions: Dict,
        max_tokens: int = 8000
    ) -> str:
        """
        Get optimized context for a query
        """
        # Generate cache key
        cache_key = self._generate_cache_key(query, database_id, tables)
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"Context cache hit for query")
            return cached
        
        # Retrieve all relevant context
        context_dict = await self.retriever.retrieve_all_context(
            query=query,
            database_id=database_id,
            tables=tables,
            user_permissions=user_permissions
        )
        
        # Convert to list of items
        context_items = self._flatten_context(context_dict)
        
        # Count query tokens
        query_tokens = self.optimizer.count_tokens(query)
        
        # Optimize to fit budget
        optimized_context = self.optimizer.optimize(
            context_items=context_items,
            query_tokens=query_tokens,
            reserved_for_response=1000
        )
        
        # Cache for 1 hour
        await self.cache.set(cache_key, optimized_context, ttl=3600)
        
        logger.info(
            f"Context assembled: {self.optimizer.count_tokens(optimized_context)} tokens"
        )
        
        return optimized_context
    
    def _flatten_context(self, context_dict: Dict) -> List[Dict]:
        """Convert nested context dict to flat list of items"""
        items = []
        
        # Schema items
        if "schema" in context_dict:
            for table, info in context_dict["schema"].items():
                items.append({
                    "type": "schema",
                    "table": table,
                    "columns": info,
                    "relevance": 1.0  # Always relevant
                })
        
        # Metric items
        for metric in context_dict.get("metrics", []):
            items.append({
                "type": "metric",
                **metric,
                "relevance": metric.get("similarity", 0.8)
            })
        
        # ... etc for other types
        
        return items
    
    def _generate_cache_key(
        self,
        query: str,
        database_id: int,
        tables: List[str]
    ) -> str:
        """Generate cache key for context"""
        import hashlib
        key_str = f"{query}:{database_id}:{':'.join(sorted(tables))}"
        return f"context:{hashlib.md5(key_str.encode()).hexdigest()}"
```

**Acceptance Criteria**:
- [ ] Orchestrates retrieval and optimization
- [ ] Caching works
- [ ] Logging in place
- [ ] Tests pass

---

### Day 11-12: Testing & Documentation

#### Task 1.8: Comprehensive Tests
**Owner**: Backend Developer  
**Effort**: 6 hours  
**Priority**: High

**File**: `backend/app/tests/test_context_system.py`

```python
import pytest
from app.services.context_retriever import ContextRetriever
from app.services.context_optimizer import ContextOptimizer
from app.services.context_manager import ContextManager

class TestContextRetriever:
    """Test context retrieval"""
    
    async def test_retrieve_relevant_metrics(self, db_session):
        """Test metric retrieval"""
        retriever = ContextRetriever(db_session, ...)
        
        metrics = await retriever.retrieve_relevant_metrics(
            query="What is our revenue?",
            top_k=3
        )
        
        assert len(metrics) > 0
        assert "revenue" in [m["name"] for m in metrics]
    
    async def test_similarity_search(self, db_session):
        """Test semantic search"""
        # ... test implementation
    
    async def test_caching(self, db_session, cache):
        """Test context caching"""
        # ... test implementation

class TestContextOptimizer:
    """Test context optimization"""
    
    def test_token_counting(self):
        """Test token counting"""
        optimizer = ContextOptimizer(max_tokens=8000)
        
        text = "This is a test."
        tokens = optimizer.count_tokens(text)
        
        assert tokens > 0
        assert tokens < 10
    
    def test_context_fitting(self):
        """Test fitting context in budget"""
        optimizer = ContextOptimizer(max_tokens=100)
        
        items = [
            {"type": "schema", "content": "x" * 50, "relevance": 1.0},
            {"type": "metric", "content": "y" * 50, "relevance": 0.9},
            {"type": "example", "content": "z" * 50, "relevance": 0.5}
        ]
        
        result = optimizer.optimize(items, query_tokens=10)
        
        # Should fit high-priority items first
        assert "xxx" in result  # schema
        assert "yyy" in result or "zzz" not in result  # metric or not example

# Add more tests...
```

**Acceptance Criteria**:
- [ ] >80% test coverage
- [ ] All tests green
- [ ] Edge cases covered
- [ ] Performance tests included

---

#### Task 1.9: Documentation
**Owner**: Backend Developer  
**Effort**: 3 hours  
**Priority**: Medium

**Files to Create/Update**:
- `backend/docs/context_system.md`
- Code docstrings
- API documentation

**Acceptance Criteria**:
- [ ] Architecture documented
- [ ] API endpoints documented
- [ ] Usage examples provided
- [ ] Troubleshooting guide

---

## 📊 Sprint Metrics

**Track Daily**:
- [ ] Tasks completed
- [ ] Tests passing
- [ ] Test coverage %
- [ ] Blockers

**Track at Sprint End**:
- [ ] Context retrieval latency (target: <100ms P95)
- [ ] Cache hit rate (target: >60%)
- [ ] Context quality score (target: >85%)
- [ ] Test coverage (target: >80%)

---

## 🚧 Potential Blockers

1. **pgvector installation**
   - Mitigation: Have Docker setup ready
   - Fallback: Use Pinecone if local issues

2. **Embedding model download**
   - Mitigation: Pre-download model
   - Size: ~80MB for all-MiniLM-L6-v2

3. **Token counting accuracy**
   - Mitigation: Use tiktoken library
   - Test with sample prompts

---

## 🎯 Definition of Done

Sprint 1 is complete when:

- [x] All database migrations run successfully
- [x] Context retrieval system operational
- [x] Multi-level caching implemented
- [x] Token optimizer working
- [x] Tests passing with >80% coverage
- [x] Documentation complete
- [x] Demo-able to stakeholders

---

## 📅 Daily Standup Template

**Yesterday**:
- What did I complete?
- Any blockers?

**Today**:
- What will I work on?
- What support do I need?

**Blockers**:
- Any impediments?

---

## 🚀 Sprint Kickoff

**Date**: [Today]  
**Duration**: 2 weeks  
**Team**: 1-2 developers  
**Goal**: Context engineering foundation operational

Let's build! 💪












