# 🏗️ Enhanced Architecture: Admin-Configured Data Sources

## 🎯 User Vision

### Admin Role
- **Configure data sources** - Finance DB, Sales DB, HR DB, etc.
- **Manage access** - Control who can query what
- **Monitor usage** - Track queries and performance
- **Maintain connections** - Test, update, troubleshoot

### Regular User Role
- **Chat with AI agent** - Natural language interface
- **Discover data sources** - "What data do you have about sales?"
- **Ask questions** - "Show me top products last quarter"
- **Get insights** - Agent auto-selects right database and generates queries

---

## 🔄 Required Changes

### 1. Database Connection Model Changes

**Current:**
```python
class DatabaseConnection:
    user_id: int  # Each user has their own connections
```

**New:**
```python
class DatabaseConnection:
    created_by: int  # Admin who created it
    is_shared: bool  # Shared across organization
    access_level: str  # 'public', 'restricted', 'private'
    allowed_users: list[int]  # If restricted
    allowed_roles: list[str]  # e.g., ['analyst', 'manager']
```

### 2. New User Roles

```python
class User:
    role: str  # 'admin', 'analyst', 'viewer'
    permissions: list[str]  # Fine-grained permissions
```

**Roles:**
- **Admin** - Configure data sources, manage users
- **Analyst** - Query all accessible data sources
- **Viewer** - Read-only access, limited queries

### 3. Chat Agent Enhancement

**Current Flow:**
```
User → Query → Generate SQL → Execute
```

**New Flow:**
```
User: "Show me sales data"
  ↓
Agent: Analyzes intent
  ↓
Agent: Discovers available data sources
  ↓
Agent: "I found these databases with sales data:
        1. Sales DB (2024 transactions)
        2. Finance DB (revenue reports)
       Which would you like to query?"
  ↓
User: "Sales DB"
  ↓
Agent: Generates SQL for Sales DB
  ↓
Agent: Executes and shows results
```

### 4. Data Source Discovery

**New API Endpoints:**
```
GET /api/v1/datasources/discover?query="sales"
  → Returns relevant data sources based on:
     - Database name/description
     - Table names and columns
     - User's access level
     - Semantic similarity

GET /api/v1/datasources/accessible
  → Returns all data sources user can query

GET /api/v1/datasources/{id}/summary
  → Quick overview: tables, row counts, last update
```

### 5. Enhanced Query Page

**Current:**
```
┌─────────────────────────────────────┐
│  Your Question                      │
│  [What were total sales?        ]   │
│  [Ask]                              │
└─────────────────────────────────────┘
```

**New:**
```
┌─────────────────────────────────────┐
│  💬 Chat with your data             │
├─────────────────────────────────────┤
│  Agent: Hi! I have access to:       │
│    • Finance DB (3 tables)          │
│    • Sales DB (5 tables)            │
│    • HR DB (2 tables)               │
│  What would you like to know?       │
├─────────────────────────────────────┤
│  You: Show me sales last quarter    │
├─────────────────────────────────────┤
│  Agent: I'll query the Sales DB...  │
│  [Shows results]                    │
│                                     │
│  Agent: Would you like to:          │
│    • See a breakdown by region?     │
│    • Compare to previous quarter?   │
│    • Export this data?              │
└─────────────────────────────────────┘
```

---

## 🎨 New UI Components

### Admin: Data Source Management
```
┌─────────────────────────────────────────┐
│  Data Sources               [+ Add]     │
├─────────────────────────────────────────┤
│  🗄️ Finance DB              [Edit]      │
│     PostgreSQL • 3 tables               │
│     Access: All Analysts                │
│     Status: ✅ Healthy                  │
│     Queries today: 47                   │
├─────────────────────────────────────────┤
│  🗄️ Sales DB                [Edit]      │
│     MySQL • 5 tables                    │
│     Access: Sales Team Only             │
│     Status: ✅ Healthy                  │
│     Queries today: 124                  │
├─────────────────────────────────────────┤
│  🗄️ HR DB                   [Edit]      │
│     Snowflake • 2 tables                │
│     Access: HR & Managers               │
│     Status: ⚠️ Slow                     │
│     Queries today: 12                   │
└─────────────────────────────────────────┘
```

### User: Conversational Query Interface
```
┌─────────────────────────────────────────┐
│  💬 AgentMedha                          │
├─────────────────────────────────────────┤
│  [Data Sources] [History] [Help]       │
├─────────────────────────────────────────┤
│                                         │
│  📊 Available Data Sources              │
│  • Finance (accounts, transactions)     │
│  • Sales (customers, orders, products)  │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  You: What were our top products?       │
│                                         │
│  🤖 Agent:                              │
│  I'll analyze the Sales database...     │
│                                         │
│  Found: Top 5 products by revenue       │
│  [Table with results]                   │
│  [📊 Chart]                            │
│                                         │
│  💡 Insight: Widget Pro sales increased │
│     45% vs last quarter                 │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  You: Show me by region                 │
│                                         │
│  🤖 Agent:                              │
│  Breaking down by region...             │
│  [Regional breakdown]                   │
│                                         │
├─────────────────────────────────────────┤
│  [Type your question...             ]   │
└─────────────────────────────────────────┘
```

