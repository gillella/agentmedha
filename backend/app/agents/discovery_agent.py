"""
Data Source Discovery Agent
Help users find the right data source based on their natural language query.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.database import DatabaseConnection
from app.models.user import User


class DataSourceDiscoveryAgent:
    """
    Agent responsible for discovering relevant data sources based on user queries.
    
    This agent:
    1. Analyzes user's natural language query
    2. Searches data source names, descriptions, and keywords
    3. Returns ranked list of relevant data sources
    4. Filters based on user access
    
    Principle #1: Single-Purpose Agent - focused only on discovery
    """

    @staticmethod
    async def discover(
        query: str,
        user: User,
        db: AsyncSession,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Discover relevant data sources for a user query.
        
        Args:
            query: Natural language query from user
            user: Current user (for access filtering)
            db: Database session
            limit: Maximum number of results
            
        Returns:
            List of relevant data sources with relevance scores
        """
        logger.info(
            "discovery_agent.searching",
            query_preview=query[:50],
            user_id=user.id,
        )
        
        # Get all active data sources
        result = await db.execute(
            select(DatabaseConnection)
            .where(DatabaseConnection.is_active == True)
            .order_by(DatabaseConnection.created_at.desc())
        )
        all_sources = result.scalars().all()
        
        # Filter by access
        accessible_sources = [
            source for source in all_sources
            if source.is_accessible_by(user)
        ]
        
        if not accessible_sources:
            logger.info("discovery_agent.no_accessible_sources", user_id=user.id)
            return []
        
        # Score and rank sources
        scored_sources = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for source in accessible_sources:
            score = 0
            matches = []
            
            # Check display name
            if source.display_name:
                display_name_lower = source.display_name.lower()
                if query_lower in display_name_lower:
                    score += 10
                    matches.append(f"name: {source.display_name}")
                # Check word matches
                for word in query_words:
                    if word in display_name_lower:
                        score += 5
            
            # Check internal name
            name_lower = source.name.lower()
            if query_lower in name_lower:
                score += 8
                matches.append(f"id: {source.name}")
            
            # Check description
            if source.description:
                desc_lower = source.description.lower()
                if query_lower in desc_lower:
                    score += 7
                    matches.append(f"description")
                # Check word matches
                for word in query_words:
                    if word in desc_lower:
                        score += 3
            
            # Check keywords (highest weight)
            if source.keywords:
                for keyword in source.keywords:
                    keyword_lower = keyword.lower()
                    if query_lower in keyword_lower or keyword_lower in query_lower:
                        score += 15
                        matches.append(f"keyword: {keyword}")
                    # Check word matches
                    for word in query_words:
                        if word == keyword_lower:
                            score += 10
                        elif word in keyword_lower:
                            score += 5
            
            # Database type match
            if source.database_type.lower() in query_lower:
                score += 3
                matches.append(f"type: {source.database_type}")
            
            # Only include sources with some relevance
            if score > 0:
                scored_sources.append({
                    "id": source.id,
                    "name": source.name,
                    "display_name": source.display_name or source.name,
                    "description": source.description,
                    "database_type": source.database_type,
                    "keywords": source.keywords,
                    "score": score,
                    "matches": matches,
                    "connection_status": source.connection_status,
                })
        
        # Sort by score (descending)
        scored_sources.sort(key=lambda x: x["score"], reverse=True)
        
        # Limit results
        results = scored_sources[:limit]
        
        logger.info(
            "discovery_agent.results",
            query_preview=query[:50],
            total_accessible=len(accessible_sources),
            relevant_found=len(scored_sources),
            returned=len(results),
        )
        
        return results

    @staticmethod
    def format_discovery_message(
        query: str,
        discovered_sources: List[Dict[str, Any]],
    ) -> str:
        """
        Format discovery results into a conversational message.
        
        Args:
            query: Original user query
            discovered_sources: List of discovered data sources
            
        Returns:
            Formatted message for user
        """
        if not discovered_sources:
            return (
                f"I couldn't find any data sources matching '{query}'. "
                "Please try a different query or contact your admin to add relevant data sources."
            )
        
        if len(discovered_sources) == 1:
            source = discovered_sources[0]
            return (
                f"I found **{source['display_name']}** which seems relevant for your query.\n\n"
                f"*{source['description'] or 'No description available'}*\n\n"
                f"Would you like me to query this database?"
            )
        
        # Multiple sources
        message_parts = [
            f"I found {len(discovered_sources)} data sources that might help:\n"
        ]
        
        for idx, source in enumerate(discovered_sources, 1):
            desc = source['description'] or 'No description'
            keywords_str = ", ".join(source['keywords'][:3]) if source.get('keywords') else ""
            
            message_parts.append(
                f"\n{idx}. **{source['display_name']}** ({source['database_type']})"
            )
            message_parts.append(f"   *{desc}*")
            if keywords_str:
                message_parts.append(f"   Tags: {keywords_str}")
        
        message_parts.append("\n\nWhich data source would you like to query?")
        
        return "\n".join(message_parts)


# Global instance
discovery_agent = DataSourceDiscoveryAgent()














