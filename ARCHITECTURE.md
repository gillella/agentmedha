# AgentMedha - System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │  Chat Interface  │  │ Admin Dashboard  │  │ Data Catalog  │ │
│  │  (NL2SQL)        │  │ (MCP Servers)    │  │ (Resources)   │ │
│  └────────┬─────────┘  └────────┬─────────┘  └───────┬───────┘ │
│           │                     │                     │          │
└───────────┼─────────────────────┼─────────────────────┼──────────┘
            │                     │                     │
            │   React Frontend (TypeScript + Tailwind) │
            │                     │                     │
┌───────────┴─────────────────────┴─────────────────────┴──────────┐
│                        API GATEWAY                                │
│                     FastAPI (Python)                              │
└───────────┬─────────────────────┬─────────────────────┬──────────┘
            │                     │                     │
    ┌───────▼────────┐   ┌────────▼────────┐   ┌──────▼──────┐
    │  Query Service │   │  MCP Manager    │   │   Auth      │
    │  (NL2SQL)      │   │  (Connectors)   │   │   Service   │
    └───────┬────────┘   └────────┬────────┘   └──────┬──────┘
            │                     │                    │
            │            ┌────────▼────────┐          │
            │            │  MCP Connectors │          │
            │            │  - PostgreSQL   │          │
            │            │  - GitHub       │          │
            │            │  - SQLite       │          │
            │            │  - Filesystem   │          │
            │            └────────┬────────┘          │
            │                     │                    │
┌───────────┴─────────────────────┴────────────────────┴──────────┐
│                    DATA & STORAGE LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PostgreSQL  │  │    Redis     │  │   OpenAI     │          │
│  │  + pgvector  │  │   (Cache)    │  │   GPT-4      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Natural Language to SQL Flow

```
┌─────────────┐
│    User     │
│  "Show me   │
│  all users" │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────┐
│  SimpleChatPage.tsx          │
│  - Captures user input       │
│  - Manages conversation      │
└──────┬───────────────────────┘
       │ POST /api/v1/query/query
       │ { question, history }
       ▼
┌──────────────────────────────┐
│  query.py Endpoint           │
│  1. Get MCP servers          │
│  2. List resources (tables)  │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  MCP Manager                 │
│  - list_servers()            │
│  - list_resources()          │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Generate SQL Prompt         │
│  - Question                  │
│  - Available tables          │
│  - Schema information        │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  OpenAI GPT-4                │
│  - Generates SQL query       │
│  - Returns: SELECT * FROM... │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Execute SQL                 │
│  - Run against PostgreSQL    │
│  - Serialize results (UUID)  │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Generate Answer             │
│  - Send results to GPT-4     │
│  - Get natural language      │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Response                    │
│  {                           │
│    answer: "...",            │
│    sql_query: "SELECT...",   │
│    results: [...],           │
│    tables_used: [...]        │
│  }                           │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  SimpleChatPage.tsx          │
│  - Display answer            │
│  - Show SQL in code block    │
│  - Render results table      │
│  - List tables used          │
└──────────────────────────────┘
```

---

## 🗄️ Database Schema

### Core Tables

#### `users`
```sql
id                  SERIAL PRIMARY KEY
email               VARCHAR(255) UNIQUE
username            VARCHAR(100) UNIQUE
full_name           VARCHAR(255)
hashed_password     VARCHAR(255)
is_active           BOOLEAN DEFAULT TRUE
is_superuser        BOOLEAN DEFAULT FALSE
role                VARCHAR(50) DEFAULT 'user'
default_database_id INTEGER
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

#### `mcp_servers`
```sql
id                  UUID PRIMARY KEY
name                VARCHAR(255) UNIQUE
description         TEXT
server_type         VARCHAR(100)
config              JSONB
status              VARCHAR(50)
last_connected_at   TIMESTAMP
error_message       TEXT
created_by          UUID
organization_id     UUID
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

#### `mcp_resources`
```sql
id                  UUID PRIMARY KEY
server_id           UUID REFERENCES mcp_servers
resource_uri        TEXT UNIQUE
resource_type       VARCHAR(100)
name                VARCHAR(255)
description         TEXT
metadata            JSONB
last_synced_at      TIMESTAMP
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

#### `mcp_access_log`
```sql
id                  UUID PRIMARY KEY
server_id           UUID REFERENCES mcp_servers
user_id             UUID REFERENCES users
operation           VARCHAR(100)
resource_uri        TEXT
status              VARCHAR(50)
duration_ms         INTEGER
error_message       TEXT
accessed_at         TIMESTAMP
```

---

## 🔌 MCP Connector Architecture

### Base Connector Interface
```python
class MCPConnector(ABC):
    def __init__(self, config: Dict[str, Any])
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]
    
    @abstractmethod
    def discover_resources(self) -> List[Dict[str, Any]]
