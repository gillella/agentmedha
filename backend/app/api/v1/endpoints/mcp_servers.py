"""
MCP Server API Endpoints

Admin endpoints for managing MCP servers.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import structlog

from app.models.base import get_db
from app.services.auth import get_current_admin
from app.models.user import User
from app.services.mcp_manager import get_mcp_manager, MCPServerConfig
from app.models.mcp import MCPServer, MCPResource

logger = structlog.get_logger()

router = APIRouter()


# Request/Response Schemas

class MCPServerCreate(BaseModel):
    """Request to create a new MCP server"""
    name: str = Field(..., description="Server name")
    description: Optional[str] = Field(None, description="Server description")
    server_type: str = Field(..., description="Server type (github, postgres, filesystem, etc.)")
    config: Dict[str, Any] = Field(..., description="Server-specific configuration")


class MCPServerUpdate(BaseModel):
    """Request to update an MCP server"""
    name: Optional[str] = Field(None, description="Server name")
    description: Optional[str] = Field(None, description="Server description")
    config: Optional[Dict[str, Any]] = Field(None, description="Server configuration")
    status: Optional[str] = Field(None, description="Server status")


class MCPServerResponse(BaseModel):
    """MCP server response"""
    id: str
    name: str
    description: Optional[str]
    server_type: str
    config: Dict[str, Any]  # Sensitive fields masked
    status: str
    last_connected_at: Optional[str]
    error_message: Optional[str]
    created_by: Optional[str]
    created_at: str
    updated_at: str
    resource_count: int


class MCPResourceResponse(BaseModel):
    """MCP resource response"""
    id: str
    server_id: str
    resource_uri: str
    resource_type: Optional[str]
    name: Optional[str]
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    last_synced_at: Optional[str]


class ConnectionTestResponse(BaseModel):
    """Connection test result"""
    success: bool
    server_id: str
    message: Optional[str] = None
    error: Optional[str] = None


# API Endpoints

@router.post("/servers", response_model=MCPServerResponse, status_code=status.HTTP_201_CREATED)
async def create_mcp_server(
    server_data: MCPServerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Register a new MCP server (Admin only).
    
    Creates a new MCP server configuration that can be used to connect
    to external data sources.
    """
    try:
        logger.info("mcp.create_server", name=server_data.name, type=server_data.server_type)
        
        # Create server configuration
        config = MCPServerConfig(
            name=server_data.name,
            server_type=server_data.server_type,
            config=server_data.config,
            description=server_data.description
        )
        
        # Register server
        manager = get_mcp_manager()
        server_id = await manager.register_server(
            db=db,
            config=config,
            user_id=str(current_user.id)
        )
        
        # Get created server
        server = await manager.get_server(db, server_id)
        
        return MCPServerResponse(**server.to_dict_safe())
        
    except ValueError as e:
        logger.error("mcp.create_server_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("mcp.create_server_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create server: {str(e)}"
        )


@router.get("/servers", response_model=List[MCPServerResponse])
async def list_mcp_servers(
    server_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    List all MCP servers (Admin only).
    
    Returns all configured MCP servers, optionally filtered by type or status.
    """
    try:
        from sqlalchemy import select, func
        from app.models.mcp import MCPResource
        
        manager = get_mcp_manager()
        servers = await manager.list_servers(
            db=db,
            server_type=server_type,
            status=status_filter
        )
        
        # Calculate resource counts for each server
        result = []
        for server in servers:
            server_dict = server.to_dict_safe()
            
            # Query resource count
            stmt = select(func.count()).select_from(MCPResource).where(MCPResource.server_id == server.id)
            count_result = await db.execute(stmt)
            resource_count = count_result.scalar() or 0
            
            server_dict['resource_count'] = resource_count
            result.append(MCPServerResponse(**server_dict))
        
        return result
        
    except Exception as e:
        logger.error("mcp.list_servers_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list servers: {str(e)}"
        )


@router.get("/servers/{server_id}", response_model=MCPServerResponse)
def get_mcp_server(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get MCP server details (Admin only).
    """
    manager = get_mcp_manager()
    server = manager.get_server(db, server_id)
    
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server {server_id} not found"
        )
    
    return MCPServerResponse(**server.to_dict_safe())


