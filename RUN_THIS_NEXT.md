# ⚡ RUN THIS NEXT - Sprint 1 Setup Guide

**Goal**: Get Sprint 1 context engineering system operational in 15 minutes

---

## 📋 Prerequisites Checklist

Before starting, ensure:
- [ ] Docker and Docker Compose installed
- [ ] At least 4GB RAM available
- [ ] Terminal access
- [ ] You're in the project root directory

---

## 🚀 Step-by-Step Setup (15 minutes)

### Step 1: Navigate to Project (30 seconds)

```bash
cd /Users/aravindgillella/dev/active/12FactorAgents/agentmedha
```

### Step 2: Start Docker Environment (2 minutes)

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy
docker-compose ps

# Expected output:
# postgres    running    healthy
# redis       running    healthy
# backend     running    healthy
# frontend    running    healthy
```

**Troubleshooting**:
```bash
# If services fail to start
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

### Step 3: Install New Dependencies (3 minutes)

```bash
# Option A: Rebuild backend container (recommended)
docker-compose build backend
docker-compose up -d backend

# Option B: Install inside running container
docker-compose exec backend poetry add tiktoken pgvector

# Verify installation
docker-compose exec backend python -c "import tiktoken; import pgvector; print('✅ Dependencies installed')"
```

---

### Step 4: Run Database Migrations (2 minutes)

```bash
# Run all migrations
docker-compose exec backend alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade ... -> 003_semantic_layer
# INFO  [alembic.runtime.migration] Running upgrade ... -> 004_vector_store
```

**Verify migrations**:
```bash
# Check tables created
docker-compose exec postgres psql -U postgres -d agentmedha -c "\dt"

# Should see:
#  metrics
#  business_glossary
#  business_rules
#  data_lineage
#  embeddings
```

**Verify pgvector extension**:
```bash
docker-compose exec postgres psql -U postgres -d agentmedha -c "SELECT * FROM pg_extension WHERE extname='vector';"

# Should show:
#  vector | 0.5.1 | ...
```

---

### Step 5: Seed Sample Data (2 minutes)

```bash
# Run seed script
docker-compose exec backend python -m app.scripts.seed_semantic_layer

# Expected output:
# Seeding metrics...
# Created metric: revenue
# Created metric: arr
# Created metric: mrr
# Created metric: customer_count
# Created metric: churn_rate
# Creating 5 embeddings...
# ✅ Seeded 5 metrics
#
# Seeding glossary...
# Created glossary term: ARR
# Created glossary term: MRR
# Created glossary term: churn
# ...
# ✅ Seeded 6 glossary terms
#
# Seeding business rules...
# Created rule: Fiscal Year Definition
# ...
# ✅ Seeded 3 business rules
#
# ✅ SEMANTIC LAYER SEEDED SUCCESSFULLY!
```

**Verify seed data**:
```bash
# Check metrics
docker-compose exec postgres psql -U postgres -d agentmedha -c "SELECT name, display_name FROM metrics;"

# Check glossary
docker-compose exec postgres psql -U postgres -d agentmedha -c "SELECT term FROM business_glossary;"

# Check embeddings
docker-compose exec postgres psql -U postgres -d agentmedha -c "SELECT namespace, COUNT(*) FROM embeddings GROUP BY namespace;"
```

---

### Step 6: Run Tests (3 minutes)

```bash
# Run all context system tests
docker-compose exec backend pytest app/tests/test_context_system.py -v

# Expected output:
# test_context_system.py::TestEmbeddingService::test_generate_embedding PASSED
# test_context_system.py::TestEmbeddingService::test_generate_embedding_empty_text PASSED
# test_context_system.py::TestEmbeddingService::test_generate_embeddings_batch PASSED
# ...
# ==================== 22 passed in 5.23s ====================
```

**Run specific tests**:
```bash
# Just embedding tests
docker-compose exec backend pytest app/tests/test_context_system.py::TestEmbeddingService -v

# With coverage
docker-compose exec backend pytest app/tests/test_context_system.py --cov=app.services --cov-report=term-missing
```

---

