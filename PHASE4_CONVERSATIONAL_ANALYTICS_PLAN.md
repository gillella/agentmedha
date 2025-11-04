# 🚀 Phase 4: Conversational Data Analytics

**Status**: In Planning  
**Start Date**: November 4, 2025  
**Estimated Duration**: 2-3 weeks  
**Goal**: Build a complete conversational interface for natural language data analytics

---

## 📊 Executive Summary

Phase 4 will complete the core vision of AgentMedha by connecting all the pieces into a seamless conversational analytics experience. Users will be able to discover data sources, ask questions in natural language, and receive SQL-generated insights with visualizations—all in a multi-turn conversation.

### What We're Building

```
User: "Show me sales data"
  ↓ Discovery Agent finds relevant databases
AgentMedha: "I found Sales DB. What would you like to know?"
  ↓ User selects database
User: "What's the total revenue this quarter?"
  ↓ Context-aware SQL generation
AgentMedha: [Shows SQL + Results + Bar Chart]
  ↓ Multi-turn conversation
User: "Now show me by region"
  ↓ Context carryforward + refinement
AgentMedha: [Updated SQL + Results + Regional breakdown]
```

---

## ✅ Current State (What's Done)

### Backend ✅
- ✅ Context Engineering System (embeddings, semantic search, context optimization)
- ✅ Context-aware SQL Agent (integrated with ContextManager)
- ✅ Discovery Agent (finds relevant data sources)
- ✅ Query endpoint (basic SQL execution)
- ✅ Simple chat endpoint (OpenAI integration)
- ✅ RBAC and shared data sources
- ✅ Database connectors (PostgreSQL, MySQL, Snowflake, BigQuery)
- ✅ MCP server integration

### Frontend ✅
- ✅ Modern chat UI (QueryPage.tsx)
- ✅ Discovery flow (search → select data source)
- ✅ Message history display
- ✅ Auth system and layout
- ✅ DataVisualization component (Plotly integration)

### What's Missing 🔧
- ❌ SQL query execution from chat interface
- ❌ Visualization rendering in chat
- ❌ Session/conversation management
- ❌ Multi-turn context carryforward
- ❌ Query refinement and follow-ups
- ❌ Error handling and user feedback
- ❌ Query history and bookmarks

---

## 🎯 Phase 4 Goals

### Primary Goals
1. **Complete Query Flow**: Discovery → SQL → Execution → Visualization
2. **Session Management**: Persistent conversations with context
3. **Multi-Turn Conversations**: Follow-up questions with context carryforward
4. **Visual Results**: Show SQL results as tables and charts
5. **Query Refinement**: Edit, rerun, and improve queries

### Success Metrics
- ✅ User can discover data source and execute query in <30 seconds
- ✅ 90%+ SQL query accuracy (with context)
- ✅ Support 5+ turn conversations with context
- ✅ Automatic visualization for 80%+ of queries
- ✅ <100ms context retrieval (cached)
- ✅ Zero context loss between turns

---

## 🏗️ Architecture Overview

### System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │ QueryPage    │  │ Chat UI     │  │ Visualization    │  │
│  │ (Discovery)  │→ │ (Messages)  │→ │ (Results/Charts) │  │
│  └──────────────┘  └─────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                   Backend API (FastAPI)                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │             Conversational Query Endpoint              │ │
│  │  /api/v1/chat/query (new!)                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                             ↕                                │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  Session     │  │  Context     │  │  SQL Agent      │  │
│  │  Manager     │→ │  Manager     │→ │  (integrated)   │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                             ↕                                │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  Query       │  │  Viz Agent   │  │  Insight Agent  │  │
│  │  Executor    │  │  (suggest)   │  │  (optional)     │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             ↕
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ PostgreSQL   │  │ Redis        │  │ User Databases  │  │
│  │ (metadata)   │  │ (sessions)   │  │ (query target)  │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Phase 4 Tasks Breakdown

