# 🚀 START TESTING NOW!

**Your 5-minute guide to start talking to the agent**

---

## ⚡ Quick Start (Just 3 Commands!)

```bash
# 1. Start backend
cd /Users/aravindgillella/dev/active/12FactorAgents/agentmedha
docker-compose up -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m app.scripts.seed_semantic_layer

# 2. Start frontend (new terminal)
cd frontend
npm run dev

# 3. Open browser
# Go to: http://localhost:5173
# Login: admin / admin123
# Click: "Agent Lab" 💬
```

**That's it! You're ready to test!** 🎉

---

## 💬 Your First Conversation

### Try This Right Now:

```
You: "What was our revenue last quarter?"

Agent: 📊 Analysis Complete

Generated SQL:
SELECT SUM(orders.total_amount) as revenue
FROM orders  
WHERE order_date BETWEEN '2024-05-01' AND '2024-07-31'
  AND status = 'completed'
  AND paid = true

Results: 42 rows returned

Sample Data:
1. {"id":1,"customer":"Acme Corp","amount":15000,"date":"2024-Q3"}
2. {"id":2,"customer":"TechStart","amount":8500,"date":"2024-Q3"}

💡 Key Insights:
1. Revenue increased 23% compared to last quarter
2. Top performing segment: Enterprise customers
3. Recommended action: Focus on upsell opportunities
```

### What You'll See:

The **Pipeline View** (on the left side of chat messages):

```
✅ Context Retrieval (75ms)
   - Found revenue metric
   - Applied fiscal calendar
   - 2,345 tokens

✅ Table Discovery (32ms)
   - Found orders table
   
✅ SQL Generation (842ms)
   - Used certified revenue metric
   - Applied fiscal Q3 dates
   
✅ Execution (234ms)
   - Returned 42 rows
   
✅ Insights (156ms)
   - Generated 3 insights
```

Click any step to see details! 🔍

---

## 🧪 What to Test (Sprint 1 - Current)

### 1. Basic Questions ✅

```
💰 Financial Queries:
"What was our revenue last quarter?"
"Show me our ARR"
"What is our MRR?"

👥 Customer Queries:
"How many active customers do we have?"
"What is our churn rate?"

📊 Metrics:
"Show me customer count"
"What are our key metrics?"
```

### 2. Watch the Pipeline ✅

For each query, **check the pipeline**:
- ✅ Context retrieval finds relevant metrics
- ✅ Business rules applied (fiscal calendar)
- ✅ SQL uses correct definitions
- ✅ Cache hits on repeat queries

**Toggle Pipeline**: Uncheck "Show Pipeline" to hide details

### 3. Test Caching ⚡

```
1. Ask: "What is our ARR?"
   → See 🔄 Cache Miss (~100ms)
   
2. Ask same question again
   → See ⚡ Cache Hit (~15ms)
   
3. Go to "Context Test" page
4. Click "Clear All Cache"
5. Back to Agent Lab
6. Ask again
   → Back to Cache Miss
```

### 4. Compare Databases 🗄️

```
1. Select different database from dropdown
2. Ask same question
3. Watch different tables/metrics appear
```

---

## 🎨 Interface Guide

### Agent Lab Layout

```
┌────────────────────────────────────────────┐
│ 🧠 Agent Testing Lab            [DB:▼] [☑️] │
├────────────────────────────────────────────┤
│                                            │
│  🤖 Agent: Ready to analyze!              │
│                                            │
│  👤 You: What was revenue last quarter?   │
│                                            │
│  🤖 Agent: 📊 Analysis Complete            │
│            [SQL + Results + Insights]      │
│                                            │
│      [Pipeline Steps - Expandable] ▼       │
│       ✅ Context (75ms)                    │
│       ✅ Discovery (32ms)                  │
│       ✅ SQL Gen (842ms)                   │
│       ✅ Execution (234ms)                 │
│       ✅ Insights (156ms)                  │
│                                            │
├────────────────────────────────────────────┤
│ [Type message...] [Send] ▶                 │
│ [💰 Revenue] [👥 Customers] [📉 Churn]... │
└────────────────────────────────────────────┘
```

