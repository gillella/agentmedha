"""
Database Connection Endpoints
Manage organization-wide data sources (admin) and query accessible sources (users).
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db
from app.core.logging import logger
from app.models.database import DatabaseConnection
from app.models.user import User
from app.schemas.database import (
    DatabaseConnectionCreate,
    DatabaseConnectionResponse,
    DatabaseTestResponse,
)
from app.services.auth import get_current_admin, get_current_user
from app.services.database_connector import DatabaseConnectorFactory
from app.services.encryption import encryption_service

router = APIRouter()


# ============================================================================
# ADMIN ENDPOINTS - Data Source Management
# ============================================================================

@router.post(
    "",
    response_model=DatabaseConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Data Source (Admin Only)",
)
async def create_database_connection(
    connection_data: DatabaseConnectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),  # Admin only
):
    """
    Create a new data source (admin only).
    
    Admin can configure organization-wide data sources that users can discover and query.
    
    - Encrypts connection string before storing
    - Can be shared across organization
    - Access control via roles and specific users
    """
    logger.info(
        "database.create",
        user_id=current_user.id,
        database_type=connection_data.database_type,
        is_shared=connection_data.is_shared,
    )
    
    # Encrypt connection string
    encrypted_connection_string = encryption_service.encrypt(
        connection_data.connection_string
    )
    
    # Create new connection
    db_connection = DatabaseConnection(
        created_by=current_user.id,
        name=connection_data.name,
        display_name=connection_data.display_name,
        description=connection_data.description,
        keywords=connection_data.keywords,
        database_type=connection_data.database_type,
        connection_string=encrypted_connection_string,
        is_shared=connection_data.is_shared,
        access_level=connection_data.access_level,
        allowed_roles=connection_data.allowed_roles,
        allowed_users=connection_data.allowed_users,
        is_active=True,
        connection_status="untested",
    )
    
    db.add(db_connection)
    await db.commit()
    await db.refresh(db_connection)
    
    logger.info(
        "database.created",
        database_id=db_connection.id,
        user_id=current_user.id,
    )
    
    return db_connection


@router.put(
    "/{connection_id}",
    response_model=DatabaseConnectionResponse,
    summary="Update Data Source (Admin Only)",
)
async def update_database_connection(
    connection_id: int,
    connection_data: DatabaseConnectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),  # Admin only
):
    """
    Update a data source (admin only).
    """
    result = await db.execute(
        select(DatabaseConnection)
        .where(DatabaseConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found",
        )
    
    # Update fields
    connection.name = connection_data.name
    connection.display_name = connection_data.display_name
    connection.description = connection_data.description
    connection.keywords = connection_data.keywords
    connection.database_type = connection_data.database_type
    connection.is_shared = connection_data.is_shared
    connection.access_level = connection_data.access_level
    connection.allowed_roles = connection_data.allowed_roles
    connection.allowed_users = connection_data.allowed_users
    
    # Re-encrypt connection string if changed
    if connection_data.connection_string:
        connection.connection_string = encryption_service.encrypt(
            connection_data.connection_string
        )
        # Reset connection status when credentials change
        connection.connection_status = "untested"
    
    await db.commit()
    await db.refresh(connection)
    
    logger.info(
        "database.updated",
        database_id=connection_id,
        user_id=current_user.id,
    )
    
    return connection


@router.delete(
    "/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Data Source (Admin Only)",
)
async def delete_database_connection(
    connection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),  # Admin only
):
    """
    Delete a data source (admin only, soft delete).
    """
    result = await db.execute(
        select(DatabaseConnection)
        .where(DatabaseConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found",
        )
    
    # Soft delete
    connection.is_active = False
    await db.commit()
    
    logger.info(
        "database.deleted",
        database_id=connection_id,
        user_id=current_user.id,
    )
    
    return None


# ============================================================================
# USER ENDPOINTS - Data Source Discovery & Access
# ============================================================================

@router.get(
    "",
    response_model=List[DatabaseConnectionResponse],
    summary="List Accessible Data Sources",
)
async def list_database_connections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all data sources accessible to the current user.
    
    Returns data sources based on:
    - User is the creator
    - Data source is shared and public
    - Data source is shared and user's role is allowed
    - Data source is shared and user is specifically allowed
    """
    # Get all active data sources
    result = await db.execute(
        select(DatabaseConnection)
        .where(DatabaseConnection.is_active == True)
        .order_by(DatabaseConnection.created_at.desc())
    )
    all_connections = result.scalars().all()
    
    # Filter by access
    accessible_connections = [
        conn for conn in all_connections
        if conn.is_accessible_by(current_user)
    ]
    
    logger.info(
        "database.list",
        user_id=current_user.id,
        count=len(accessible_connections),
    )
    
    return accessible_connections