### Task 4.1: Session Management System ⏱️ 1 day

**Backend Tasks**:
- [ ] Create `ConversationSession` model (PostgreSQL)
- [ ] Create `ConversationMessage` model (PostgreSQL)
- [ ] Build `SessionManager` service
  - Create session
  - Add message to session
  - Get session history
  - Update session state (data source selection, context)
  - Session expiration and cleanup
- [ ] Add Redis caching for active sessions
- [ ] Create migration for session tables

**Files to Create**:
```
backend/app/models/session.py         (100 LOC)
backend/app/services/session_manager.py  (250 LOC)
backend/alembic/versions/006_conversation_sessions.py  (75 LOC)
```

**API Endpoints**:
```python
POST   /api/v1/sessions                  # Create new session
GET    /api/v1/sessions/{session_id}     # Get session history
POST   /api/v1/sessions/{session_id}/messages  # Add message
DELETE /api/v1/sessions/{session_id}     # End session
```

---

### Task 4.2: Conversational Query Endpoint ⏱️ 2 days

**Backend Tasks**:
- [ ] Create unified `/api/v1/chat/query` endpoint
- [ ] Orchestrate full flow:
  1. Session management (get/create session)
  2. Discovery (if no data source selected)
  3. Context retrieval (from ContextManager)
  4. SQL generation (using context-aware SQLAgent)
  5. Query execution
  6. Result formatting
  7. Visualization suggestion
  8. Store message and results in session
- [ ] Add multi-turn support (reference previous queries)
- [ ] Add query refinement support
- [ ] Error handling and user feedback

**Files to Create**:
```
backend/app/api/v1/endpoints/chat_query.py  (400 LOC)
backend/app/services/query_orchestrator.py   (300 LOC)
```

**Request/Response Models**:
```python
# Request
{
  "session_id": "uuid",
  "message": "What's the total revenue?",
  "data_source_id": 123,  # optional, from session context
  "refinement_of": "message_id"  # optional, for follow-ups
}

# Response
{
  "message_id": "uuid",
  "session_id": "uuid",
  "response_type": "query_result" | "discovery" | "clarification",
  "message": "Here's your total revenue...",
  "sql_query": "SELECT SUM(revenue)...",
  "results": [...],
  "visualization": {
    "type": "bar_chart",
    "config": {...}
  },
  "context_stats": {
    "metrics_used": 3,
    "context_tokens": 2500,
    "cache_hit": true
  },
  "suggested_follow_ups": [
    "Show me by region",
    "Compare to last quarter"
  ]
}
```

---

### Task 4.3: Context Carryforward ⏱️ 1 day

**Backend Tasks**:
- [ ] Extend `ContextManager` with session awareness
- [ ] Add `get_context_for_follow_up()` method
- [ ] Store query context in session state
- [ ] Implement context carryforward:
  - Previous tables used
  - Previous filters applied
  - Previous metrics referenced
  - Previous results summary
- [ ] Add context pruning (keep only relevant context)

**Files to Modify**:
```
backend/app/services/context_manager.py  (+100 LOC)
backend/app/services/session_manager.py  (+50 LOC)
```

**Features**:
```python
# Example: Follow-up question with context
User: "What's the revenue by region?"
# SQL: SELECT region, SUM(revenue) FROM sales GROUP BY region

User: "Now show me just the top 5"
# Context: Previous query had region, revenue, sales table
# SQL: SELECT region, SUM(revenue) FROM sales GROUP BY region ORDER BY 2 DESC LIMIT 5

User: "And filter by this year"
# Context: Keep region grouping, add year filter
# SQL: SELECT region, SUM(revenue) FROM sales WHERE YEAR(date) = 2025 GROUP BY region ORDER BY 2 DESC LIMIT 5
```

---

### Task 4.4: Frontend Integration ⏱️ 2 days

