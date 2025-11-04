"""
Data Source Discovery Endpoints
Help users find relevant data sources via natural language.
"""

from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db
from app.agents.discovery_agent import discovery_agent
from app.core.logging import logger
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter()


class DiscoveryRequest(BaseModel):
    """Schema for discovery request."""
    query: str
    limit: int = 5


class DiscoveryResult(BaseModel):
    """Schema for discovery result."""
    id: int
    name: str
    display_name: str
    description: str | None
    database_type: str
    keywords: List[str] | None
    score: int
    matches: List[str]
    connection_status: str


class DiscoveryResponse(BaseModel):
    """Schema for discovery response."""
    query: str
    results: List[DiscoveryResult]
    message: str


@router.post(
    "/discover",
    response_model=DiscoveryResponse,
    summary="Discover Relevant Data Sources",
)
async def discover_data_sources(
    request: DiscoveryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Discover relevant data sources based on natural language query.
    
    The agent analyzes the query and searches across:
    - Data source names
    - Descriptions
    - Keywords
    
    Returns ranked list of accessible data sources with relevance scores.
    
    Example queries:
    - "sales data"
    - "customer information"
    - "financial reports"
    - "employee records"
    """
    logger.info(
        "discover.request",
        user_id=current_user.id,
        query_preview=request.query[:50],
    )
    
    # Discover data sources
    results = await discovery_agent.discover(
        query=request.query,
        user=current_user,
        db=db,
        limit=request.limit,
    )
    
    # Format conversational message
    message = discovery_agent.format_discovery_message(
        query=request.query,
        discovered_sources=results,
    )
    
    logger.info(
        "discover.success",
        user_id=current_user.id,
        results_count=len(results),
    )
    
    return DiscoveryResponse(
        query=request.query,
        results=results,
        message=message,
    )


@router.get(
    "/suggest",
    response_model=List[str],
    summary="Get Query Suggestions",
)
async def get_query_suggestions(
    partial: str = Query(..., description="Partial query text"),
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get query suggestions based on partial input.
    
    Returns suggested queries based on:
    - Available data source keywords
    - Common query patterns
    - User's accessible data sources
    """
    # Get accessible data sources
    results = await discovery_agent.discover(
        query=partial,
        user=current_user,
        db=db,
        limit=10,
    )
    
    # Extract keywords from top results
    suggestions = []
    for result in results[:limit]:
        if result.get('keywords'):
            for keyword in result['keywords']:
                if partial.lower() in keyword.lower():
                    suggestion = f"Show me {keyword} data"
                    if suggestion not in suggestions:
                        suggestions.append(suggestion)
    
    # Add generic suggestions if we don't have enough
    if len(suggestions) < limit:
        generic_suggestions = [
            f"Show me {partial} trends",
            f"What is the total {partial}?",
            f"Show me top {partial}",
            f"Compare {partial} by region",
            f"Show me recent {partial}",
        ]
        for suggestion in generic_suggestions:
            if len(suggestions) >= limit:
                break
            if suggestion not in suggestions:
                suggestions.append(suggestion)
    
    return suggestions[:limit]














