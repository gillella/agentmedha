"""
Conversational Query API Endpoint

Unified endpoint for conversational data analytics:
- Session management
- Data source discovery
- Context-aware SQL generation
- Query execution
- Visualization suggestions
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.base import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.services.query_orchestrator import get_query_orchestrator
from app.services.session_manager import get_session_manager

logger = structlog.get_logger(__name__)
router = APIRouter()


# Request/Response Models

class ChatQueryRequest(BaseModel):
    """Request to process a conversational query"""
    message: str = Field(..., description="User message", min_length=1, max_length=2000)
    session_id: Optional[int] = Field(None, description="Existing session ID")
    data_source_id: Optional[int] = Field(None, description="Data source ID (if already selected)")


class DataSourceInfo(BaseModel):
    """Data source information"""
    id: int
    name: str
    display_name: str
    description: Optional[str]
    database_type: str
    keywords: Optional[List[str]]
    connection_status: str


class VisualizationConfig(BaseModel):
    """Visualization configuration"""
    type: str = Field(..., description="Chart type: bar_chart, line_chart, pie_chart, table")
    title: Optional[str] = Field(None, description="Chart title")
    suggested: bool = Field(False, description="Whether this was auto-suggested")


class ContextStats(BaseModel):
    """Context retrieval statistics"""
    query_tokens: int
    context_tokens: int
    total_tokens: int
    max_tokens: int
    utilization: float
    cache_hit: bool


class ChatQueryResponse(BaseModel):
    """Response from conversational query"""
    session_id: int = Field(..., description="Session ID")
    message_type: str = Field(
        ...,
        description="Response type: discovery, query_result, clarification, error, info"
    )
    content: str = Field(..., description="Response message")
    
    # For discovery responses
    data_sources: Optional[List[DataSourceInfo]] = Field(None, description="Discovered data sources")
    
    # For query_result responses
    sql_query: Optional[str] = Field(None, description="Generated SQL query")
    sql_explanation: Optional[str] = Field(None, description="SQL explanation")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="Query results")
    result_count: Optional[int] = Field(None, description="Total result count")
    visualization: Optional[VisualizationConfig] = Field(None, description="Visualization config")
    suggested_actions: Optional[List[str]] = Field(None, description="Suggested follow-up actions")
    context_stats: Optional[ContextStats] = Field(None, description="Context stats")
    
    # For error responses
    error_code: Optional[str] = Field(None, description="Error code")


class SessionInfo(BaseModel):
    """Session information"""
    id: int
    status: str
    title: Optional[str]
    data_source_id: Optional[int]
    message_count: int
    started_at: str
    last_activity_at: str


class SessionListResponse(BaseModel):
    """List of sessions"""
    sessions: List[SessionInfo]
    total: int


# Endpoints

@router.post("/query", response_model=ChatQueryResponse)
async def conversational_query(
    request: ChatQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process a conversational query.
    
    This is the main endpoint for conversational data analytics.
    It handles:
    - Session management (create or continue)
    - Data source discovery (if needed)
    - Context-aware SQL generation
    - Query execution
    - Result formatting
    - Visualization suggestions
    
    Flow:
    1. User sends message
    2. System checks if data source is selected
    3. If not, runs discovery and returns options
    4. If yes, generates SQL, executes, and returns results
    5. Suggests visualizations and follow-up actions
    """
    try:
        logger.info(
            "chat_query.request",
            user_id=current_user.id,
            session_id=request.session_id,
            has_data_source=request.data_source_id is not None
        )
        
        # Create orchestrator
        orchestrator = get_query_orchestrator(db, current_user)
        
        # Process message
        response = await orchestrator.process_message(
            message=request.message,
            session_id=request.session_id,
            data_source_id=request.data_source_id
        )
        
        # Convert to response model
        return ChatQueryResponse(**response)
        
    except Exception as e:
        logger.error(
            "chat_query.error",
            error=str(e),
            user_id=current_user.id,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List user's conversation sessions.
    
    Args:
        status: Optional filter by status (active, completed, expired)
        limit: Max sessions to return
        offset: Pagination offset
    """
    try:
        session_manager = get_session_manager(db)
        
        from app.models.session import SessionStatus
        status_filter = None
        if status:
            try:
                status_filter = SessionStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}"
                )
        
        sessions = await session_manager.get_user_sessions(
            user_id=current_user.id,
            status=status_filter,
            limit=limit,
            offset=offset
        )
        
        return SessionListResponse(
            sessions=[
                SessionInfo(
                    id=s.id,
                    status=s.status.value,
                    title=s.title,
                    data_source_id=s.data_source_id,
                    message_count=s.message_count,
                    started_at=s.started_at.isoformat(),
                    last_activity_at=s.last_activity_at.isoformat()
                )
                for s in sessions
            ],
            total=len(sessions)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("sessions.list_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get session details including message history.
    """
    try:
        session_manager = get_session_manager(db)
        
        session = await session_manager.get_session(
            session_id=session_id,
            user_id=current_user.id,
            load_messages=True
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {
            "id": session.id,
            "status": session.status.value,
            "title": session.title,
            "data_source_id": session.data_source_id,
            "started_at": session.started_at.isoformat(),
            "last_activity_at": session.last_activity_at.isoformat(),
            "message_count": session.message_count,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role.value,
                    "type": m.message_type.value,
                    "content": m.content,
                    "sql_query": m.sql_query,
                    "sql_explanation": m.sql_explanation,
                    "result_count": m.result_count,
                    "visualization_config": m.visualization_config,
                    "suggested_actions": m.suggested_actions,
                    "error_message": m.error_message,
                    "created_at": m.created_at.isoformat()
                }
                for m in session.messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("session.get_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    End/delete a session.
    """
    try:
        session_manager = get_session_manager(db)
        
        # Verify session belongs to user
        session = await session_manager.get_session(
            session_id=session_id,
            user_id=current_user.id,
            load_messages=False
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        success = await session_manager.end_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to end session"
            )
        
        return {"success": True, "message": "Session ended"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("session.delete_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.post("/sessions/{session_id}/data-source")
async def set_session_data_source(
    session_id: int,
    data_source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Set data source for a session.
    """
    try:
        session_manager = get_session_manager(db)
        
        # Verify session belongs to user
        session = await session_manager.get_session(
            session_id=session_id,
            user_id=current_user.id,
            load_messages=False
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        success = await session_manager.set_data_source(session_id, data_source_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set data source"
            )
        
        return {"success": True, "data_source_id": data_source_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("session.set_data_source_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set data source: {str(e)}"
        )

