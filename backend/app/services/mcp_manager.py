"""
MCP Server Manager Service

Manages MCP (Model Context Protocol) server connections and operations.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
import uuid

from app.models.mcp import MCPServer, MCPResource, MCPAccessLog
from app.services.mcp_connectors import get_connector

logger = structlog.get_logger()


class MCPServerConfig:
    """Configuration for an MCP server"""
    
    def __init__(
        self,
        name: str,
        server_type: str,
        config: Dict[str, Any],
        description: Optional[str] = None,
        organization_id: Optional[str] = None
    ):
        self.name = name
        self.server_type = server_type
        self.config = config
        self.description = description
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
        logger.info("mcp_manager.initialized")
    
    async def register_server(
        self,
        db: AsyncSession,
        config: MCPServerConfig,
        user_id: str
    ) -> str:
        """
        Register a new MCP server.
        
        Args:
            db: Database session
            config: Server configuration
            user_id: User registering the server
            
        Returns:
            Server ID
            
        Raises:
            ValueError: If server name already exists or config is invalid
        """
        logger.info("mcp.register", name=config.name, type=config.server_type)
        
        # Check if server name already exists
        stmt = select(MCPServer).where(
            MCPServer.name == config.name,
            MCPServer.organization_id == config.organization_id
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError(f"Server with name '{config.name}' already exists")
        
        # Validate configuration
        self._validate_config(config.server_type, config.config)
        
        # Create server record
        # Note: created_by is None for now as User.id is int but MCPServer expects UUID
        # TODO: Update User model to use UUID or MCPServer to use int
        server = MCPServer(
            name=config.name,
            description=config.description,
            server_type=config.server_type,
            config=config.config,
            created_by=None,
            organization_id=uuid.UUID(config.organization_id) if config.organization_id else None,
            status='inactive'
        )
        
        db.add(server)
        await db.commit()
        await db.refresh(server)
        
        logger.info("mcp.registered", server_id=str(server.id), name=config.name)
        
        return str(server.id)
    
    async def get_server(self, db: AsyncSession, server_id: str) -> Optional[MCPServer]:
        """Get server by ID"""
        try:
            server_uuid = uuid.UUID(server_id)
            stmt = select(MCPServer).where(MCPServer.id == server_uuid)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except (ValueError, AttributeError):
            return None
    
    async def list_servers(
        self,
        db: AsyncSession,
        organization_id: Optional[str] = None,
        server_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[MCPServer]:
        """
        List all MCP servers with optional filtering.
        
        Args:
            db: Database session
            organization_id: Filter by organization
            server_type: Filter by server type
            status: Filter by status
            
        Returns:
            List of servers
        """
        stmt = select(MCPServer)
        
        if organization_id:
            stmt = stmt.where(MCPServer.organization_id == uuid.UUID(organization_id))
        
        if server_type:
            stmt = stmt.where(MCPServer.server_type == server_type)
        
        if status:
            stmt = stmt.where(MCPServer.status == status)
        
        stmt = stmt.order_by(MCPServer.created_at.desc())
        result = await db.execute(stmt)
        servers = result.scalars().all()
        
        logger.info("mcp.list_servers", count=len(servers))
        return servers
    
    async def update_server(
        self,
        db: AsyncSession,
        server_id: str,
        updates: Dict[str, Any]
    ) -> MCPServer:
        """
        Update server configuration.
        
        Args:
            db: Database session
            server_id: Server to update
            updates: Fields to update
            
        Returns:
            Updated server
            
        Raises:
            ValueError: If server not found or invalid updates
        """
        server = await self.get_server(db, server_id)
        if not server:
            raise ValueError(f"Server {server_id} not found")
        
        # Update allowed fields
        allowed_fields = ['name', 'description', 'config', 'status']
        
        for field, value in updates.items():
            if field in allowed_fields:
                if field == 'config':
                    # Validate new config
                    self._validate_config(server.server_type, value)
                setattr(server, field, value)
        
        server.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(server)
        
        logger.info("mcp.updated", server_id=server_id)
        
        return server
    
    async def delete_server(self, db: AsyncSession, server_id: str) -> bool:
        """
        Delete an MCP server.
        
        Args:
            db: Database session
            server_id: Server to delete
            
        Returns:
            True if deleted, False if not found
        """
        server = await self.get_server(db, server_id)
        if not server:
            return False
        
        # Disconnect if active
        if server_id in self.active_servers:
            self.disconnect_server(server_id)
        
        await db.delete(server)
        await db.commit()
        
        logger.info("mcp.deleted", server_id=server_id)
        
        return True
    
    async def test_connection(self, db: AsyncSession, server_id: str) -> Dict[str, Any]:
        """
        Test connection to an MCP server.
        
        Args:
            db: Database session
            server_id: Server to test
            
        Returns:
            Dict with status and details
        """
        server = await self.get_server(db, server_id)
        if not server:
            return {"success": False, "error": "Server not found"}
        
        logger.info("mcp.test_connection", server_id=server_id, type=server.server_type)
        
        try:
            # Get the appropriate connector and test connection
            connector = get_connector(server.server_type, server.config)
            result = connector.test_connection()
            
            # Update server status based on result
            if result['success']:
                server.status = 'active'
                server.last_connected_at = datetime.utcnow()
                server.error_message = None
            else:
                server.status = 'error'
                server.error_message = result.get('error', 'Connection failed')
            
            await db.commit()
            
            return {
                **result,
                "server_id": server_id,
                "server_type": server.server_type
            }
            
        except Exception as e:
            logger.error("mcp.test_connection_failed", error=str(e))
            
            server.status = 'error'
            server.error_message = str(e)
            await db.commit()
            
            return {
                "success": False,
                "server_id": server_id,
                "error": str(e),
                "message": "Connection test failed"
            }
    
    def connect_server(self, server_id: str) -> bool:
        """
        Connect to an MCP server and make it active.
        
        Note: Phase 1 skeleton - actual connection in Phase 2
        """
        if server_id in self.active_servers:
            logger.info("mcp.already_connected", server_id=server_id)
            return True
        
        # TODO: Phase 2 - Establish actual MCP connection
        # For now, just mark as connected
        self.active_servers[server_id] = {"connected_at": datetime.utcnow()}
        
        logger.info("mcp.connected", server_id=server_id)
        return True
    
    def disconnect_server(self, server_id: str) -> bool:
        """
        Disconnect from an MCP server.
        
        Note: Phase 1 skeleton - actual disconnection in Phase 2
        """
        if server_id not in self.active_servers:
            return True
        
        # TODO: Phase 2 - Close actual MCP connection
        del self.active_servers[server_id]
        
        logger.info("mcp.disconnected", server_id=server_id)
        return True
    
    async def list_resources(
        self,
        db: AsyncSession,
        server_id: str,
        refresh: bool = False
    ) -> List[MCPResource]:
        """
        List all resources available from an MCP server.
        
        Args:
            db: Database session
            server_id: Server to query
            refresh: Force refresh from server (vs cached)
            
        Returns:
            List of resources
            
        Note: Phase 1 returns cached resources only
        """
        logger.info("mcp.list_resources", server_id=server_id, refresh=refresh)
        
        server_uuid = uuid.UUID(server_id)
        
        # If refresh requested, discover resources from actual server
        if refresh:
            server = await self.get_server(db, server_id)
            if server:
                try:
                    # Get connector and discover resources
                    connector = get_connector(server.server_type, server.config)
                    discovered = connector.discover_resources()
                    
                    # Delete old resources for this server
                    stmt_delete = select(MCPResource).where(MCPResource.server_id == server_uuid)
                    result_delete = await db.execute(stmt_delete)
                    old_resources = result_delete.scalars().all()
                    for resource in old_resources:
                        await db.delete(resource)
                    
                    # Save newly discovered resources
                    for res_data in discovered:
                        resource = MCPResource(
                            server_id=server_uuid,
                            resource_uri=res_data['resource_uri'],
                            resource_type=res_data.get('resource_type'),
                            name=res_data.get('name'),
                            description=res_data.get('description'),
                            metadata=res_data.get('metadata', {}),
                            last_synced_at=datetime.utcnow()
                        )
                        db.add(resource)
                    
                    await db.commit()
                    logger.info("mcp.resources_synced", server_id=server_id, count=len(discovered))
                    
                except Exception as e:
                    logger.error("mcp.resource_sync_failed", server_id=server_id, error=str(e))
                    await db.rollback()
        
        # Return cached resources
        stmt = select(MCPResource).where(MCPResource.server_id == server_uuid)
        result = await db.execute(stmt)
        resources = result.scalars().all()
        
        return resources
    
    async def log_access(
        self,
        db: AsyncSession,
        server_id: str,
        user_id: str,
        operation: str,
        resource_uri: str,
        status: str,
        duration_ms: int,
        error_message: Optional[str] = None
    ):
        """Log MCP server access"""
        log_entry = MCPAccessLog(
            server_id=uuid.UUID(server_id) if server_id else None,
            user_id=uuid.UUID(user_id) if user_id else None,
            operation=operation,
            resource_uri=resource_uri,
            status=status,
            duration_ms=duration_ms,
            error_message=error_message
        )
        
        db.add(log_entry)
        await db.commit()
    
    def _validate_config(self, server_type: str, config: Dict[str, Any]) -> bool:
        """
        Validate server configuration based on type.
        
        Args:
            server_type: Type of server
            config: Configuration to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Required fields per server type
        required_fields = {
            'github': ['token'],
            'postgres': ['host', 'port', 'database', 'username', 'password'],
            'filesystem': ['path'],
            'sqlite': ['database_path'],
            'gmail': [],  # No required fields - uses OAuth tokens from ~/.local/share/google-auth/
        }
        
        if server_type not in required_fields:
            logger.warning("mcp.unknown_server_type", type=server_type)
            return True  # Allow unknown types for flexibility
        
        required = required_fields[server_type]
        missing = [f for f in required if f not in config or not config[f]]
        
        if missing:
            raise ValueError(f"Missing required fields for {server_type}: {', '.join(missing)}")
        
        # Gmail-specific validation
        if server_type == 'gmail':
            # Validate accounts if provided
            if 'accounts' in config and not isinstance(config['accounts'], list):
                raise ValueError("Gmail 'accounts' must be a list")
            # Set defaults if not provided
            if 'default_account' not in config:
                config['default_account'] = config.get('accounts', ['arvinda.reddy@gmail.com'])[0]
        
        return True


# Singleton instance
mcp_manager = MCPServerManager()


def get_mcp_manager() -> MCPServerManager:
    """Get MCP manager singleton"""
    return mcp_manager