---

## 🔐 Access Control Model

### Data Source Access Levels

1. **Public** - All users can query
2. **Restricted** - Only specific users/roles
3. **Private** - Admin only

### Permission Matrix

```
┌──────────────┬───────┬─────────┬────────┐
│ Action       │ Admin │ Analyst │ Viewer │
├──────────────┼───────┼─────────┼────────┤
│ Add data src │   ✅  │    ❌   │   ❌   │
│ Edit data src│   ✅  │    ❌   │   ❌   │
│ Delete data  │   ✅  │    ❌   │   ❌   │
│ Query data   │   ✅  │    ✅   │   ✅   │
│ Export data  │   ✅  │    ✅   │   ❌   │
│ See all DBs  │   ✅  │    ❌   │   ❌   │
└──────────────┴───────┴─────────┴────────┘
```

---

## 🤖 Enhanced Agent Capabilities

### 1. Data Source Discovery Agent
```python
class DataSourceDiscoveryAgent:
    """Help users find the right data source."""
    
    async def discover(self, user_query: str, user: User):
        """
        Analyze query and suggest data sources.
        
        Example:
        Query: "sales data"
        Returns: [Sales DB, Finance DB (revenue)]
        """
```

### 2. Context-Aware SQL Agent
```python
class ContextAwareSQLAgent:
    """Generate SQL with data source context."""
    
    async def generate(
        self, 
        question: str,
        data_source: DataSource,
        conversation_history: list
    ):
        """
        Generate SQL considering:
        - Selected data source schema
        - Previous questions in conversation
        - User's access level
        """
```

### 3. Multi-Turn Conversation Agent
```python
class ConversationAgent:
    """Manage multi-turn conversations."""
    
    async def process(
        self,
        message: str,
        conversation_id: str,
        user: User
    ):
        """
        Handle conversation flow:
        1. Understand intent
        2. Discover/confirm data source
        3. Generate query
        4. Show results
        5. Suggest follow-ups
        """
```

---

## 🚀 Implementation Plan

### Phase 1: Current ✅
- [x] User authentication
- [x] Database connections
- [x] Basic query interface

### Phase 2: Admin Data Sources 🔄
- [ ] Add role-based access control
- [ ] Shared data sources (admin-configured)
- [ ] Data source discovery API
- [ ] Access control middleware

### Phase 3: Conversational Interface
- [ ] Multi-turn chat UI
- [ ] Data source discovery in chat
- [ ] Context-aware SQL generation
- [ ] Conversation history

### Phase 4: Advanced Features
- [ ] Auto-suggest data sources
- [ ] Cross-database queries
- [ ] Query recommendations
- [ ] Usage analytics

---

## 📊 Example User Journey

### Admin Setup
```
Admin logs in
  ↓
Goes to "Data Sources" (admin-only page)
  ↓
Adds "Sales DB"
  - Name: Sales Database
  - Description: Customer orders and products
  - Connection: mysql://...
  - Access: All Analysts
  - Keywords: sales, orders, revenue, customers
  ↓
Tests connection ✅
  ↓
Saves and makes available
```

### User Query Flow
```
User (Analyst) logs in
  ↓
Sees chat interface
  ↓
Agent: "Hi! You have access to 3 databases. What would you like to know?"
  ↓
User: "Show me top products"
  ↓
Agent: "I found 'products' in Sales DB. Let me query it..."
  [Shows SQL preview]
  ↓
User: "Yes, run it"
  ↓
Agent: [Executes, shows results, generates chart]
  ↓
Agent: "Would you like to see this by region?"
  ↓
User: "Yes"
  ↓
Agent: [Continues conversation...]
```

---

## 🎯 Benefits of This Architecture

1. **Simplified User Experience**
   - Users don't manage connections
   - Just ask questions naturally
   - Agent handles complexity

2. **Better Security**
   - Centralized access control
   - Admin manages credentials
   - Audit trail for all queries

3. **Scalability**
   - Add new data sources easily
   - Onboard users quickly
   - Manage permissions centrally

4. **Intelligence**
   - Agent learns from conversations
   - Suggests relevant data sources
   - Optimizes query patterns

---

## 🔥 Next Steps

1. **Update Models** - Add roles, shared data sources
2. **Build Admin UI** - Data source management page
3. **Enhance Chat Agent** - Discovery + conversation
4. **Implement RBAC** - Role-based access control
5. **Create Discovery API** - Find relevant data sources

Let's build this! 🚀