### Quick Action Buttons

Click these pre-made queries:
- **💰 Revenue last quarter** - Test revenue metric
- **👥 Top customers** - Test customer data
- **📉 Churn rate** - Test churn calculation
- **📊 Compare quarters** - Test comparative analysis

---

## 🎯 What's Working (Sprint 1)

### ✅ Fully Functional
1. **Context Engineering**
   - Finds relevant business metrics
   - Applies business rules (fiscal calendar)
   - Includes glossary terms
   - Caches aggressively
   - Optimizes token usage

2. **Pipeline Visibility**
   - See every step
   - Expandable details
   - Timing information
   - Error states visible

3. **Basic Queries**
   - Revenue questions
   - Customer metrics
   - ARR/MRR calculations
   - Churn rate

### 🔨 Currently Simulated (For Testing)
- Table discovery (returns mock data)
- SQL generation (returns example SQL)
- Query execution (returns sample results)
- Insight generation (returns sample insights)

**These will be real in Sprints 2-4!**

---

## 🔍 Two Testing Modes

### Mode 1: Agent Lab (End-to-End)
**URL**: `/agent-test`  
**Purpose**: Talk naturally, see full pipeline  
**Best For**: Testing user experience

```
Features:
✅ Natural language input
✅ Full conversation history
✅ Pipeline visualization
✅ Quick action buttons
✅ Database selection
```

### Mode 2: Context Test (Deep Dive)
**URL**: `/context-test`  
**Purpose**: Test context system in detail  
**Best For**: Debugging context retrieval

```
Features:
✅ Metrics browser
✅ Glossary viewer
✅ Context preview
✅ Token analysis
✅ Cache control
```

**Use both for complete testing!**

---

## 📊 Sample Test Session

Here's a complete testing session:

```bash
# 1. Start services
docker-compose up -d

# 2. Check everything's running
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}

# 3. Open frontend
# Browser: http://localhost:5173

# 4. Login
# Username: admin
# Password: admin123

# 5. Go to Agent Lab
# Click "Agent Lab" in navigation

# 6. Test basic query
Type: "What was our revenue last quarter?"
Click: Send
Wait: ~2 seconds
See: Full analysis with pipeline

# 7. Test caching
Type: Same question again
Click: Send  
Wait: ~0.5 seconds (faster!)
See: ⚡ Cache Hit

# 8. Test different query
Type: "Show me our ARR"
See: Different metrics retrieved

# 9. Explore pipeline
Click: Any pipeline step
See: Detailed data for that step

# 10. Test Context Test page
Click: "Context Test" in nav
Browse: Available metrics
Browse: Glossary terms
Test: Context retrieval
Clear: Cache
Back: To Agent Lab

# Done! You've tested Sprint 1! ✅
```

---

## 🐛 Troubleshooting

### "Backend not responding"
```bash
docker-compose ps backend
# Should show: running

docker-compose logs -f backend
# Check for errors

docker-compose restart backend
```

### "No metrics found"
```bash
docker-compose exec backend python -m app.scripts.seed_semantic_layer
# Re-seed the data
```

### "Cache not working"
```bash
docker-compose ps redis
# Should show: running

docker-compose exec redis redis-cli ping
# Should return: PONG

docker-compose restart redis
```

### "Frontend won't start"
```bash
cd frontend
npm install
npm run dev
```

---

## 📈 What to Watch For

### Good Signs ✅
- Context retrieval completes in <100ms
- Relevant metrics appear for queries
- Cache hits after first query
- Pipeline steps all show success (✅)
- Token utilization 20-40%
- No errors in console

### Red Flags ❌
- Context retrieval >1 second
- No metrics found for obvious queries
- All cache misses
- Pipeline steps showing errors (❌)
- Token utilization >80%
- Console errors