**Frontend Tasks**:
- [ ] Update `QueryPage.tsx` to use new chat endpoint
- [ ] Add SQL query display (collapsible)
- [ ] Add results table rendering
- [ ] Add visualization rendering (using DataVisualization component)
- [ ] Add suggested follow-up buttons
- [ ] Add query refinement UI
- [ ] Add loading states and animations
- [ ] Add error handling and retry
- [ ] Add export functionality (CSV, JSON)

**Files to Modify**:
```
frontend/src/pages/QueryPage.tsx          (+200 LOC)
frontend/src/components/QueryResult.tsx   (+150 LOC)
frontend/src/services/api.ts              (+50 LOC)
```

**New Components**:
```
frontend/src/components/
  ├── ChatMessage.tsx              (150 LOC) - Enhanced message display
  ├── SQLDisplay.tsx               (100 LOC) - SQL query display with syntax highlighting
  ├── ResultsTable.tsx             (150 LOC) - Paginated results table
  ├── ChartDisplay.tsx             (100 LOC) - Chart rendering wrapper
  └── SuggestedActions.tsx         (80 LOC)  - Follow-up suggestions
```

**UI Features**:
```typescript
// Message types
type MessageType = 
  | "discovery"        // Data source suggestions
  | "query_result"     // SQL results + viz
  | "clarification"    // Need more info
  | "error"           // Something went wrong
  | "info"            // General info

// Message display
<ChatMessage>
  <Text>{message}</Text>
  {sql && <SQLDisplay query={sql} />}
  {results && <ResultsTable data={results} />}
  {visualization && <ChartDisplay config={visualization} />}
  {followUps && <SuggestedActions actions={followUps} />}
</ChatMessage>
```

---

### Task 4.5: Visualization Agent ⏱️ 1 day

**Backend Tasks**:
- [ ] Create `VisualizationAgent` service
- [ ] Implement chart type recommendation:
  - Analyze result structure (columns, data types, row count)
  - Detect patterns (time series, categories, aggregations)
  - Suggest chart type (bar, line, pie, scatter, heatmap, table)
- [ ] Generate Plotly configuration
- [ ] Add color scheme selection
- [ ] Add responsive layout config

**Files to Create**:
```
backend/app/agents/visualization_agent.py  (250 LOC)
backend/app/tests/test_visualization_agent.py  (150 LOC)
```

**Logic**:
```python
def recommend_visualization(results, sql_query, result_metadata):
    """
    Recommend visualization based on:
    - Column types (date, numeric, categorical)
    - Row count
    - Aggregation type (SUM, COUNT, AVG)
    - Query patterns (GROUP BY, ORDER BY, time series)
    """
    
    # Time series detection
    if has_date_column(results) and row_count > 5:
        return {
            "type": "line_chart",
            "x": date_column,
            "y": numeric_columns,
            "title": "Trend over time"
        }
    
    # Categorical comparison
    if has_group_by(sql_query) and row_count <= 20:
        return {
            "type": "bar_chart",
            "x": category_column,
            "y": aggregate_column,
            "title": f"{aggregate} by {category}"
        }
    
    # Many rows, few columns → table
    if row_count > 50:
        return {"type": "table"}
    
    return {"type": "table"}  # Default
```

---

### Task 4.6: Query Refinement & Feedback ⏱️ 1 day

**Backend Tasks**:
- [ ] Add query refinement endpoint
- [ ] Support refinement types:
  - Add filter
  - Change aggregation
  - Modify limit/offset
  - Change sort order
  - Add/remove columns
- [ ] Track refinement history
- [ ] Add user feedback collection (👍👎)
- [ ] Store feedback for future improvements

**Frontend Tasks**:
- [ ] Add "Refine Query" button
- [ ] Show refinement options based on query type
- [ ] Add feedback buttons
- [ ] Show refinement history