@router.put("/servers/{server_id}", response_model=MCPServerResponse)
async def update_mcp_server(
    server_id: str,
    updates: MCPServerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Update MCP server configuration (Admin only).
    """
    try:
        manager = get_mcp_manager()
        
        # Convert to dict, excluding None values
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        
        server = await manager.update_server(db, server_id, update_dict)
        
        return MCPServerResponse(**server.to_dict_safe())
        
    except ValueError as e:
        logger.error("mcp.update_server_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e) else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("mcp.update_server_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update server: {str(e)}"
        )


@router.delete("/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mcp_server(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Delete an MCP server (Admin only).
    
    This will also delete all associated resources and disconnect if active.
    """
    manager = get_mcp_manager()
    deleted = manager.delete_server(db, server_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server {server_id} not found"
        )
    
    return None


@router.post("/servers/{server_id}/test", response_model=ConnectionTestResponse)
async def test_server_connection(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Test connection to an MCP server (Admin only).
    
    Validates that the server configuration is correct and the server is reachable.
    """
    manager = get_mcp_manager()
    result = await manager.test_connection(db, server_id)
    
    return ConnectionTestResponse(**result)


@router.post("/servers/{server_id}/connect")
def connect_to_server(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Connect to an MCP server (Admin only).
    
    Establishes an active connection to the server.
    """
    manager = get_mcp_manager()
    
    # Verify server exists
    server = manager.get_server(db, server_id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server {server_id} not found"
        )
    
    success = manager.connect_server(server_id)
    
    if success:
        server.status = 'active'
        db.commit()
    
    return {
        "success": success,
        "server_id": server_id,
        "message": "Connected successfully" if success else "Connection failed"
    }


@router.post("/servers/{server_id}/disconnect")
def disconnect_from_server(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Disconnect from an MCP server (Admin only).
    """
    manager = get_mcp_manager()
    success = manager.disconnect_server(server_id)
    
    if success:
        server = manager.get_server(db, server_id)
        if server:
            server.status = 'inactive'
            db.commit()
    
    return {
        "success": success,
        "server_id": server_id,
        "message": "Disconnected successfully"
    }


@router.get("/servers/{server_id}/resources", response_model=List[MCPResourceResponse])
async def list_server_resources(
    server_id: str,
    refresh: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    List resources available from an MCP server (Admin only).
    
    Args:
        server_id: Server to query
        refresh: If True, refresh from server (otherwise use cached)
    """
    manager = get_mcp_manager()
    
    # Verify server exists
    server = await manager.get_server(db, server_id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server {server_id} not found"
        )
    
    resources = await manager.list_resources(db, server_id, refresh=refresh)
    
    return [MCPResourceResponse(**r.to_dict()) for r in resources]


@router.get("/server-types")
def get_supported_server_types(
    current_user: User = Depends(get_current_admin)
):
    """
    Get list of supported MCP server types (Admin only).
    
    Returns configuration requirements for each type.
    """
    return {
        "server_types": [
            {
                "type": "github",
                "name": "GitHub",
                "description": "Connect to GitHub repositories",
                "required_fields": ["token"],
                "optional_fields": ["owner", "repo"],
                "icon": "github"
            },
            {
                "type": "postgres",
                "name": "PostgreSQL",
                "description": "Connect to PostgreSQL databases",
                "required_fields": ["host", "port", "database", "username", "password"],
                "optional_fields": ["schema"],
                "icon": "database"
            },
            {
                "type": "filesystem",
                "name": "Filesystem",
                "description": "Access local or mounted filesystems",
                "required_fields": ["path"],
                "optional_fields": ["allowed_extensions"],
                "icon": "folder"
            },
            {
                "type": "sqlite",
                "name": "SQLite",
                "description": "Connect to SQLite databases",
                "required_fields": ["database_path"],
                "optional_fields": [],
                "icon": "database"
            }
        ]
    }

