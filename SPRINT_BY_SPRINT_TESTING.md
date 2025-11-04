# 🧪 Sprint-by-Sprint Testing Guide

**Test analytical capabilities incrementally as development progresses**

---

## 🎯 Overview

This guide shows you how to test AgentMedha's analytical capabilities through the UI at each sprint, so you can see the agent get smarter with every feature we build!

### Testing Pages
1. **🧠 Agent Lab** (`/agent-test`) - Main chat interface with full pipeline visibility
2. **🔍 Context Test** (`/context-test`) - Deep dive into context engineering
3. **📊 Query** (`/`) - Production query interface

---

## 🚀 Quick Start (5 minutes)

### Setup
```bash
# Terminal 1: Backend
cd /Users/aravindgillella/dev/active/12FactorAgents/agentmedha
docker-compose up -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m app.scripts.seed_semantic_layer

# Terminal 2: Frontend  
cd frontend
npm install
npm run dev
```

### Access
1. Open http://localhost:5173
2. Login: `admin` / `admin123`
3. Click **"Agent Lab"** in the navigation (💬 icon)

---

## 📅 Sprint 1: Context Engineering Foundation

**Status**: ✅ COMPLETE  
**What to Test**: Context retrieval and optimization

### Test Scenarios

#### Scenario 1.1: Basic Context Retrieval
```
1. Go to Agent Lab
2. Select database
3. Ask: "What was our revenue last quarter?"
4. Click send
```

**What to Watch**:
- 🧠 Context step retrieves relevant metrics
- 📊 Shows: revenue metric, fiscal calendar rule
- ⚡ Cache hit on repeat (second query)
- Token utilization: 20-30%

**Expected Pipeline**:
```
✅ Context Retrieval (50-100ms)
   - 2-3 metrics found
   - Fiscal calendar applied
   - ~2000 tokens

✅ Table Discovery (20-50ms)
   - Orders table found
   
✅ SQL Generation (500ms-1s)
   - Uses correct fiscal dates
   - Applies revenue metric definition
   
✅ Execution (200-500ms)
   - Results returned
   
✅ Insights (300ms)
   - 2-3 key insights
```

#### Scenario 1.2: Token Budget Management
```
Query: "Tell me everything about revenue, customers, and churn"
```

**What to Watch**:
- Context optimizer prioritizes critical items
- Token budget respected (stays under 8000)
- Less important items truncated/summarized

#### Scenario 1.3: Cache Performance
```
1. First query: "What is our ARR?"
   - Should see 🔄 Cache Miss
   - Context step takes ~100ms
   
2. Same query again:
   - Should see ⚡ Cache Hit
   - Context step takes ~5-15ms
   
3. Go to Context Test page
4. Click "Clear All Cache"
5. Back to Agent Lab
6. Same query again:
   - Back to Cache Miss
```

### Success Criteria ✅
- [x] Context retrieved in <100ms
- [x] Relevant metrics found for query
- [x] Cache working (hit after first call)
- [x] Token budget respected
- [x] Business rules applied

---

## 📅 Sprint 2: Multi-Turn Conversations (NEXT)

**Status**: 🔨 IN PROGRESS  
**What to Test**: Conversational context and follow-up questions

### Test Scenarios

#### Scenario 2.1: Follow-up Questions
```
Conversation:
1. "What was our revenue last quarter?"
2. "How does that compare to last year?"
3. "Show me by customer segment"
4. "Which segment grew the most?"
```

**What to Watch**:
- Agent remembers previous context
- Doesn't re-ask for clarifications
- Uses pronouns correctly ("that", "it", "which")
- Context from previous turns included

**Expected Behavior**:
- Q1: Full context retrieval (~2000 tokens)
- Q2: Reuses Q1 context + adds comparison (~1500 tokens)
- Q3: Reuses previous + adds segment data (~1000 tokens)
- Q4: Minimal new context needed (~500 tokens)

#### Scenario 2.2: Topic Switching
```
Conversation:
1. "What is our ARR?"
2. "Now show me customer churn"
3. "Back to ARR - show me growth rate"
```