**API Endpoints**:
```python
POST /api/v1/chat/refine
{
  "message_id": "uuid",
  "refinement_type": "add_filter" | "change_limit" | "modify_columns",
  "refinement_params": {
    "filter": "WHERE region = 'US'",
    "limit": 10
  }
}

POST /api/v1/chat/feedback
{
  "message_id": "uuid",
  "feedback_type": "positive" | "negative",
  "comment": "SQL was incorrect..."
}
```

---

### Task 4.7: Testing & Documentation ⏱️ 1 day

**Testing Tasks**:
- [ ] Unit tests for SessionManager
- [ ] Unit tests for QueryOrchestrator
- [ ] Unit tests for VisualizationAgent
- [ ] Integration tests for full query flow
- [ ] Frontend component tests
- [ ] End-to-end tests (Playwright)

**Documentation Tasks**:
- [ ] API documentation (OpenAPI)
- [ ] User guide (how to use conversational interface)
- [ ] Developer guide (how to extend agents)
- [ ] Architecture diagrams
- [ ] Demo video/GIFs

**Files to Create**:
```
backend/app/tests/test_session_manager.py
backend/app/tests/test_query_orchestrator.py
backend/app/tests/test_chat_integration.py
docs/USER_GUIDE.md
docs/API_REFERENCE.md
docs/DEMO_WALKTHROUGH.md
```

---

## 🎨 UI/UX Design

### Chat Message Types

#### 1. Discovery Message
```
┌────────────────────────────────────────┐
│ 💬 AgentMedha                          │
│ I found 3 data sources matching        │
│ "sales data":                          │
│                                        │
│ ┌──────────────────────────────────┐ │
│ │ 📊 Sales Database                │ │
│ │ PostgreSQL • Production          │ │
│ │ Keywords: sales, revenue, orders │ │
│ └──────────────────────────────────┘ │
│                                        │
│ [Select Data Source]                   │
└────────────────────────────────────────┘
```

#### 2. Query Result Message
```
┌────────────────────────────────────────┐
│ 💬 AgentMedha                          │
│ Here's your total revenue by region:   │
│                                        │
│ ▼ SQL Query                            │
│   SELECT region, SUM(revenue)          │
│   FROM sales GROUP BY region...        │
│                                        │
│ ┌──────────────────────────────────┐ │
│ │       Revenue by Region          │ │
│ │  [Bar Chart Visualization]       │ │
│ │                                  │ │
│ │  North America:  $1.2M           │ │
│ │  Europe:         $850K           │ │
│ │  Asia Pacific:   $620K           │ │
│ └──────────────────────────────────┘ │
│                                        │
│ 💡 Suggested follow-ups:               │
│ • Show me by month                     │
│ • Compare to last year                 │
│ • Show top 10 customers                │
└────────────────────────────────────────┘
```

#### 3. Clarification Message
```
┌────────────────────────────────────────┐
│ 💬 AgentMedha                          │
│ I need a bit more information...       │
│                                        │
│ Which time period would you like?      │
│ • This month                           │
│ • This quarter                         │
│ • This year                            │
│ • Custom date range                    │
└────────────────────────────────────────┘
```

---

## 📊 Success Metrics

### Technical Metrics
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Query Success Rate | >90% | TBD | 🎯 |
| Context Retrieval Time | <100ms | ~50ms | ✅ |
| End-to-End Query Time | <5s | TBD | 🎯 |
| Cache Hit Rate | >70% | TBD | 🎯 |
| Visualization Success Rate | >80% | TBD | 🎯 |
| Multi-turn Success Rate | >85% | TBD | 🎯 |

### User Experience Metrics
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Time to First Query | <30s | TBD | 🎯 |
| Queries per Session | >5 | TBD | 🎯 |
| User Satisfaction (👍) | >80% | TBD | 🎯 |
| Error Rate | <5% | TBD | 🎯 |
| Session Duration | >5min | TBD | 🎯 |

---