```

### Implemented Connectors

#### 1. PostgreSQLConnector
**Test Connection:**
- Connects using psycopg2
- Executes `SELECT 1`
- Returns success/failure

**Discover Resources:**
- Queries `information_schema.tables`
- Filters by schema (default: public)
- Returns table list with metadata

**Config:**
```json
{
  "host": "localhost",
  "port": 5432,
  "database": "agentmedha",
  "username": "postgres",
  "password": "agentmedha",
  "schema": "public"
}
```

#### 2. GitHubConnector (Placeholder)
**Config:**
```json
{
  "token": "ghp_...",
  "owner": "username",
  "repo": "repository"
}
```

#### 3. FilesystemConnector (Placeholder)
**Config:**
```json
{
  "path": "/path/to/directory",
  "allowed_extensions": ".txt,.md,.json"
}
```

#### 4. SQLiteConnector (Placeholder)
**Config:**
```json
{
  "database_path": "/path/to/database.db"
}
```

---

## 🎨 Frontend Component Hierarchy

```
App.tsx
├── Router
│   ├── LoginPage.tsx
│   └── Layout.tsx (Protected)
│       ├── Header (Navigation)
│       ├── Outlet
│       │   ├── SimpleChatPage.tsx
│       │   │   ├── Message bubbles
│       │   │   ├── SQL code blocks
│       │   │   ├── Results tables
│       │   │   └── Input textarea
│       │   │
│       │   └── AdminDashboard.tsx
│       │       ├── Tabs
│       │       │   ├── MCP Servers
│       │       │   │   └── MCPServersPage.tsx
│       │       │   │       ├── Server cards
│       │       │   │       ├── Action buttons
│       │       │   │       └── AddMCPServerModal.tsx
│       │       │   │
│       │       │   ├── Data Sources (Placeholder)
│       │       │   │
│       │       │   ├── Data Catalog
│       │       │   │   └── ResourcesPage.tsx
│       │       │   │       ├── Stats cards
│       │       │   │       ├── Search & filters
│       │       │   │       └── Resource cards (grouped)
│       │       │   │
│       │       │   └── Settings (Placeholder)
│       │       │
│       │       └── Tab content area
│       │
│       └── Footer
```

---

## 🔐 Authentication Flow

```
┌─────────────┐
│ LoginPage   │
│ (username/  │
│  password)  │
└──────┬──────┘
       │ POST /api/v1/auth/login
       ▼
┌──────────────────────────────┐
│  Backend Auth Service        │
│  1. Verify credentials       │
│  2. Generate JWT token       │
│  3. Return user + token      │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Zustand Store               │
│  - Save accessToken          │
│  - Save user info            │
│  - Set isAuthenticated       │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Navigate to Home            │
│  - Admin → Admin Dashboard   │
│  - User → Chat Interface     │
└──────────────────────────────┘

All subsequent API calls:
Authorization: Bearer {accessToken}
```

---

## 📦 Docker Services

```yaml
services:
  db:
    image: pgvector/pgvector:pg15
    ports: 5432:5432
    volumes: ./data/postgres
    
  redis:
    image: redis:7-alpine
    ports: 6379:6379
    
  backend:
    build: ./backend
    ports: 8000:8000
    depends_on: [db, redis]
    environment:
      - DATABASE_URL
      - REDIS_URL
      - OPENAI_API_KEY
    
  frontend:
    build: ./frontend
    ports: 5173:5173
    depends_on: [backend]
```

---

## 🔄 Data Catalog Auto-Query Flow

```
┌─────────────────────┐
│  ResourcesPage      │
│  (Data Catalog)     │
│                     │
│  [metrics]          │
│   ├─ Query ←────────┤ User clicks
│   ├─ Schema         │
│   └─ Preview        │
└──────┬──────────────┘
       │
       │ handleQueryResource("metrics")
       │ navigate('/chat?query=Tell me about the metrics table')
       ▼
┌─────────────────────────────┐
│  SimpleChatPage.tsx         │
│  - useSearchParams()        │
│  - Detect ?query=...        │
│  - setInput(query)          │
│  - Auto-send after 100ms    │
└──────┬──────────────────────┘
       │
       │ Automatic POST /api/v1/query/query
       ▼
┌─────────────────────────────┐
│  Display Results            │
│  - Natural language answer  │
│  - SQL query                │
│  - Results table            │
└─────────────────────────────┘
```

---

## 🛠️ Technology Stack Summary

### Backend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Framework | FastAPI | REST API endpoints |
| ORM | SQLAlchemy 2.0 (async) | Database operations |
| Database | PostgreSQL + pgvector | Data storage + vector search |
| Cache | Redis | Performance optimization |
| LLM | OpenAI GPT-4 | NL2SQL + answers |
| Logging | structlog | Structured logging |
| Validation | Pydantic | Request/response validation |

### Frontend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React 18 | UI components |
| Language | TypeScript | Type safety |
| Styling | Tailwind CSS | Modern UI design |
| Routing | React Router v6 | Navigation |
| State | Zustand | Lightweight state management |
| Icons | Lucide React | Beautiful icons |
| HTTP | fetch API | API calls |

### Infrastructure
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containerization | Docker + Compose | Service orchestration |
| Reverse Proxy | - | (Future: Nginx) |
| Monitoring | Prometheus + Grafana | (Optional) Metrics |

---

## 🔑 Key Design Decisions

### 1. MCP Connector Pattern
**Why:** Extensible architecture for multiple data source types
**Benefit:** Easy to add new connectors (GitHub, S3, etc.)

### 2. Async SQLAlchemy
**Why:** Better performance for I/O-bound operations
**Benefit:** Handle multiple concurrent requests efficiently

### 3. UUID Primary Keys
**Why:** Distributed system friendly, no ID collisions
**Challenge:** Needed serialization helper for JSON responses

### 4. JSONB for Configurations
**Why:** Flexible schema for different connector types
**Benefit:** No need to modify schema for new connector configs

### 5. Separate Chat and Admin UIs
**Why:** Different user personas with different needs
**Benefit:** Clean, focused interfaces

---

## 📊 Current System Metrics

- **Discovered Resources**: 14 tables
- **Active MCP Servers**: 1 (PostgreSQL)
- **Supported Connectors**: 4 (PostgreSQL, GitHub, SQLite, Filesystem)
- **API Endpoints**: 20+
- **Frontend Pages**: 5
- **Database Tables**: 10+

---

**Last Updated**: November 3, 2025  
**Status**: Production-Ready  
**Version**: 1.0.0
