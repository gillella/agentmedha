"""
Database Connection Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DatabaseConnectionCreate(BaseModel):
    """Schema for creating/updating a database connection."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Internal name")
    display_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Friendly name shown to users"
    )
    description: Optional[str] = Field(None, description="Description of the data source")
    keywords: Optional[List[str]] = Field(
        None,
        description="Keywords for discovery (e.g., ['sales', 'revenue', 'customers'])"
    )
    database_type: str = Field(..., pattern="^(postgresql|mysql|snowflake|bigquery)$")
    connection_string: str = Field(..., min_length=1, description="Connection string (will be encrypted)")
    
    # Sharing and access control
    is_shared: bool = Field(
        default=False,
        description="True = organization-wide, False = personal"
    )
    access_level: str = Field(
        default="public",
        pattern="^(public|restricted|private)$",
        description="public = all users, restricted = specific roles/users, private = creator only"
    )
    allowed_roles: Optional[List[str]] = Field(
        None,
        description="Roles that can access (e.g., ['analyst', 'manager'])"
    )
    allowed_users: Optional[List[int]] = Field(
        None,
        description="Specific user IDs that can access"
    )


class DatabaseConnectionResponse(BaseModel):
    """Schema for database connection response."""
    
    id: int
    created_by: int
    name: str
    display_name: Optional[str]
    description: Optional[str]
    keywords: Optional[List[str]]
    database_type: str
    
    # Sharing and access
    is_shared: bool
    access_level: str
    allowed_roles: Optional[List[str]]
    allowed_users: Optional[List[int]]
    
    # Status
    connection_status: str
    is_active: bool
    last_tested: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DatabaseTestResponse(BaseModel):
    """Schema for database connection test result."""
    
    success: bool
    message: str
    schema_info: Optional[Dict[str, Any]] = None