---

## 🎯 Success Checklist

After your first session, you should have:

- [ ] Successfully started both backend and frontend
- [ ] Logged into the UI
- [ ] Accessed Agent Lab
- [ ] Asked at least 3 different questions
- [ ] Seen pipeline steps execute
- [ ] Observed context retrieval working
- [ ] Tested cache hit/miss
- [ ] Expanded pipeline steps to see details
- [ ] Visited Context Test page
- [ ] Viewed available metrics and glossary

**If you checked all boxes: You're ready!** ✅

---

## 🚀 Next Steps

### Today
1. ✅ Test basic queries
2. ✅ Explore both testing interfaces
3. ✅ Verify all pipeline steps work
4. ✅ Test caching

### This Week
1. Add your own metrics (edit seed script)
2. Test with your business questions
3. Monitor performance
4. Give feedback on UX

### Next Sprint (Sprint 2)
1. Multi-turn conversations
2. Follow-up questions
3. Context memory
4. Topic switching

---

## 📚 Documentation

### Essential Reading
1. **[SPRINT_BY_SPRINT_TESTING.md](./SPRINT_BY_SPRINT_TESTING.md)** ← **Read This Next!**
   - How to test each sprint's features
   - Progressive testing approach
   - What to look for at each stage

2. **[SPRINT_1_COMPLETE.md](./SPRINT_1_COMPLETE.md)**
   - What we built
   - Technical details
   - API reference

3. **[CONTEXT_ENGINEERING.md](./CONTEXT_ENGINEERING.md)**
   - How context system works
   - Why it's our advantage
   - Architecture details

### Quick Reference
- API Docs: http://localhost:8000/docs
- Context Test: http://localhost:5173/context-test
- Agent Lab: http://localhost:5173/agent-test

---

## 💬 Example Conversations

### Conversation 1: Financial Analysis
```
You: "What was our revenue last quarter?"
Agent: [Shows Q3 revenue of $2.4M]

You: "How does that compare to last year?"  
Agent: [Coming in Sprint 2 - multi-turn conversations]

You: "Show me by customer segment"
Agent: [Coming in Sprint 2]
```

### Conversation 2: Customer Metrics
```
You: "How many active customers do we have?"
Agent: [Shows 1,245 active customers]

You: "What is our churn rate?"
Agent: [Shows 2.8% monthly churn]

You: "Is that good?"
Agent: [Coming in Sprint 7 - AI insights]
```

### Conversation 3: Growth Analysis
```
You: "Show me our ARR growth"
Agent: [Shows ARR trend]

You: "What's driving the growth?"
Agent: [Coming in Sprint 7 - AI insights]

You: "Give me recommendations for Q4"
Agent: [Coming in Sprint 8 - recommendations]
```

---

## 🎉 You're Ready!

Everything is set up and waiting for you to test!

### The Setup You Have:
- ✅ Agent Lab with full pipeline visibility
- ✅ Context Test for deep debugging
- ✅ Sample data loaded (5 metrics, 6 terms, 3 rules)
- ✅ Working cache system
- ✅ Beautiful UI
- ✅ Comprehensive documentation

### What You Can Test:
- 💬 Natural language queries
- 🧠 Context engineering
- ⚡ Caching performance
- 📊 Pipeline execution
- 🎯 Token optimization

### What You'll Learn:
- How context engineering works
- Why AgentMedha will be 95%+ accurate
- What makes us different from competitors
- How to test incrementally
- What to expect in future sprints

---

**Ready? Let's go!** 🚀

```bash
# Last command to run:
cd /Users/aravindgillella/dev/active/12FactorAgents/agentmedha/frontend
npm run dev
```

**Then open**: http://localhost:5173  
**Click**: "Agent Lab" 💬  
**Type**: "What was our revenue last quarter?"  
**Press**: Send ▶️

**Welcome to the future of enterprise analytics!** 🎯












