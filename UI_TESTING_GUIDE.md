# 🎨 UI Testing Guide: Context Engineering System

**Quick guide to test the context engineering system with the new UI**

---

## 🚀 Quick Start (5 minutes)

### Step 1: Ensure Backend is Running

```bash
cd /Users/aravindgillella/dev/active/12FactorAgents/agentmedha

# Make sure Docker is running
docker-compose up -d

# Verify backend is healthy
curl http://localhost:8000/health
# Should return: {"status":"healthy","version":"1.0.0","environment":"development"}
```

### Step 2: Run Migrations & Seed Data

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Seed sample data (5 metrics, 6 glossary terms, 3 rules)
docker-compose exec backend python -m app.scripts.seed_semantic_layer

# Expected output:
# ✅ Seeded 5 metrics
# ✅ Seeded 6 glossary terms  
# ✅ Seeded 3 business rules
```

### Step 3: Start Frontend

```bash
# In a new terminal
cd /Users/aravindgillella/dev/active/12FactorAgents/agentmedha/frontend

# Install dependencies (if needed)
npm install

# Start dev server
npm run dev

# Should start on http://localhost:5173
```

### Step 4: Login & Navigate

1. **Open browser**: http://localhost:5173
2. **Login** with admin credentials:
   - Username: `admin`
   - Password: `admin123` (or your configured admin password)
3. **Navigate** to **"Context Test"** in the top menu (🧠 icon)

---

## 🎯 What You'll See

### Context Test Page Layout

```
┌─────────────────────────────────────────────────────┐
│  🧠 Context Engineering Test Lab                     │
├─────────────────────────────────────────────────────┤
│  Stats Overview (4 cards)                            │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                       │
│  │ 5  │ │ 6  │ │ 3  │ │ 11 │                       │
│  └────┘ └────┘ └────┘ └────┘                       │
│  Metrics Terms Rules Embeddings                     │
├─────────────────────────────────────────────────────┤
│  LEFT COLUMN          │  RIGHT COLUMN               │
│  ┌──────────────────┐│  ┌───────────────────────┐ │
│  │ 🔍 Test Context  ││  │ 📊 Business Metrics   │ │
│  │   Retrieval      ││  │   (list of 5 metrics) │ │
│  │                  ││  │                       │ │
│  │  Query:          ││  │ ✓ Revenue            │ │
│  │  [text area]     ││  │ ✓ ARR                │ │
│  │                  ││  │ ✓ MRR                │ │
│  │  Database ID: 1  ││  │   Customer Count     │ │
│  │  Max Tokens: 8000││  │   Churn Rate         │ │
│  │                  ││  └───────────────────────┘ │
│  │  [Retrieve Btn]  ││                            │
│  └──────────────────┘│  ┌───────────────────────┐ │
│                       │  │ 📚 Business Glossary  │ │
│  ┌──────────────────┐│  │   (list of 6 terms)   │ │
│  │ 📊 Context Stats ││  │                       │ │
│  │                  ││  │ ARR, MRR, churn, ...  │ │
│  │  2500 tokens     ││  └───────────────────────┘ │
│  │  31% utilization ││                            │
│  │                  ││  ┌───────────────────────┐ │
│  │  3 metrics       ││  │ 🗄️ Cache Control      │ │
│  │  2 examples      ││  │  [Clear Cache]        │ │
│  │  1 rule          ││  └───────────────────────┘ │
│  └──────────────────┘│                            │
│                       │                            │
│  ┌──────────────────┐│                            │
│  │ 📄 Context       ││                            │
│  │    Preview       ││                            │
│  │  [scrollable]    ││                            │
│  └──────────────────┘│                            │
└───────────────────────┴────────────────────────────┘
```

---

## 🧪 Testing Scenarios

### Scenario 1: Basic Context Retrieval ✅

**Test**: "What was our revenue last quarter?"

1. Enter query in text area
2. Keep Database ID = 1, Max Tokens = 8000
3. Click "🚀 Retrieve Context"

**Expected Results**:
- ⚡ Stats show context tokens (1500-2500)
- 📊 Shows 2-3 metrics included
- 📄 Context preview displays:
  - Business metrics (Revenue, ARR)
  - Business rules (Fiscal calendar)
  - User permissions
- Cache miss on first call, cache hit on second

**Success Criteria**:
```json
{
  "stats": {
    "context_tokens": 1500-2500,
    "utilization": 20-35%,
    "cache_hit": false (first), true (second)
  },
  "metadata": {
    "metrics_count": 2-3,
    "items_included": 5-8
  }
}
```

---

### Scenario 2: Token Budget Test ⚖️

**Test**: Low token budget forces prioritization

1. Enter: "Show me all customer metrics and revenue"
2. Set Max Tokens = **500** (very low)
3. Click Retrieve

**Expected Results**:
- Only highest priority items included
- Schema + Metrics (no examples/glossary)
- Utilization ~90-100%
- Fewer items included (2-3)

**Success Criteria**:
- Context tokens < 500
- Essential context still present
- No unnecessary items

---

### Scenario 3: Cached vs Fresh Retrieval 🚀

**Test**: Cache performance

1. Enter: "What is our ARR?"
2. Click Retrieve (first time)
   - Should show "🔄 Cache Miss"
   - Takes ~100-150ms
3. Click Retrieve again (same query)
   - Should show "⚡ Cache Hit"
   - Takes ~5-15ms
4. Click "🗑️ Clear All Cache"
5. Click Retrieve again
   - Should show "🔄 Cache Miss" again

**Success Criteria**:
- Cache hit after initial retrieval
- Much faster response time on cache hit
- Cache cleared successfully

---

### Scenario 4: Different Query Types 🔍

**Try these queries**:

```
Financial Queries:
✅ "What was our revenue last quarter?"
✅ "Show me ARR by customer segment"
✅ "What is our monthly churn rate?"