**What to Watch**:
- Agent switches topics cleanly
- Doesn't confuse metrics from different topics
- Retrieves new context when topic changes

#### Scenario 2.3: Clarification Handling
```
Conversation:
1. "Show me revenue"
   Agent: "Which time period? This quarter, last quarter, or year-to-date?"
2. "Last quarter"
   Agent: Provides specific data
```

### Success Criteria (When Built) 🎯
- [ ] Follow-up questions understood
- [ ] Context memory across 3-5 turns
- [ ] Smooth topic switching
- [ ] Clarification requests when needed
- [ ] Conversation history displayed

---

## 📅 Sprint 3-4: Advanced SQL & Query Optimization

**Status**: 📋 PLANNED  
**What to Test**: Complex queries and performance

### Test Scenarios

#### Scenario 3.1: Complex Aggregations
```
Queries to try:
- "Show me revenue by quarter for the last 2 years"
- "What is our customer lifetime value by segment?"
- "Compare ARR growth across all regions"
```

**What to Watch**:
- Complex JOINs handled correctly
- GROUP BY logic accurate
- Aggregations use correct fiscal calendar
- Performance optimizations applied

#### Scenario 3.2: Query Optimization
```
Query: "Show me all transactions with customer details"
```

**What to Watch In Pipeline**:
```
✅ SQL Generation
   - Automatic LIMIT added (100 rows)
   - Pagination suggested
   - Indexes recommended
   
✅ Execution
   - EXPLAIN ANALYZE run
   - Query plan displayed
   - Optimization suggestions
```

#### Scenario 3.3: Error Recovery
```
Query: "Show me revenue from the wrong_table"
```

**What to Watch**:
- Agent catches error
- Suggests correct table name
- Offers to retry with correction
- Error displayed in friendly way

### Success Criteria (When Built) 🎯
- [ ] Complex queries generate correct SQL
- [ ] Automatic query optimization
- [ ] Sub-second execution for typical queries
- [ ] Graceful error handling
- [ ] Helpful error messages

---

## 📅 Sprint 5-6: Visualizations & Charts

**Status**: 📋 PLANNED  
**What to Test**: Automatic chart generation

### Test Scenarios

#### Scenario 5.1: Auto Chart Selection
```
Queries:
1. "Show me revenue trend" → Line chart
2. "Compare revenue by segment" → Bar chart
3. "Show customer distribution by region" → Pie chart
4. "Plot revenue vs churn rate" → Scatter plot
```

**What to Watch In Pipeline**:
```
✅ Visualization Planning
   - Chart type selected automatically
   - Axes configured
   - Colors assigned
   
✅ Chart Generation
   - Data formatted correctly
   - Chart rendered
   - Interactive tooltips
```

#### Scenario 5.2: Multi-Chart Dashboards
```
Query: "Give me an executive summary of our performance"
```

**Expected Output**:
- 4-6 charts in dashboard layout
- Revenue trend (line)
- Top customers (bar)
- Geographic breakdown (map/pie)
- Key metrics (cards)

### Success Criteria (When Built) 🎯
- [ ] Correct chart type for data
- [ ] Beautiful, professional charts
- [ ] Interactive elements work
- [ ] Export to PNG/PDF
- [ ] Dashboard layouts responsive

---

## 📅 Sprint 7-8: AI Insights & Narratives

**Status**: 📋 PLANNED  
**What to Test**: Automated insight generation

### Test Scenarios

#### Scenario 7.1: Automatic Insights
```
Query: "Analyze our Q3 performance"
```

**Expected Insights**:
```
💡 Key Findings:
1. Revenue increased 23% YoY, driven by enterprise segment
2. Customer acquisition cost decreased 15% due to referral program
3. Churn rate stable at 2.8%, slightly below industry average
4. Warning: Sales pipeline down 12% - may impact Q4

🎯 Recommendations:
1. Focus sales efforts on enterprise segment (highest ROI)
2. Expand referral program to other segments
3. Investigate pipeline drop - schedule review with sales team
```

**What to Watch In Pipeline**:
```
✅ Insight Generation
   - Statistical analysis run
   - Trends identified
   - Anomalies detected
   - Recommendations generated
```

