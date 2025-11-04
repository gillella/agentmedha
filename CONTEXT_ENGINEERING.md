# Context Engineering Architecture
## Building Intelligent, Context-Aware AI Agents

> **"The quality of AI responses is directly proportional to the quality of context provided."**

---

## 🎯 What is Context Engineering?

**Context Engineering** is the systematic practice of:
1. **Capturing** relevant information from multiple sources
2. **Organizing** it in a structured, retrievable format
3. **Selecting** the most relevant pieces for each query
4. **Delivering** it to LLMs within token constraints
5. **Validating** that context is complete and accurate

This is CRITICAL for enterprise AI because generic LLMs don't know:
- Your database schema
- Your business rules
- Your metric definitions
- Your data access permissions
- Your organizational context

---

## 🏗️ Context Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                   QUERY LAYER                           │
│  User Question + Intent + Entities + Clarifications     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              CONTEXT ORCHESTRATOR                       │
│  Decides what context to retrieve and in what order     │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│  SYSTEM    │  │  SESSION   │  │   USER     │
│  CONTEXT   │  │  CONTEXT   │  │  CONTEXT   │
│            │  │            │  │            │
│ • Schema   │  │ • History  │  │ • Role     │
│ • Metrics  │  │ • State    │  │ • Prefs    │
│ • Rules    │  │ • Results  │  │ • Access   │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │               │               │
      └───────────────┼───────────────┘
                      │
         ┌────────────▼────────────┐
         │                         │
         ▼                         ▼
