"""
Query Refinement API Endpoints

Allows users to refine and improve queries.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.base import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.services.session_manager import get_session_manager
from app.services.query_orchestrator import get_query_orchestrator
from app.models.session import MessageRole, MessageType

logger = structlog.get_logger(__name__)
router = APIRouter()


class QueryRefinementRequest(BaseModel):
    """Request to refine a query"""
    session_id: int = Field(..., description="Session ID")
    message_id: Optional[int] = Field(None, description="Original message ID to refine")
    refinement_type: str = Field(
        ...,
        description="Type of refinement: add_filter, change_limit, add_columns, change_sort, simplify"
    )
    refinement_params: dict = Field(..., description="Refinement parameters")


class FeedbackRequest(BaseModel):
    """Request to provide feedback on a query"""
    session_id: int = Field(..., description="Session ID")
    message_id: int = Field(..., description="Message ID")
    feedback_type: str = Field(..., description="Feedback type: positive, negative")
    comment: Optional[str] = Field(None, description="Optional comment")
    issue_category: Optional[str] = Field(
        None,
        description="Issue category: incorrect_sql, wrong_results, slow_query, other"
    )


@router.post("/refine")
async def refine_query(
    request: QueryRefinementRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Refine a previous query.
    
    Refinement types:
    - add_filter: Add WHERE clause
    - change_limit: Modify LIMIT
    - add_columns: Add SELECT columns
    - change_sort: Modify ORDER BY
    - simplify: Simplify the query
    
    Example:
    ```json
    {
      "session_id": 1,
      "refinement_type": "add_filter",
      "refinement_params": {
        "filter": "region = 'US'"
      }
    }
    ```
    """
    try:
        logger.info(
            "refinement.request",
            user_id=current_user.id,
            session_id=request.session_id,
            type=request.refinement_type
        )
        
        # Verify session belongs to user
        session_manager = get_session_manager(db)
        session = await session_manager.get_session(
            session_id=request.session_id,
            user_id=current_user.id,
            load_messages=True
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Get last SQL query from session
        last_sql = None
        for msg in reversed(session.messages):
            if msg.sql_query:
                last_sql = msg.sql_query
                break
        
        if not last_sql:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No previous query found in session"
            )
        
        # Generate refinement message based on type
        refinement_message = _generate_refinement_message(
            request.refinement_type,
            request.refinement_params
        )
        
        # Store refinement request as user message
        await session_manager.add_message(
            session_id=session.id,
            role=MessageRole.USER,
            content=refinement_message,
            message_type=MessageType.USER_MESSAGE,
            metadata={
                "refinement_type": request.refinement_type,
                "refinement_params": request.refinement_params,
                "original_sql": last_sql
            }
        )
        
        # Process the refinement through orchestrator
        orchestrator = get_query_orchestrator(db, current_user)
        response = await orchestrator.process_message(
            message=refinement_message,
            session_id=session.id,
            data_source_id=session.data_source_id
        )
        
        logger.info(
            "refinement.success",
            session_id=session.id,
            type=request.refinement_type
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("refinement.error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refine query: {str(e)}"
        )


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback on a query result.
    
    Feedback helps improve future query generation.
    
    Example:
    ```json
    {
      "session_id": 1,
      "message_id": 5,
      "feedback_type": "negative",
      "comment": "SQL query was incorrect",
      "issue_category": "incorrect_sql"
    }
    ```
    """
    try:
        logger.info(
            "feedback.request",
            user_id=current_user.id,
            session_id=request.session_id,
            message_id=request.message_id,
            type=request.feedback_type
        )
        
        # Verify session belongs to user
        session_manager = get_session_manager(db)
        session = await session_manager.get_session(
            session_id=request.session_id,
            user_id=current_user.id,
            load_messages=True
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Find the message
        target_message = None
        for msg in session.messages:
            if msg.id == request.message_id:
                target_message = msg
                break
        
        if not target_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Store feedback in message metadata
        target_message.set_metadata_value("user_feedback", {
            "type": request.feedback_type,
            "comment": request.comment,
            "issue_category": request.issue_category,
            "timestamp": str(target_message.created_at)
        })
        
        await db.commit()
        
        # Add feedback acknowledgment message
        if request.feedback_type == "positive":
            response_content = "Thanks for the positive feedback! 👍"
        else:
            response_content = f"Thanks for the feedback. I'll work on improving! 👎\n\n"
            if request.comment:
                response_content += "Would you like me to try again with a different approach?"
        
        await session_manager.add_message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content=response_content,
            message_type=MessageType.INFO,
            metadata={"feedback_acknowledgment": True}
        )
        
        logger.info(
            "feedback.success",
            session_id=session.id,
            message_id=request.message_id,
            type=request.feedback_type
        )
        
        return {
            "success": True,
            "message": "Feedback received",
            "response": response_content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("feedback.error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


def _generate_refinement_message(
    refinement_type: str,
    params: dict
) -> str:
    """Generate natural language message from refinement params"""
    
    if refinement_type == "add_filter":
        filter_expr = params.get("filter", "")
        return f"Add a filter: {filter_expr}"
    
    elif refinement_type == "change_limit":
        limit = params.get("limit", 10)
        return f"Show me just the top {limit} results"
    
    elif refinement_type == "add_columns":
        columns = params.get("columns", [])
        columns_str = ", ".join(columns)
        return f"Also include these columns: {columns_str}"
    
    elif refinement_type == "change_sort":
        sort_col = params.get("column", "")
        direction = params.get("direction", "DESC")
        return f"Sort by {sort_col} in {direction} order"
    
    elif refinement_type == "simplify":
        return "Simplify this query to just show the essential information"
    
    else:
        return f"Refine the previous query with: {params}"