### Step 7: Test Context System Manually (3 minutes)

```bash
# Enter Python shell
docker-compose exec backend python

# Then run:
```

```python
import asyncio
from app.services.embedding import EmbeddingService
from app.services.context_manager import get_context_manager
from app.core.database import SessionLocal
from app.services.cache import cache

# Initialize
db = SessionLocal()
await cache.connect()

# Test 1: Generate embedding
service = EmbeddingService()
embedding = service.generate_embedding("What is our total revenue?")
print(f"✅ Embedding generated: {len(embedding)} dimensions")

# Test 2: Search for similar metrics
results = await service.similarity_search(
    db=db,
    query="What is our revenue?",
    namespace="metrics",
    top_k=3,
    threshold=0.3
)
print(f"✅ Found {len(results)} similar metrics")
for r in results:
    print(f"  - {r['object_id']}: {r['similarity']:.2f}")

# Test 3: Get full context
context_mgr = get_context_manager(db, cache)
result = await context_mgr.get_context_for_query(
    query="What was our revenue last quarter?",
    database_id=1,
    tables=["orders"],
    user_permissions={"role": "analyst"},
    max_tokens=8000,
    use_cache=False
)

print(f"\n✅ Context retrieved:")
print(f"  - Context tokens: {result['stats']['context_tokens']}")
print(f"  - Items included: {result['metadata']['items_included']}")
print(f"  - Metrics found: {result['metadata']['metrics_count']}")
print(f"  - Cache hit: {result['stats']['cache_hit']}")

# Preview context
print(f"\n📄 Context preview (first 500 chars):")
print(result['context'][:500])

# Exit
exit()
```

**Expected output**:
```
✅ Embedding generated: 384 dimensions
✅ Found 3 similar metrics
  - revenue_001: 0.85
  - arr_002: 0.72
  - mrr_003: 0.68

✅ Context retrieved:
  - Context tokens: 2345
  - Items included: 7
  - Metrics found: 3
  - Cache hit: False

📄 Context preview (first 500 chars):
## User Permissions
{"role": "analyst"}

## Business Metrics
Metric: Total Revenue
Definition: Total revenue from completed orders
SQL: SUM(orders.total_amount)
Status: ✓ Certified
Filters: {'status': 'completed', 'paid': True}

Metric: Annual Recurring Revenue
Definition: Annualized recurring revenue from active subscriptions
...
```

---

## ✅ Verification Checklist

After completing all steps, verify:

### Database
- [ ] Migrations ran successfully
- [ ] 5 new tables created (metrics, business_glossary, business_rules, data_lineage, embeddings)
- [ ] pgvector extension installed
- [ ] Sample data loaded (5 metrics, 6 glossary terms, 3 rules)
- [ ] Embeddings created (11 total: 5 metrics + 6 glossary)

### Services
- [ ] EmbeddingService works (generate + search)
- [ ] ContextRetriever works (finds relevant metrics)
- [ ] ContextOptimizer works (token counting)
- [ ] ContextManager works (end-to-end context retrieval)
- [ ] Cache service working (Redis connected)

### Tests
- [ ] All 22 tests passing
- [ ] No linting errors
- [ ] Manual tests work

---

## 🐛 Troubleshooting

### Issue: "Module not found: tiktoken"

**Solution**:
```bash
docker-compose exec backend poetry add tiktoken
# Or rebuild
docker-compose build backend
docker-compose up -d backend
```

### Issue: "pgvector extension not found"

**Solution**:
```bash
# Install pgvector in PostgreSQL
docker-compose exec postgres bash
apt-get update
apt-get install -y postgresql-15-pgvector
exit

# Restart PostgreSQL
docker-compose restart postgres

# Try migration again
docker-compose exec backend alembic upgrade head
```

### Issue: "Migration fails"

**Solution**:
```bash
# Check current migration
docker-compose exec backend alembic current

# Downgrade if needed
docker-compose exec backend alembic downgrade -1

# Try upgrade again
docker-compose exec backend alembic upgrade head
```

### Issue: "Tests fail with database errors"