## 🔄 Development Timeline

### Week 1: Backend Foundation
- **Days 1-2**: Session management + conversational query endpoint
- **Days 3-4**: Context carryforward + query orchestrator
- **Day 5**: Testing and bug fixes

### Week 2: Frontend & Agents
- **Days 1-2**: Frontend integration (results, viz, UI)
- **Day 3**: Visualization agent
- **Day 4**: Query refinement + feedback
- **Day 5**: Polish and testing

### Week 3: Testing & Launch
- **Days 1-2**: Comprehensive testing (unit, integration, E2E)
- **Day 3**: Documentation and user guide
- **Day 4**: Demo preparation
- **Day 5**: Launch and monitoring

---

## 🚀 Deployment Plan

### Pre-Launch Checklist
- [ ] All tests passing (unit, integration, E2E)
- [ ] Performance benchmarks met
- [ ] Security audit completed
- [ ] Documentation complete
- [ ] Demo ready
- [ ] Monitoring dashboards configured
- [ ] Error tracking enabled (Sentry)
- [ ] Backup strategy in place

### Launch Steps
1. **Deploy to Staging**
   - Run full test suite
   - Manual QA testing
   - Invite beta users

2. **Beta Testing** (1 week)
   - 10-20 internal users
   - Collect feedback
   - Fix critical bugs
   - Monitor performance

3. **Production Launch**
   - Deploy to production
   - Enable monitoring
   - Announce to users
   - Monitor closely for first 48 hours

4. **Post-Launch**
   - Daily monitoring for 1 week
   - Collect user feedback
   - Plan iteration based on feedback

---

## 🎓 Learning & Documentation

### User Documentation
- [ ] Quick Start Guide
- [ ] Video Tutorial (5 min)
- [ ] FAQ
- [ ] Example Queries Library
- [ ] Best Practices

### Developer Documentation
- [ ] API Reference
- [ ] Architecture Overview
- [ ] How to Add New Agents
- [ ] Testing Guide
- [ ] Deployment Guide

---

## 🔮 Future Enhancements (Phase 5+)

### Short Term (1-2 months)
- [ ] Query bookmarks and favorites
- [ ] Share queries with team
- [ ] Scheduled queries/reports
- [ ] Email alerts for key metrics
- [ ] Mobile-responsive design

### Medium Term (3-6 months)
- [ ] Dashboard builder (drag & drop)
- [ ] Custom metrics library
- [ ] Advanced visualizations (geo maps, sankey, etc.)
- [ ] Query templates
- [ ] Team collaboration features

### Long Term (6-12 months)
- [ ] Predictive insights (ML-powered)
- [ ] Anomaly detection
- [ ] Natural language reports
- [ ] Voice interface
- [ ] Multi-language support

---

## 📞 Support & Resources

### Development Resources
- **Backend**: FastAPI, SQLAlchemy, OpenAI, Redis, PostgreSQL
- **Frontend**: React, TypeScript, TailwindCSS, Plotly, React Query
- **Testing**: Pytest, Jest, Playwright
- **Monitoring**: Prometheus, Grafana, Sentry

### Team Communication
- Daily standups (15 min)
- Weekly demos
- Slack channel: #agentmedha-dev
- Issue tracking: GitHub Issues

### Getting Help
- Check documentation first
- Ask in Slack
- Create GitHub issue for bugs
- Schedule pairing session if needed

---

## ✅ Sign-Off

**Phase 4: Conversational Data Analytics**
- **Status**: 📋 Planning Complete
- **Next Step**: Begin implementation
- **Estimated Completion**: 3 weeks
- **Risk Level**: Low (building on solid foundation)

**Prepared by**: AI Assistant  
**Date**: November 4, 2025  
**Approved**: Ready to start development

---

**🚀 Let's build the future of conversational analytics!**

*This phase will complete the core vision of AgentMedha and deliver real value to users.*