┌────────────────┐        ┌────────────────┐
│ VECTOR STORE   │        │  KNOWLEDGE     │
│                │        │    GRAPH       │
│ • Embeddings   │        │                │
│ • Semantic     │        │ • Relations    │
│   Search       │        │ • Lineage      │
└────────────────┘        └────────────────┘
```

---

## 1. System Context (Static/Slowly Changing)

### 1.1 Database Schema Context

**What**: Complete database structure information

**Contents**:
```python
{
    "databases": {
        "sales_db": {
            "type": "postgresql",
            "version": "15.2",
            "tables": {
                "customers": {
                    "columns": {
                        "customer_id": {
                            "type": "integer",
                            "primary_key": true,
                            "description": "Unique customer identifier"
                        },
                        "email": {
                            "type": "varchar(255)",
                            "unique": true,
                            "nullable": false,
                            "pii": true,  # Important for access control
                            "description": "Customer email address"
                        },
                        "created_at": {
                            "type": "timestamp",
                            "default": "CURRENT_TIMESTAMP",
                            "description": "Account creation date"
                        }
                    },
                    "relationships": {
                        "orders": {
                            "type": "one-to-many",
                            "foreign_key": "customer_id",
                            "description": "Customer orders"
                        }
                    },
                    "indexes": [
                        {"columns": ["email"], "type": "btree"},
                        {"columns": ["created_at"], "type": "btree"}
                    ],
                    "row_count": 45000,
                    "last_updated": "2024-11-03T10:30:00Z",
                    "data_owner": "Sales Team",
                    "sensitivity": "medium"
                }
            }
        }
    }
}
```

**Storage**: PostgreSQL metadata tables + Redis cache

**Refresh**: 
- Full refresh: Daily
- Incremental: Every 15 minutes
- On-demand: Schema changes trigger immediate refresh

### 1.2 Semantic Layer (Business Context)

**What**: Business definitions and rules

**Contents**:
```python
{
    "metrics": {
        "revenue": {
            "display_name": "Revenue",
            "description": "Total revenue from completed orders",
            "sql_definition": """
                SELECT SUM(o.total_amount)
                FROM orders o
                WHERE o.status = 'completed'
                  AND o.payment_status = 'paid'
            """,
            "data_sources": ["orders"],
            "dependencies": ["orders.total_amount", "orders.status"],
            "filters": {
                "default": "o.created_at >= CURRENT_DATE - INTERVAL '90 days'",
                "always_apply": "o.status = 'completed'"
            },
            "aggregation": "sum",
            "format": "currency",
            "currency": "USD",
            "owner": "CFO",
            "certified": true,
            "certification_date": "2024-10-01",
            "tags": ["financial", "kpi"],
            "business_rules": [
                "Excludes refunded orders",
                "Includes tax and shipping",
                "Recorded at order completion time"
            ],
            "related_metrics": ["arr", "mrr", "gross_profit"],
            "typical_questions": [
                "What is our total revenue?",
                "Show me revenue by product",
                "How much revenue did we make last quarter?"
            ]
        },
        "arr": {
            "display_name": "Annual Recurring Revenue",
            "description": "Annualized value of active subscriptions",
            "sql_definition": """
                SELECT SUM(s.monthly_amount * 12)
                FROM subscriptions s
                WHERE s.status = 'active'
            """,
            # ... similar structure
        }
    },
    
    "dimensions": {
        "region": {
            "display_name": "Geographic Region",
            "description": "Sales region classification",
            "table": "customers",
            "column": "region",
            "type": "categorical",
            "values": ["North America", "EMEA", "APAC", "LATAM"],
            "hierarchy": ["region", "country", "state", "city"]
        }
    },
    
    "business_rules": {
        "fiscal_calendar": {
            "fiscal_year_start": "2024-11-01",
            "fiscal_quarters": {
                "Q1": {"start": "2024-11-01", "end": "2025-01-31"},
                "Q2": {"start": "2025-02-01", "end": "2025-04-30"},
                "Q3": {"start": "2025-05-01", "end": "2025-07-31"},
                "Q4": {"start": "2025-08-01", "end": "2025-10-31"}
            }
        },
        "data_retention": {
            "orders": "7 years",
            "logs": "90 days",
            "analytics": "2 years"
        }
    },
    
    "glossary": {
        "churn": {
            "definition": "Customer who cancelled subscription",
            "calculation": "Cancelled subscriptions / Total subscriptions",
            "period": "monthly",
            "owner": "Customer Success"
        }
    }
}
```

**Storage**: Dedicated PostgreSQL schema (`semantic_layer`) + Vector embeddings

**Refresh**: 
- User-driven updates via admin UI
- Version controlled
- Approval workflow for certified metrics

### 1.3 Data Lineage & Relationships

**What**: How data flows through systems

```python
{
    "lineage": {
        "customers": {
            "upstream": [],  # Source system
            "downstream": [
                {
                    "table": "orders",
                    "relationship": "one-to-many",
                    "joins": ["customer_id"]
                },
                {
                    "table": "customer_segments",
                    "relationship": "one-to-one",
                    "type": "derived",
                    "transformation": "ML segmentation model"
                }
            ],
            "transformations": [
                {
                    "type": "ETL",
                    "source": "CRM (Salesforce)",
                    "schedule": "every 6 hours",
                    "last_run": "2024-11-03T10:00:00Z"
                }
            ]
        }
    }
}
```

**Storage**: Graph database (Neo4j) or PostgreSQL with recursive queries

---

## 2. Session Context (Conversation-Scoped)

### 2.1 Conversation History

**What**: Previous interactions in this session

```python
{
    "session_id": "sess_abc123",
    "user_id": 42,
    "started_at": "2024-11-03T10:00:00Z",
    "conversation": [
        {
            "turn": 1,
            "timestamp": "2024-11-03T10:00:05Z",
            "user_message": "What were total sales last quarter?",
            "intent": "aggregate_query",
            "entities": {
                "metric": "sales",
                "time_period": "last quarter"
            },
            "selected_datasource": "sales_db",
            "sql_generated": "SELECT SUM(total_amount) FROM orders...",
            "result_summary": "$1.2M in Q3 2024",
            "visualization": "single_metric_card"
        },
        {
            "turn": 2,
            "timestamp": "2024-11-03T10:01:23Z",
            "user_message": "How does that compare to the previous quarter?",
            "intent": "comparison",
            "context_carried_forward": {
                "metric": "sales",
                "original_time_period": "Q3 2024",
                "comparison_period": "Q2 2024"
            },
            "sql_generated": "SELECT SUM(...) FROM orders WHERE quarter = 'Q2 2024'",
            "result_summary": "Q3 was 15% higher than Q2 ($1.04M)"
        }
    ],
    "context_state": {
        "active_datasource": "sales_db",
        "active_metrics": ["sales"],
        "active_dimensions": ["time"],
        "applied_filters": ["fiscal_year = 2024"]
    }
}
```

**Storage**: Redis (fast access, TTL: 30 minutes)

**Purpose**: 
- Handle follow-up questions
- Maintain conversation coherence
- Avoid re-asking for clarifications

### 2.2 Intermediate Results

**What**: Results from previous queries in this session

```python
{
    "cached_results": {
        "query_hash_abc123": {
            "sql": "SELECT ...",
            "results": [...],  # Actual data
            "metadata": {
                "row_count": 150,
                "execution_time_ms": 234,
                "cached_at": "2024-11-03T10:00:05Z"
            }
        }
    }
}
```

**Storage**: Redis (TTL: 1 hour)

**Purpose**: 
- Avoid re-executing same query
- Enable drill-downs without re-querying

---

## 3. User Context (User-Specific)

### 3.1 User Profile & Permissions

```python
{
    "user_id": 42,
    "role": "analyst",
    "department": "sales",
    "permissions": {
        "data_sources": {
            "sales_db": {
                "access": "read",
                "tables": {
                    "customers": {
                        "access": "full",
                        "row_filter": null
                    },
                    "orders": {
                        "access": "full",
                        "row_filter": null
                    },
                    "employee_salaries": {
                        "access": "denied"
                    }
                }
            },
            "hr_db": {
                "access": "denied"
            }
        },
        "features": {
            "export_data": true,
            "create_dashboards": true,
            "schedule_reports": false,  # Only admins
            "manage_datasources": false
        }
    },
    "preferences": {
        "theme": "dark",
        "default_date_range": "last_90_days",
        "favorite_datasources": ["sales_db"],
        "notification_preferences": {
            "email": true,
            "slack": true
        }
    },
    "usage_stats": {
        "total_queries": 847,
        "avg_queries_per_day": 12,
        "favorite_metrics": ["revenue", "conversion_rate"],
        "common_questions": [
            "What is revenue by region?",
            "Show top products"
        ]
    }
}
```

**Storage**: PostgreSQL (users table) + Redis cache

### 3.2 User's Query Patterns (Personalization)

```python
{
    "query_history": {
        "frequent_patterns": [
            {
                "pattern": "revenue by {dimension}",
                "count": 45,
                "dimensions_used": ["region", "product", "customer_segment"]
            }
        ],
        "favorite_queries": [
            {
                "id": "q_123",
                "description": "Weekly sales dashboard",
                "query": "...",
                "runs_per_week": 5
            }
        ]
    }
}
```

**Storage**: Vector store (for similarity search)

---

## 4. Query Context (Request-Specific)

### 4.1 Intent Analysis

```python
{
    "user_question": "What were our top 10 products by revenue last quarter compared to the previous quarter?",
    "parsed_intent": {
        "primary_intent": "ranking",
        "secondary_intent": "comparison",
        "analysis_type": "trend_analysis",
        "entities": {
            "metric": {
                "name": "revenue",
                "semantic_mapping": "metrics.revenue",
                "confidence": 0.95
            },
            "dimension": {
                "name": "products",
                "table": "products",
                "confidence": 0.92
            },
            "time_period_1": {
                "description": "last quarter",
                "resolved": "Q3 2024",
                "start_date": "2024-07-01",
                "end_date": "2024-09-30"
            },
            "time_period_2": {
                "description": "previous quarter",
                "resolved": "Q2 2024",
                "start_date": "2024-04-01",
                "end_date": "2024-06-30"
            },
            "limit": 10,
            "sort": "desc"
        },
        "ambiguities": [],  # None detected
        "clarifications_needed": []
    }
}
```

### 4.2 Context Retrieval Plan

```python
{
    "retrieval_plan": {
        "required_context": [
            {
                "type": "schema",
                "tables": ["products", "orders", "order_items"],
                "priority": "critical",
                "estimated_tokens": 500
            },
            {
                "type": "metric_definition",
                "metrics": ["revenue"],
                "priority": "critical",
                "estimated_tokens": 150
            },
            {
                "type": "business_rule",
                "rules": ["fiscal_calendar"],
                "priority": "high",
                "estimated_tokens": 100
            },
            {
                "type": "similar_queries",
                "top_k": 3,
                "priority": "medium",
                "estimated_tokens": 400
            },
            {
                "type": "conversation_history",
                "previous_turns": 2,
                "priority": "low",
                "estimated_tokens": 300
            }
        ],
        "total_estimated_tokens": 1450,
        "token_budget": 8000,
        "remaining_budget": 6550
    }
}
```

---

## 5. Context Retrieval Strategies

### 5.1 Semantic Search (RAG++)

```python
class ContextRetriever:
    """
    Retrieve most relevant context using semantic search
    """
    
    def __init__(self, vector_store, embedding_model):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
    
    async def retrieve_similar_queries(
        self, 
        question: str, 
        top_k: int = 3
    ) -> List[Dict]:
        """
        Find similar successful queries
        """
        # Create embedding
        question_embedding = self.embedding_model.encode(question)
        
        # Search vector store
        results = await self.vector_store.similarity_search(
            embedding=question_embedding,
            namespace="successful_queries",
            top_k=top_k,
            filter={
                "success": True,
                "user_rating": {"$gte": 4}
            }
        )
        
        return [
            {
                "question": r.metadata["question"],
                "sql": r.metadata["sql"],
                "explanation": r.metadata["explanation"],
                "similarity_score": r.score
            }
            for r in results
        ]
    
    async def retrieve_relevant_tables(
        self,
        question: str,
        top_k: int = 5
    ) -> List[str]:
        """
        Find tables relevant to question
        """
        question_embedding = self.embedding_model.encode(question)
        
        results = await self.vector_store.similarity_search(
            embedding=question_embedding,
            namespace="table_descriptions",
            top_k=top_k
        )
        
        return [r.metadata["table_name"] for r in results]
    
    async def retrieve_relevant_metrics(
        self,
        question: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Find business metrics relevant to question
        """
        question_embedding = self.embedding_model.encode(question)
        
        results = await self.vector_store.similarity_search(
            embedding=question_embedding,
            namespace="metrics",
            top_k=top_k
        )
        
        return [
            {
                "name": r.metadata["metric_name"],
                "definition": r.metadata["definition"],
                "sql": r.metadata["sql_definition"]
            }
            for r in results
        ]
```

### 5.2 Hybrid Search (Keyword + Semantic)

```python
class HybridRetriever:
    """
    Combine keyword matching with semantic search
    """
    
    def __init__(self, vector_store, keyword_index):
        self.vector_store = vector_store
        self.keyword_index = keyword_index  # Elasticsearch
    
    async def hybrid_search(
        self,
        question: str,
        top_k: int = 5,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict]:
        """
        Combine semantic and keyword search results
        """
        # Semantic search
        semantic_results = await self.vector_store.similarity_search(
            question, top_k=top_k * 2
        )
        
        # Keyword search
        keyword_results = await self.keyword_index.search(
            question, top_k=top_k * 2
        )
        
        # Merge and re-rank
        merged = self._merge_and_rerank(
            semantic_results,
            keyword_results,
            semantic_weight,
            keyword_weight
        )
        
        return merged[:top_k]
    
    def _merge_and_rerank(self, semantic, keyword, w1, w2):
        """Reciprocal rank fusion"""
        scores = {}
        
        for rank, result in enumerate(semantic):
            doc_id = result.id
            scores[doc_id] = scores.get(doc_id, 0) + w1 / (rank + 1)
        
        for rank, result in enumerate(keyword):
            doc_id = result.id
            scores[doc_id] = scores.get(doc_id, 0) + w2 / (rank + 1)
        
        # Sort by score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked
```

### 5.3 Graph-Based Retrieval

```python
class GraphRetriever:
    """
    Use knowledge graph to find related context
    """
    
    def __init__(self, graph_db):
        self.graph = graph_db
    
    async def get_related_entities(
        self,
        entity: str,
        max_depth: int = 2
    ) -> Dict:
        """
        Find entities related to given entity
        """
        query = """
        MATCH (e:Entity {name: $entity})-[r*1..{depth}]-(related)
        RETURN related, type(r), distance(e, related)
        ORDER BY distance
        LIMIT 20
        """.format(depth=max_depth)
        
        results = await self.graph.query(query, {"entity": entity})
        
        return {
            "entity": entity,
            "related": [
                {
                    "name": r["related"]["name"],
                    "type": r["related"]["type"],
                    "relationship": r["type"],
                    "distance": r["distance"]
                }
                for r in results
            ]
        }
    
    async def get_data_lineage(
        self,
        table: str,
        direction: str = "both"  # upstream, downstream, both
    ) -> Dict:
        """
        Get data lineage for table
        """
        if direction == "upstream":
            query = """
            MATCH path = (t:Table {name: $table})<-[:DEPENDS_ON*]-(source)
            RETURN path
            """
        elif direction == "downstream":
            query = """
            MATCH path = (t:Table {name: $table})-[:DEPENDS_ON*]->(target)
            RETURN path
            """
        else:
            query = """
            MATCH path = (t:Table {name: $table})-[:DEPENDS_ON*]-(related)
            RETURN path
            """
        
        results = await self.graph.query(query, {"table": table})
        return self._format_lineage(results)
```

---

## 6. Context Assembly & Optimization

### 6.1 Token Budget Management

```python
class ContextOptimizer:
    """
    Fit maximum relevant context within token budget
    """
    
    def __init__(self, tokenizer, max_tokens: int = 8000):
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens
    
    def optimize(
        self,
        context_items: List[Dict],
        query_tokens: int
    ) -> str:
        """
        Select and fit context items within budget
        """
        available_tokens = self.max_tokens - query_tokens - 1000  # Reserve for response
        
        # Sort by priority
        sorted_items = sorted(
            context_items,
            key=lambda x: self._priority_score(x),
            reverse=True
        )
        
        # Greedy selection within budget
        selected = []
        used_tokens = 0
        
        for item in sorted_items:
            item_tokens = len(self.tokenizer.encode(item["content"]))
            
            if used_tokens + item_tokens <= available_tokens:
                selected.append(item)
                used_tokens += item_tokens
            else:
                # Try to fit summary instead of full content
                if "summary" in item:
                    summary_tokens = len(self.tokenizer.encode(item["summary"]))
                    if used_tokens + summary_tokens <= available_tokens:
                        selected.append({"content": item["summary"], **item})
                        used_tokens += summary_tokens
        
        # Assemble final context
        return self._assemble_context(selected)
    
    def _priority_score(self, item: Dict) -> float:
        """Calculate priority score for context item"""
        base_score = {
            "critical": 100,
            "high": 70,
            "medium": 40,
            "low": 10
        }[item.get("priority", "low")]
        
        # Boost by relevance
        relevance = item.get("relevance_score", 0.5)
        
        # Penalize by size (prefer smaller items)
        size_penalty = len(item["content"]) / 1000
        
        return base_score * relevance - size_penalty
    
    def _assemble_context(self, items: List[Dict]) -> str:
        """Assemble selected items into coherent context"""
        sections = []
        
        # Group by type
        by_type = {}
        for item in items:
            type_ = item.get("type", "other")
            by_type.setdefault(type_, []).append(item)
        
        # Schema section
        if "schema" in by_type:
            sections.append("## Database Schema\n")
            for item in by_type["schema"]:
                sections.append(item["content"])
        
        # Metrics section
        if "metric" in by_type:
            sections.append("\n## Business Metrics\n")
            for item in by_type["metric"]:
                sections.append(item["content"])
        
        # Examples section
        if "example" in by_type:
            sections.append("\n## Example Queries\n")
            for item in by_type["example"]:
                sections.append(item["content"])
        
        # Conversation history
        if "history" in by_type:
            sections.append("\n## Conversation History\n")
            for item in by_type["history"]:
                sections.append(item["content"])
        
        return "\n".join(sections)
```

### 6.2 Context Validation

```python
class ContextValidator:
    """
    Ensure context is complete and consistent
    """
    
    def validate(self, context: Dict, query: Dict) -> Tuple[bool, List[str]]:
        """
        Validate that context is sufficient for query
        """
        errors = []
        
        # Check required tables exist in schema
        required_tables = query.get("required_tables", [])
        schema_tables = context.get("schema", {}).get("tables", {})
        
        missing_tables = set(required_tables) - set(schema_tables.keys())
        if missing_tables:
            errors.append(f"Missing schema for tables: {missing_tables}")
        
        # Check metric definitions exist
        required_metrics = query.get("metrics", [])
        available_metrics = context.get("metrics", {})
        
        missing_metrics = set(required_metrics) - set(available_metrics.keys())
        if missing_metrics:
            errors.append(f"Missing metric definitions: {missing_metrics}")
        
        # Check user has access to required tables
        user_access = context.get("user_permissions", {})
        for table in required_tables:
            if not self._has_table_access(user_access, table):
                errors.append(f"User lacks access to table: {table}")
        
        # Check for ambiguous entities
        entities = query.get("entities", {})
        for entity_name, entity_info in entities.items():
            if entity_info.get("confidence", 1.0) < 0.7:
                errors.append(f"Ambiguous entity: {entity_name}")
        
        return len(errors) == 0, errors
    
    def _has_table_access(self, permissions: Dict, table: str) -> bool:
        """Check if user can access table"""
        # Implementation depends on your RBAC model
        return True  # Simplified
```

---

## 7. Context Caching Strategy

```python
class ContextCache:
    """
    Multi-level caching for context
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.local_cache = {}  # In-memory L1 cache
    
    async def get_schema(self, database: str, table: str) -> Optional[Dict]:
        """
        Get schema with multi-level cache
        """
        cache_key = f"schema:{database}:{table}"
        
        # L1: In-memory cache (fastest)
        if cache_key in self.local_cache:
            return self.local_cache[cache_key]
        
        # L2: Redis cache (fast)
        cached = await self.redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            self.local_cache[cache_key] = data  # Populate L1
            return data
        
        # L3: Database (slow)
        data = await self._fetch_schema_from_db(database, table)
        
        # Populate caches
        await self.redis.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(data)
        )
        self.local_cache[cache_key] = data
        
        return data
    
    async def invalidate(self, pattern: str):
        """
        Invalidate cache entries matching pattern
        """
        # Clear local cache
        self.local_cache = {
            k: v for k, v in self.local_cache.items()
            if not fnmatch.fnmatch(k, pattern)
        }
        
        # Clear Redis cache
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