@router.get(
    "/{connection_id}",
    response_model=DatabaseConnectionResponse,
    summary="Get Data Source Details",
)
async def get_database_connection(
    connection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific data source (if user has access).
    """
    result = await db.execute(
        select(DatabaseConnection)
        .where(DatabaseConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found",
        )
    
    # Check access
    if not connection.is_accessible_by(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this data source",
        )
    
    return connection


# ============================================================================
# SHARED ENDPOINTS - Test, Schema, Sample Data
# ============================================================================

@router.post(
    "/{connection_id}/test",
    response_model=DatabaseTestResponse,
    summary="Test Data Source Connection",
)
async def test_database_connection(
    connection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Test a data source connection.
    
    - Attempts to connect to the database
    - Retrieves basic schema information
    - Updates connection status
    
    Accessible to:
    - Admin (creator)
    - Users with access to the data source
    """
    result = await db.execute(
        select(DatabaseConnection)
        .where(DatabaseConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found",
        )
    
    # Check access (admins can test any, users can test accessible)
    is_admin = current_user.is_superuser or current_user.role == "admin"
    if not is_admin and not connection.is_accessible_by(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this data source",
        )
    
    try:
        # Decrypt connection string
        connection_string = encryption_service.decrypt(connection.connection_string)
        
        # Get appropriate connector
        connector = get_connector(
            db_type=connection.database_type,
            connection_string=connection_string,
        )
        
        # Test connection by getting table names
        table_names = await connector.get_table_names()
        
        # Update connection status
        from datetime import datetime
        connection.connection_status = "healthy"
        connection.last_tested = datetime.utcnow().isoformat()
        await db.commit()
        
        logger.info(
            "database.test_success",
            database_id=connection_id,
            table_count=len(table_names),
        )
        
        return DatabaseTestResponse(
            success=True,
            message=f"Connection successful! Found {len(table_names)} tables.",
            schema_info={"table_count": len(table_names), "tables": table_names[:10]},
        )
        
    except Exception as e:
        # Update connection status
        from datetime import datetime
        connection.connection_status = "unhealthy"
        connection.last_tested = datetime.utcnow().isoformat()
        await db.commit()
        
        logger.error(
            "database.test_failed",
            database_id=connection_id,
            error=str(e),
        )
        
        return DatabaseTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}",
        )


@router.get(
    "/{connection_id}/schema",
    summary="Get Database Schema",
)
async def get_database_schema(
    connection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get database schema (tables, columns, relationships).
    
    Only accessible to users who have access to this data source.
    """
    result = await db.execute(
        select(DatabaseConnection)
        .where(DatabaseConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found",
        )
    
    # Check access
    if not connection.is_accessible_by(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this data source",
        )
    
    try:
        # Decrypt connection string
        connection_string = encryption_service.decrypt(connection.connection_string)
        
        # Get appropriate connector
        connector = get_connector(
            db_type=connection.database_type,
            connection_string=connection_string,
        )
        
        # Get schema
        schema = await connector.get_schema()
        
        logger.info(
            "database.schema_retrieved",
            database_id=connection_id,
            table_count=len(schema.get("tables", [])),
        )
        
        return schema
        
    except Exception as e:
        logger.error(
            "database.schema_failed",
            database_id=connection_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve schema: {str(e)}",
        )


@router.get(
    "/{connection_id}/tables/{table_name}/sample",
    summary="Get Table Sample Data",
)
async def get_table_sample(
    connection_id: int,
    table_name: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get sample data from a table.
    
    Only accessible to users who have access to this data source.
    """
    result = await db.execute(
        select(DatabaseConnection)
        .where(DatabaseConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found",
        )
    
    # Check access
    if not connection.is_accessible_by(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this data source",
        )
    
    try:
        # Decrypt connection string
        connection_string = encryption_service.decrypt(connection.connection_string)
        
        # Get appropriate connector
        connector = get_connector(
            db_type=connection.database_type,
            connection_string=connection_string,
        )
        
        # Execute sample query
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        result = await connector.execute_query(query)
        
        logger.info(
            "database.sample_retrieved",
            database_id=connection_id,
            table=table_name,
        )
        
        return {
            "table": table_name,
            "rows": result.get("rows", []),
            "columns": result.get("columns", []),
        }
        
    except Exception as e:
        logger.error(
            "database.sample_failed",
            database_id=connection_id,
            table=table_name,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sample data: {str(e)}",
        )
