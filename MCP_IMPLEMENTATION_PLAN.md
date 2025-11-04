# 🔌 MCP Server Implementation Plan for AgentMedha

## Overview

Admin connects various data sources through MCP servers, making them available to AgentMedha for data operations.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentMedha Admin UI                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   GitHub     │  │  PostgreSQL  │  │   Filesystem │     │
│  │ MCP Server   │  │  MCP Server  │  │  MCP Server  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                  ┌──────────────────────┐
                  │  MCP Server Manager  │
                  │   (Backend Service)   │
                  └──────────┬───────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
    ┌─────────┐        ┌─────────┐      ┌─────────┐
    │ GitHub  │        │Postgres │      │  File   │
    │   API   │        │Database │      │ System  │
    └─────────┘        └─────────┘      └─────────┘
```

---

## 📊 Database Schema

### 1. MCP Servers Table

```sql
CREATE TABLE mcp_servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    server_type VARCHAR(100) NOT NULL,  -- 'github', 'postgres', 'filesystem', etc.
    
    -- Connection Details
    config JSONB NOT NULL,  -- Server-specific configuration
    
    -- Status
    status VARCHAR(50) DEFAULT 'inactive',  -- 'active', 'inactive', 'error'
    last_connected_at TIMESTAMP,
    error_message TEXT,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Organization (if multi-tenant)
    organization_id UUID,
    
    UNIQUE(name, organization_id)
);
```

### 2. MCP Resources Table (What's available from each server)

```sql
CREATE TABLE mcp_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID REFERENCES mcp_servers(id) ON DELETE CASCADE,
    
    -- Resource Identity
    resource_uri VARCHAR(500) NOT NULL,
    resource_type VARCHAR(100),  -- 'file', 'table', 'repository', etc.
    name VARCHAR(255),
    description TEXT,
    
    -- Resource Metadata
    metadata JSONB,
    
    -- Caching
    last_synced_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(server_id, resource_uri)
);
```

### 3. MCP Server Access Log

```sql
CREATE TABLE mcp_access_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID REFERENCES mcp_servers(id),
    user_id UUID REFERENCES users(id),
    
    operation VARCHAR(100),  -- 'read', 'write', 'list', etc.
    resource_uri VARCHAR(500),
    
    status VARCHAR(50),  -- 'success', 'error'
    duration_ms INTEGER,
    error_message TEXT,
    
    timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## 🔧 Backend Implementation

### 1. MCP Server Manager Service