---

## 8. Implementation Checklist

### Phase 1: Foundation
- [ ] Design context database schema
- [ ] Implement ContextRetriever with semantic search
- [ ] Build ContextOptimizer for token management
- [ ] Create ContextValidator
- [ ] Set up multi-level caching

### Phase 2: Semantic Layer
- [ ] Build metrics repository
- [ ] Create business glossary UI
- [ ] Implement graph-based lineage
- [ ] Add metric certification workflow

### Phase 3: Intelligence
- [ ] Implement hybrid search (semantic + keyword)
- [ ] Add personalization (user query patterns)
- [ ] Build context enrichment pipeline
- [ ] Create context quality metrics

### Phase 4: Optimization
- [ ] Profile context retrieval performance
- [ ] Optimize token usage
- [ ] Implement smart caching
- [ ] Add monitoring & alerts

---

## 🎯 Success Metrics

**Context Quality**:
- Query success rate: >95%
- Context completeness score: >90%
- Ambiguity resolution rate: >85%

**Performance**:
- Context retrieval time: <100ms (P95)
- Cache hit rate: >70%
- Token usage efficiency: >80%

**User Experience**:
- Queries requiring clarification: <10%
- User satisfaction with answers: >4.5/5

---

This context engineering architecture is the **secret sauce** that makes AgentMedha enterprise-grade. Without it, we're just throwing random context at an LLM and hoping for the best. With it, we're delivering consistently accurate, business-aware responses. 🚀