Customer Queries:
✅ "How many active customers do we have?"
✅ "Show customer count by region"
✅ "What is our customer retention?"

Complex Queries:
✅ "Compare revenue this quarter vs last quarter"
✅ "Show me top 10 customers by ARR"
✅ "What's our CAC and LTV ratio?"
```

**Expected Results**:
- Different metrics retrieved based on query
- Relevant glossary terms appear
- Business rules applied (fiscal calendar)

---

## 📊 Understanding the Results

### Context Stats Breakdown

```
┌─────────────────────────────────────┐
│ Context Tokens: 2345                │  ← Total tokens in context
│ Token Utilization: 29.3%            │  ← % of max budget used
│ Cache Hit: ⚡ Yes / 🔄 No            │  ← Cache performance
├─────────────────────────────────────┤
│ Metrics: 3                          │  ← Business metrics found
│ Examples: 2                         │  ← Similar queries found
│ Rules: 1                            │  ← Business rules applied
│ Glossary: 2                         │  ← Terms included
├─────────────────────────────────────┤
│ Items: 8 / 15                       │  ← Included / Available
└─────────────────────────────────────┘
```

### Context Preview Structure

The preview shows assembled context in this order:

```markdown
## User Permissions
{"role": "analyst", "can_query": true}

## Database Schema
Table: orders
Columns:
  - id (INTEGER) NOT NULL
  - total_amount (NUMERIC) NOT NULL
  - status (VARCHAR) NOT NULL
  ...

## Business Metrics
Metric: Total Revenue
Definition: Total revenue from completed orders
SQL: SUM(orders.total_amount)
Status: ✓ Certified
Filters: {'status': 'completed', 'paid': True}

## Business Rules
Rule: Fiscal Year Definition
Type: fiscal_calendar
Definition: {
  "fiscal_year_start": "November 1",
  "quarters": {...}
}

## Example Queries
Example Question: What was revenue last month?
SQL: SELECT SUM(total_amount) FROM orders...
```

---

## 🎨 Visual Elements

### Color Coding
- **Blue**: Metrics, tokens
- **Green**: Certified items, cache hits
- **Yellow**: Cache misses, warnings
- **Purple**: Glossary, rules
- **Red**: Errors, cache clear

### Interactive Elements
- **Hover**: Cards highlight on hover
- **Click**: Metric/glossary cards expand (future)
- **Refresh**: 🔄 buttons reload data
- **Clear**: 🗑️ button requires confirmation

---

## 🐛 Troubleshooting

### Issue: "Failed to retrieve context"

**Possible causes**:
1. Backend not running
2. Database not migrated
3. No seed data loaded

**Solution**:
```bash
# Check backend
docker-compose ps backend