```python
# backend/app/services/mcp_manager.py

from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import structlog

logger = structlog.get_logger()


class MCPServerConfig:
    """Configuration for an MCP server"""
    def __init__(
        self,
        name: str,
        server_type: str,
        config: Dict[str, Any],
        organization_id: Optional[str] = None
    ):
        self.name = name
        self.server_type = server_type
        self.config = config
        self.organization_id = organization_id


class MCPServerManager:
    """
    Manages MCP server connections and operations.
    
    Responsibilities:
    - Register/unregister MCP servers
    - Connect/disconnect from servers
    - List available resources
    - Execute operations through MCP servers
    - Cache resource metadata
    """
    
    def __init__(self):
        self.active_servers: Dict[str, Any] = {}  # server_id -> MCP client
        
    async def register_server(
        self,
        db: Session,
        config: MCPServerConfig,
        user_id: str
    ) -> str:
        """
        Register a new MCP server.
        
        Steps:
        1. Validate configuration
        2. Test connection
        3. Store in database
        4. Discover resources
        5. Return server ID
        """
        logger.info("mcp.register", name=config.name, type=config.server_type)
        
        # TODO: Validate config based on server_type
        
        # Test connection
        is_valid = await self._test_connection(config)
        if not is_valid:
            raise ValueError("Cannot connect to MCP server")
        
        # Store in database
        server = MCPServer(
            name=config.name,
            server_type=config.server_type,
            config=config.config,
            created_by=user_id,
            organization_id=config.organization_id,
            status='active',
            last_connected_at=datetime.utcnow()
        )
        db.add(server)
        db.commit()
        
        # Discover resources (async)
        asyncio.create_task(self._discover_resources(server.id, config))
        
        return str(server.id)
    
    async def connect_server(self, server_id: str) -> bool:
        """
        Connect to an MCP server and make it active.
        """
        if server_id in self.active_servers:
            logger.info("mcp.already_connected", server_id=server_id)
            return True
        
        # TODO: Load config from DB and establish connection
        # TODO: Store active connection
        
        logger.info("mcp.connected", server_id=server_id)
        return True
    
    async def disconnect_server(self, server_id: str) -> bool:
        """
        Disconnect from an MCP server.
        """
        if server_id not in self.active_servers:
            return True
        
        # TODO: Close connection gracefully
        del self.active_servers[server_id]
        
        logger.info("mcp.disconnected", server_id=server_id)
        return True
    
    async def list_resources(
        self,
        server_id: str,
        refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all resources available from an MCP server.
        
        Args:
            server_id: Server to query
            refresh: Force refresh from server (vs cached)
        """
        logger.info("mcp.list_resources", server_id=server_id, refresh=refresh)
        
        # TODO: If refresh, query MCP server directly
        # TODO: Otherwise, return from cache (mcp_resources table)
        
        return []
    
    async def execute_operation(
        self,
        server_id: str,
        resource_uri: str,
        operation: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Execute an operation through an MCP server.
        
        Examples:
        - Read a file
        - Query a database
        - Fetch GitHub issues
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(
                "mcp.execute",
                server_id=server_id,
                operation=operation,
                resource=resource_uri
            )
            
            # TODO: Get active server connection
            # TODO: Execute operation through MCP
            # TODO: Return result
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Log success
            await self._log_access(
                server_id=server_id,
                operation=operation,
                resource_uri=resource_uri,
                status='success',
                duration_ms=int(duration_ms)
            )
            
            return {"status": "success"}
            
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Log error
            await self._log_access(
                server_id=server_id,
                operation=operation,
                resource_uri=resource_uri,
                status='error',
                duration_ms=int(duration_ms),
                error_message=str(e)
            )
            
            raise
    
    async def _test_connection(self, config: MCPServerConfig) -> bool:
        """Test if we can connect to the MCP server"""
        # TODO: Implement per server type
        return True
    
    async def _discover_resources(
        self,
        server_id: str,
        config: MCPServerConfig
    ):
        """Discover and cache available resources"""
        # TODO: Query MCP server for available resources
        # TODO: Store in mcp_resources table
        pass
    
    async def _log_access(
        self,
        server_id: str,
        operation: str,
        resource_uri: str,
        status: str,
        duration_ms: int,
        error_message: Optional[str] = None
    ):
        """Log MCP server access"""
        # TODO: Store in mcp_access_log table
        pass


# Singleton instance
mcp_manager = MCPServerManager()
```

---

## 🎨 Frontend - Admin MCP Server Management

### 1. MCP Servers Page

```typescript
// frontend/src/pages/MCPServersPage.tsx

interface MCPServer {
  id: string;
  name: string;
  serverType: string;
  status: 'active' | 'inactive' | 'error';
  lastConnected: string;
  resourceCount: number;
}

export default function MCPServersPage() {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  
  return (
    <div>
      <h1>MCP Servers</h1>
      
      {/* Server Cards */}
      <div className="grid grid-cols-3 gap-4">
        {servers.map(server => (
          <ServerCard key={server.id} server={server} />
        ))}
        
        {/* Add New Server Card */}
        <AddServerCard onClick={() => setShowAddModal(true)} />
      </div>
      
      {/* Add Server Modal */}
      {showAddModal && (
        <AddMCPServerModal
          onClose={() => setShowAddModal(false)}
          onAdd={(config) => addServer(config)}
        />
      )}
    </div>
  );
}
```

### 2. Add MCP Server Modal

```typescript
// Support different server types with specific configs

const SERVER_TYPES = {
  github: {
    name: 'GitHub',
    icon: GithubIcon,
    fields: [
      { name: 'token', label: 'Personal Access Token', type: 'password' },
      { name: 'owner', label: 'Repository Owner', type: 'text' },
      { name: 'repo', label: 'Repository Name', type: 'text' }
    ]
  },
  postgres: {
    name: 'PostgreSQL',
    icon: DatabaseIcon,
    fields: [
      { name: 'host', label: 'Host', type: 'text' },
      { name: 'port', label: 'Port', type: 'number', default: 5432 },
      { name: 'database', label: 'Database', type: 'text' },
      { name: 'username', label: 'Username', type: 'text' },
      { name: 'password', label: 'Password', type: 'password' }
    ]
  },
  filesystem: {
    name: 'Filesystem',
    icon: FolderIcon,
    fields: [
      { name: 'path', label: 'Base Path', type: 'text' },
      { name: 'allowedExtensions', label: 'Allowed Extensions', type: 'text', 
        placeholder: '.txt,.md,.json' }
    ]
  }
};
```

---

## 🚀 Implementation Phases

### **Phase 1: Foundation (Week 1-2)**