#### Scenario 7.2: Comparative Analysis
```
Query: "Compare this quarter vs last quarter"
```

**Expected Narrative**:
```
📊 Quarterly Comparison: Q3 2024 vs Q2 2024

Revenue Performance:
Q3 revenue of $2.4M represents a 12% increase over Q2's $2.1M.
This growth was primarily driven by the Enterprise segment, which
grew 28% quarter-over-quarter. However, SMB segment declined 5%,
requiring attention.

Customer Metrics:
Net new customers increased to 145 (vs 128 in Q2), representing
13% growth. Churn remained stable at 2.8% (vs 2.9% in Q2).

Overall: Strong quarter with accelerating enterprise growth. Focus
areas: SMB segment recovery and maintaining sales pipeline health.
```

### Success Criteria (When Built) 🎯
- [ ] Insights generated automatically
- [ ] Insights are actionable
- [ ] Narratives are clear and professional
- [ ] Anomalies detected
- [ ] Recommendations provided

---

## 📅 Sprint 9-10: Export & Sharing

**Status**: 📋 PLANNED  
**What to Test**: Collaboration features

### Test Scenarios

#### Scenario 9.1: Export Report
```
1. Generate analysis: "Q3 executive report"
2. Click "Export" button
3. Select format: PDF, PowerPoint, or Markdown
```

**Expected Output**:
- Professional formatted document
- Charts included with high resolution
- Data tables formatted
- Executive summary at top
- Methodology notes at bottom

#### Scenario 9.2: Share Analysis
```
1. Generate analysis
2. Click "Share"
3. Generate shareable link
4. Set permissions (view only, can comment, can edit)
5. Copy link
```

**What to Watch**:
- Link works for other users
- Permissions respected
- Conversation history included
- Real-time collaboration (if multiple users)

### Success Criteria (When Built) 🎯
- [ ] Export to PDF/PPT/MD works
- [ ] Shared links functional
- [ ] Permissions enforced
- [ ] Real-time collaboration
- [ ] Version history maintained

---

## 🧪 Continuous Testing Checklist

Use this checklist at each sprint to ensure nothing breaks:

### Regression Tests (Run Every Sprint)

#### Core Functionality
- [ ] Can login successfully
- [ ] Database connections work
- [ ] Context retrieval functional
- [ ] SQL generation works
- [ ] Query execution succeeds
- [ ] Results displayed correctly

#### Context System (Sprint 1+)
- [ ] Metrics found for queries
- [ ] Business rules applied
- [ ] Glossary terms included
- [ ] Cache working
- [ ] Token budget respected

#### Conversations (Sprint 2+)
- [ ] Follow-up questions work
- [ ] Context memory functional
- [ ] Topic switching smooth

#### Visualizations (Sprint 5+)
- [ ] Charts render correctly
- [ ] Interactive features work
- [ ] Export functions

#### Insights (Sprint 7+)
- [ ] Insights generated
- [ ] Narratives readable
- [ ] Recommendations actionable

---

## 🐛 What to Look For (Testing Checklist)

### For Every Query, Check:

#### 1. Pipeline Execution ✅
- [ ] All steps complete successfully
- [ ] No error states in pipeline
- [ ] Reasonable timing (<2s total)

#### 2. Context Quality ✅
- [ ] Relevant metrics retrieved
- [ ] Business rules applied correctly
- [ ] No irrelevant context included
- [ ] Token budget not exceeded

#### 3. SQL Accuracy ✅
- [ ] SQL is valid
- [ ] Uses correct tables/columns
- [ ] Applies filters from metrics
- [ ] Uses fiscal calendar when needed

#### 4. Results ✅
- [ ] Results returned successfully
- [ ] Data makes sense
- [ ] No obvious errors
- [ ] Formatted nicely

#### 5. Insights (When Available) ✅
- [ ] Insights are relevant
- [ ] Recommendations are actionable
- [ ] No hallucinations
- [ ] Backed by data

---

## 📊 Performance Benchmarks

Track these metrics at each sprint:

| Metric | Sprint 1 | Sprint 2 | Sprint 5 | Sprint 10 | Target |
|--------|---------|----------|----------|-----------|--------|
| Context Retrieval | 50-100ms | 50-100ms | 50-100ms | 50-100ms | <100ms |
| SQL Generation | 500ms-1s | 500ms-1s | 400-800ms | 300-600ms | <500ms |
| Query Execution | 200-500ms | 200-500ms | 150-400ms | 100-300ms | <200ms |
| Total Time | ~2s | ~2s | ~1.5s | ~1s | <1s |
| Accuracy | 75% | 85% | 92% | 95%+ | 95%+ |

---

## 🎯 Quick Test Commands

### Sample Queries for Each Sprint

```bash
# Sprint 1: Context & Basic Queries
"What was our revenue last quarter?"
"Show me our ARR"
"What is our customer count?"

# Sprint 2: Conversations
"What was revenue last quarter?"
  → "How does that compare to last year?"
  → "Show me by segment"

# Sprint 3-4: Complex SQL
"Show me revenue trend for last 2 years"
"Compare top 10 vs bottom 10 customers"
"Analyze customer cohorts by signup month"

# Sprint 5-6: Visualizations
"Chart revenue by month"
"Show customer distribution by region"
"Plot ARR growth rate"

# Sprint 7-8: Insights
"Analyze Q3 performance"
"What are the key trends this year?"
"Give me recommendations for Q4"

# Sprint 9-10: Export
[Generate any analysis]
→ Click "Export to PDF"
→ Click "Share Analysis"
```

---

## 🚀 Progressive Enhancement

With each sprint, the agent gets smarter:

```
Sprint 1:  Basic queries work
Sprint 2:  + Remembers context
Sprint 3:  + Complex SQL
Sprint 4:  + Query optimization
Sprint 5:  + Beautiful charts
Sprint 6:  + Multi-chart dashboards
Sprint 7:  + AI insights
Sprint 8:  + Professional narratives
Sprint 9:  + Export reports
Sprint 10: + Collaboration
Sprint 11: + Scheduled reports
Sprint 12: + Alert system
...
Sprint 18: Production-ready enterprise analytics platform!
```

---

## 📞 Troubleshooting

### Issue: Pipeline step fails

**Check**:
1. Backend logs: `docker-compose logs -f backend`
2. Frontend console: Browser DevTools → Console
3. Network tab: Check API responses

**Common Fixes**:
```bash
# Restart backend
docker-compose restart backend

# Check database
docker-compose exec postgres psql -U postgres -d agentmedha

# Verify migrations
docker-compose exec backend alembic current

# Re-seed data
docker-compose exec backend python -m app.scripts.seed_semantic_layer
```

### Issue: Context not found

**Check**:
1. Is data seeded? `SELECT COUNT(*) FROM metrics;`
2. Are embeddings created? `SELECT COUNT(*) FROM embeddings;`
3. Is Redis connected? `docker-compose ps redis`

**Fix**:
```bash
docker-compose exec backend python -m app.scripts.seed_semantic_layer
```

---

## ✅ Testing Success Criteria

You know testing is working when:

### Sprint 1
- ✅ Context retrieves in <100ms
- ✅ Relevant metrics found
- ✅ Business rules applied
- ✅ Cache hits after first query

### Sprint 2  
- ✅ Follow-up questions understood
- ✅ Context memory works 3-5 turns
- ✅ Topic switching smooth

### Future Sprints
- ✅ Complex queries work
- ✅ Charts render beautifully
- ✅ Insights are actionable
- ✅ Exports look professional
- ✅ 95%+ query accuracy

---

**🎉 Happy Testing!**

Test early, test often, and watch AgentMedha get smarter with every sprint! 🚀

---

**Quick Links**:
- [Sprint 1 Complete Report](./SPRINT_1_COMPLETE.md)
- [Context Engineering Architecture](./CONTEXT_ENGINEERING.md)
- [18-Sprint Roadmap](./GAP_ANALYSIS_AND_ROADMAP.md)
- [UI Testing Guide](./UI_TESTING_GUIDE.md)