# Check logs
docker-compose logs -f backend

# Re-run migrations
docker-compose exec backend alembic upgrade head

# Re-seed data
docker-compose exec backend python -m app.scripts.seed_semantic_layer
```

---

### Issue: "No metrics found"

**Cause**: Seed data not loaded

**Solution**:
```bash
# Check if data exists
docker-compose exec postgres psql -U postgres -d agentmedha -c "SELECT COUNT(*) FROM metrics;"

# Should return: count = 5
# If 0, run seed script again
```

---

### Issue: "Cache not working"

**Possible causes**:
1. Redis not running
2. Cache service not connected

**Solution**:
```bash
# Check Redis
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# Check backend logs for cache errors
docker-compose logs backend | grep cache
```

---

### Issue: "Context tokens = 0"

**Cause**: Context optimization failed

**Check**:
1. Query too short?
2. No matching metrics?
3. All items filtered out?

**Solution**: Try a different query or increase max tokens

---

## 📈 Performance Benchmarks

### Expected Performance

| Operation | First Call | Cached |
|-----------|-----------|--------|
| Context Retrieval | ~100ms | ~15ms |
| Similarity Search | ~20ms | ~5ms |
| Token Counting | ~1ms | ~1ms |
| Context Assembly | ~10ms | instant |

### Token Usage Examples

| Query Type | Context Tokens | Utilization (8000 max) |
|------------|----------------|------------------------|
| Simple | 800-1200 | 10-15% |
| Medium | 1500-2500 | 20-30% |
| Complex | 3000-4500 | 40-55% |
| Very Complex | 5000-7000 | 65-85% |

---

## 🎯 Success Criteria

Your context system is working correctly if:

✅ **Stats Overview** shows:
- 5 metrics
- 6 glossary terms
- 3 business rules
- 11 total embeddings

✅ **Context Retrieval** returns:
- Non-zero context tokens
- Relevant metrics for query
- Properly formatted context
- Cache hits on repeated queries

✅ **Performance** meets targets:
- Context retrieval < 100ms (P95)
- Cache hit rate > 60% (after warmup)
- Token utilization 20-40% (typical)

✅ **Functionality** works:
- Different queries return different context
- Token budget respected
- Cache clear works
- Stats update correctly

---

## 🚀 Next Steps

After successful testing:

1. **Integrate with SQL Agent**
   - Use context in SQL generation prompts
   - Measure query accuracy improvement

2. **Add More Metrics**
   - Edit `seed_semantic_layer.py`
   - Add your domain-specific metrics
   - Re-run seed script

3. **Test with Real Queries**
   - Use actual business questions
   - Verify correct context retrieved
   - Iterate on metric definitions

4. **Monitor Performance**
   - Watch token usage
   - Optimize if needed
   - Adjust priorities

---

## 📞 Need Help?

### Documentation
- **API Docs**: http://localhost:8000/docs (when backend running)
- **Architecture**: [CONTEXT_ENGINEERING.md](./CONTEXT_ENGINEERING.md)
- **Implementation**: [SPRINT_1_COMPLETE.md](./SPRINT_1_COMPLETE.md)

### Quick Commands
```bash
# Restart everything
docker-compose restart

# View backend logs
docker-compose logs -f backend

# View frontend logs
cd frontend && npm run dev

# Run tests
docker-compose exec backend pytest app/tests/test_context_system.py -v
```

---

## ✅ Testing Checklist

Before considering testing complete:

- [ ] Backend running and healthy
- [ ] Migrations completed
- [ ] Sample data seeded
- [ ] Frontend accessible
- [ ] Can login as admin
- [ ] Context Test page loads
- [ ] Stats show correct counts
- [ ] Can retrieve context for queries
- [ ] Context preview displays properly
- [ ] Cache hit/miss working
- [ ] Token budget respected
- [ ] All interactive elements work

---

**🎉 Happy Testing!**

The context engineering system is your competitive advantage. Test it thoroughly and see the difference it makes in SQL accuracy! 🚀












