"""
Role-Based Access Control (RBAC) Service
Manage permissions and access control.
"""

from enum import Enum
from typing import List

from fastapi import HTTPException, status

from app.models.user import User


class Role(str, Enum):
    """User roles in the system."""
    
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Permission(str, Enum):
    """System permissions."""
    
    # Data Source Management
    CREATE_DATASOURCE = "create_datasource"
    EDIT_DATASOURCE = "edit_datasource"
    DELETE_DATASOURCE = "delete_datasource"
    VIEW_DATASOURCE = "view_datasource"
    TEST_DATASOURCE = "test_datasource"
    
    # Query Operations
    EXECUTE_QUERY = "execute_query"
    VIEW_QUERY_HISTORY = "view_query_history"
    EXPORT_DATA = "export_data"
    
    # User Management
    MANAGE_USERS = "manage_users"
    VIEW_ANALYTICS = "view_analytics"


# Role → Permissions mapping
ROLE_PERMISSIONS: dict[Role, List[Permission]] = {
    Role.ADMIN: [
        # All permissions
        Permission.CREATE_DATASOURCE,
        Permission.EDIT_DATASOURCE,
        Permission.DELETE_DATASOURCE,
        Permission.VIEW_DATASOURCE,
        Permission.TEST_DATASOURCE,
        Permission.EXECUTE_QUERY,
        Permission.VIEW_QUERY_HISTORY,
        Permission.EXPORT_DATA,
        Permission.MANAGE_USERS,
        Permission.VIEW_ANALYTICS,
    ],
    Role.ANALYST: [
        # Query and view, but no datasource management
        Permission.VIEW_DATASOURCE,
        Permission.EXECUTE_QUERY,
        Permission.VIEW_QUERY_HISTORY,
        Permission.EXPORT_DATA,
    ],
    Role.VIEWER: [
        # Read-only access
        Permission.VIEW_DATASOURCE,
        Permission.EXECUTE_QUERY,
        Permission.VIEW_QUERY_HISTORY,
    ],
}


class RBACService:
    """Service for role-based access control."""
    
    @staticmethod
    def has_permission(user: User, permission: Permission) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user: User to check
            permission: Permission to check
            
        Returns:
            True if user has permission
        """
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # Get user's role
        try:
            role = Role(user.role)
        except ValueError:
            # Invalid role
            return False
        
        # Check if role has permission
        return permission in ROLE_PERMISSIONS.get(role, [])
    
    @staticmethod
    def require_permission(user: User, permission: Permission) -> None:
        """
        Require user to have permission, raise exception if not.
        
        Args:
            user: User to check
            permission: Required permission
            
        Raises:
            HTTPException: If user doesn't have permission
        """
        if not RBACService.has_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value}",
            )
    
    @staticmethod
    def require_role(user: User, required_role: Role) -> None:
        """
        Require user to have specific role, raise exception if not.
        
        Args:
            user: User to check
            required_role: Required role
            
        Raises:
            HTTPException: If user doesn't have role
        """
        if user.is_superuser:
            return  # Superusers bypass role checks
        
        try:
            user_role = Role(user.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role",
            )
        
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {required_role.value}",
            )
    
    @staticmethod
    def is_admin(user: User) -> bool:
        """Check if user is an admin."""
        return user.is_superuser or user.role == Role.ADMIN.value


# Global instance
rbac_service = RBACService()