#### Backend
- [ ] Create database migrations for MCP tables
- [ ] Implement `MCPServerManager` service skeleton
- [ ] Create MCP server CRUD endpoints
- [ ] Add connection testing functionality

#### Frontend
- [ ] Create MCP Servers management page
- [ ] Build "Add Server" modal with server type selection
- [ ] Display server cards with status indicators
- [ ] Add server connection testing UI

**Deliverable**: Admins can add/remove MCP server configs (no actual MCP connection yet)

---

### **Phase 2: MCP Integration (Week 3-4)**

#### Backend
- [ ] Integrate actual MCP client library
- [ ] Implement GitHub MCP server connector
- [ ] Implement PostgreSQL MCP server connector
- [ ] Add resource discovery functionality
- [ ] Cache discovered resources

#### Frontend
- [ ] Display available resources per server
- [ ] Add resource browser interface
- [ ] Show resource metadata and preview
- [ ] Add search/filter for resources

**Deliverable**: Real MCP connections working, resources discoverable

---

### **Phase 3: Agent Integration (Week 5-6)**

#### Backend
- [ ] Expose MCP resources to AI agents
- [ ] Create agent tools for MCP operations
- [ ] Implement operation execution through MCP
- [ ] Add permission/access control

#### Frontend
- [ ] Show which resources are available to agents
- [ ] Add resource selection for queries
- [ ] Display MCP operation logs
- [ ] Add resource usage analytics

**Deliverable**: AgentMedha can use MCP servers for data operations

---

### **Phase 4: Advanced Features (Week 7-8)**

- [ ] Resource embeddings for semantic search
- [ ] Smart resource recommendations
- [ ] Multi-server query orchestration
- [ ] Caching and performance optimization
- [ ] Monitoring and alerting

---

## 💡 Key Design Decisions

### 1. **Why MCP?**
- **Standardized**: Industry standard by Anthropic
- **Extensible**: Easy to add new data sources
- **Secure**: Built-in security patterns
- **Composable**: Can combine multiple sources

### 2. **Server Types Priority**
1. **PostgreSQL** - Most common for AgentMedha use case
2. **GitHub** - Code/documentation access
3. **Filesystem** - File-based data
4. **Custom** - Extensibility for future needs

### 3. **Resource Discovery Strategy**
- **Lazy Loading**: Discover on first connection
- **Background Refresh**: Periodic updates
- **On-Demand**: Manual refresh when needed
- **Caching**: Store metadata locally

### 4. **Security**
- Credentials encrypted at rest
- Admin-only server management
- Resource-level permissions
- Audit logging for all operations

---

## 📝 API Endpoints

```
POST   /api/v1/mcp/servers              # Register new server
GET    /api/v1/mcp/servers              # List all servers
GET    /api/v1/mcp/servers/:id          # Get server details
PUT    /api/v1/mcp/servers/:id          # Update server config
DELETE /api/v1/mcp/servers/:id          # Remove server
POST   /api/v1/mcp/servers/:id/test     # Test connection
POST   /api/v1/mcp/servers/:id/connect  # Activate server
POST   /api/v1/mcp/servers/:id/disconnect # Deactivate server

GET    /api/v1/mcp/servers/:id/resources         # List resources
POST   /api/v1/mcp/servers/:id/resources/refresh # Refresh resources
GET    /api/v1/mcp/servers/:id/resources/:uri    # Get resource details
POST   /api/v1/mcp/servers/:id/execute           # Execute operation

GET    /api/v1/mcp/access-logs          # Access audit logs
GET    /api/v1/mcp/stats                # Usage statistics
```

---

## 🧪 Testing Strategy

### Unit Tests
- MCP server configuration validation
- Connection testing logic
- Resource discovery parsing
- Operation execution

### Integration Tests
- End-to-end server registration
- Actual MCP connection (with test servers)
- Resource fetching and caching
- Operation execution flow

### UI Tests
- Server addition workflow
- Resource browsing
- Connection status updates
- Error handling

---

## 📊 Success Metrics

- **Server Setup Time**: < 2 minutes to add new server
- **Resource Discovery**: < 30 seconds for typical server
- **Operation Latency**: < 500ms for cached operations
- **Error Rate**: < 1% for established connections
- **Admin Satisfaction**: Can manage all data sources from one place

---

## 🎯 Next Steps

1. **Review this plan** with the team
2. **Set up development environment** for MCP testing
3. **Create Phase 1 tasks** in project management tool
4. **Start with database schema** (easiest first step)
5. **Build basic UI mockups** for feedback

---

## 📚 References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Example MCP Servers](https://github.com/modelcontextprotocol/servers)

