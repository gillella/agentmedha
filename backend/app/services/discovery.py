"""
Discovery Service

Wraps the discovery agent for use in the query orchestrator.
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.discovery_agent import discovery_agent
from app.models.database import DatabaseConnection


class DiscoveryService:
    """Service for data source discovery"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def discover_data_sources(
        self,
        query: str,
        user_id: int,
        limit: int = 5
    ) -> List[DatabaseConnection]:
        """
        Discover data sources relevant to the query.
        
        Args:
            query: Search query
            user_id: User ID for access control
            limit: Max results
            
        Returns:
            List of databases
        """
        # Import here to avoid circular imports
        from app.models.user import User
        from sqlalchemy import select
        
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return []
        
        # Use discovery agent
        results = await discovery_agent.discover(
            query=query,
            user=user,
            db=self.db,
            limit=limit
        )
        
        return results