**Solution**:
```bash
# Make sure test database exists
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE agentmedha_test;"

# Update pytest.ini if needed
# Run tests again
docker-compose exec backend pytest app/tests/test_context_system.py -v
```

### Issue: "Seed script fails"

**Solution**:
```bash
# Check if migrations ran
docker-compose exec postgres psql -U postgres -d agentmedha -c "\dt"

# Run seed script with more logging
docker-compose exec backend python -m app.scripts.seed_semantic_layer --verbose

# Or manually check what's failing
docker-compose exec backend python
>>> from app.scripts.seed_semantic_layer import main
>>> import asyncio
>>> asyncio.run(main())
```

---

## 📊 Expected Performance

After setup, you should see:

| Operation | Time | Notes |
|-----------|------|-------|
| Embedding generation | ~3ms | Per text |
| Similarity search (5 results) | ~20ms | With pgvector |
| Context retrieval (fresh) | ~100ms | Without cache |
| Context retrieval (cached) | ~5ms | With cache hit |
| Token counting | <1ms | With tiktoken |
| Context optimization | ~10ms | For ~10 items |
| End-to-end context | ~120ms | First call |
| End-to-end context | ~15ms | Cached |

---

## 🎯 Next Steps After Setup

Once everything is working:

1. **Review Documentation**
   - Read [CONTEXT_ENGINEERING.md](./CONTEXT_ENGINEERING.md)
   - Understand [SPRINT_1_COMPLETE.md](./SPRINT_1_COMPLETE.md)

2. **Add More Sample Data**
   - Modify `app/scripts/seed_semantic_layer.py`
   - Add metrics for your domain
   - Add glossary terms for your business

3. **Integrate with SQL Agent**
   - Update SQL agent to use `ContextManager`
   - Add context to prompts
   - Test query accuracy

4. **Monitor Performance**
   - Check Redis for cache hits
   - Monitor query times
   - Track context token usage

5. **Start Sprint 2**
   - Agent integration
   - Multi-turn conversations
   - Admin UI for metrics

---

## 📞 Getting Help

### Documentation
- **Overview**: [START_HERE_2.0.md](./START_HERE_2.0.md)
- **Architecture**: [CONTEXT_ENGINEERING.md](./CONTEXT_ENGINEERING.md)
- **Complete Report**: [SPRINT_1_COMPLETE.md](./SPRINT_1_COMPLETE.md)

### Code Examples
- **Services**: `backend/app/services/`
- **Tests**: `backend/app/tests/test_context_system.py`
- **Models**: `backend/app/models/semantic_layer.py`

### Quick Commands
```bash
# Restart everything
docker-compose restart

# View logs
docker-compose logs -f backend

# Check Redis
docker-compose exec redis redis-cli ping

# Check PostgreSQL
docker-compose exec postgres psql -U postgres -d agentmedha -c "SELECT version();"

# Run specific test
docker-compose exec backend pytest app/tests/test_context_system.py::TestEmbeddingService::test_generate_embedding -v
```

---

## ✅ Success Criteria

You're done when you see:

```
✅ Docker containers running
✅ Dependencies installed (tiktoken, pgvector)
✅ Migrations completed (003, 004)
✅ Sample data loaded (5 metrics, 6 terms, 3 rules)
✅ Embeddings created (11 total)
✅ Tests passing (22/22)
✅ Manual tests work
✅ Performance is good (<50ms context retrieval with cache)
```

---

## 🎉 You're Done!

If all checks pass, you've successfully set up the **Context Engineering System**!

**What you now have**:
- ✅ Semantic layer with business metrics
- ✅ Vector search with embeddings
- ✅ Context optimization for LLM prompts
- ✅ Multi-level caching for performance
- ✅ Comprehensive test suite
- ✅ Production-ready code

**What's next**:
- Integrate with SQL agent
- Build conversational interface
- Create admin UI for metrics
- Deploy to production

**Estimated time to complete setup**: **15 minutes**  
**Your progress**: Check items as you go! ✅

---

**🚀 Let's ship it!**

*If you run into issues, check the Troubleshooting section or review the documentation.*












