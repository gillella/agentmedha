"""
Admin Setup API Endpoints
Conversational interface for admin database configuration.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.agents.admin_setup_agent import admin_setup_agent
from app.core.logging import logger
from app.models.user import User
from app.services.auth import get_current_admin

router = APIRouter()


class AdminChatMessage(BaseModel):
    """Schema for admin chat message"""
    
    message: str
    context: Optional[Dict[str, Any]] = None


class AdminChatResponse(BaseModel):
    """Schema for admin chat response"""
    
    message: str
    intent: str
    ui_component: str
    data: Optional[Dict[str, Any]] = None
    next_state: str
    context: Dict[str, Any]


class DatabaseSelectionRequest(BaseModel):
    """Schema for database type selection"""
    
    database_type: str  # postgresql, mysql, supabase, snowflake
    context: Optional[Dict[str, Any]] = None


@router.post(
    "/chat",
    response_model=AdminChatResponse,
    summary="Chat with Admin Setup Assistant",
)
async def chat_with_admin_agent(
    request: AdminChatMessage,
    current_user: User = Depends(get_current_admin),
):
    """
    Conversational endpoint for admin database setup.
    
    The agent understands natural language and guides the admin through:
    - Database type selection
    - Connection configuration
    - Database creation
    - Table creation
    - Data loading
    
    Example messages:
    - "I want to set up a database"
    - "Connect to PostgreSQL"
    - "Help me configure MySQL"
    """
    logger.info(
        "admin_setup.chat_request",
        user_id=current_user.id,
        message_preview=request.message[:50],
    )
    
    try:
        # Process message through agent
        response = await admin_setup_agent.process_message(
            message=request.message,
            context=request.context,
        )
        
        # Extract context for next request
        context = request.context or {}
        context["state"] = response["next_state"]
        if "database_type" in response.get("data", {}):
            context["database_type"] = response["data"]["database_type"]
        
        logger.info(
            "admin_setup.chat_success",
            user_id=current_user.id,
            intent=response["intent"],
            ui_component=response["ui_component"],
        )
        
        return AdminChatResponse(
            message=response["message"],
            intent=response["intent"],
            ui_component=response["ui_component"],
            data=response.get("data"),
            next_state=response["next_state"],
            context=context,
        )
        
    except Exception as e:
        logger.error(
            "admin_setup.chat_failed",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}",
        )


@router.post(
    "/select-database",
    response_model=AdminChatResponse,
    summary="Select Database Type",
)
async def select_database_type(
    request: DatabaseSelectionRequest,
    current_user: User = Depends(get_current_admin),
):
    """
    Handle database type selection (when admin clicks a database card).
    
    This is called when admin clicks on a database card in the UI,
    as an alternative to typing the selection in chat.
    """
    logger.info(
        "admin_setup.database_selected",
        user_id=current_user.id,
        database_type=request.database_type,
    )
    
    try:
        # Process as if admin typed the database name
        message = f"I want to use {request.database_type}"
        
        # Ensure context has the right state
        context = request.context or {}
        context["state"] = "selecting_database_type"
        
        response = await admin_setup_agent.process_message(
            message=message,
            context=context,
        )
        
        # Update context
        context["state"] = response["next_state"]
        context["database_type"] = request.database_type
        
        logger.info(
            "admin_setup.database_selection_success",
            user_id=current_user.id,
            database_type=request.database_type,
        )
        
        return AdminChatResponse(
            message=response["message"],
            intent=response["intent"],
            ui_component=response["ui_component"],
            data=response.get("data"),
            next_state=response["next_state"],
            context=context,
        )
        
    except Exception as e:
        logger.error(
            "admin_setup.database_selection_failed",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to select database: {str(e)}",
        )


@router.get(
    "/database-types",
    summary="Get Available Database Types",
)
async def get_database_types(
    current_user: User = Depends(get_current_admin),
):
    """
    Get list of supported database types with metadata.
    
    Returns information about each database type including:
    - Name and description
    - Connection requirements
    - Popularity/recommended status
    """
    return {
        "database_types": [
            {
                "id": "postgresql",
                "name": "PostgreSQL",
                "description": "Open-source relational database with excellent features and performance",
                "icon": "database",
                "popular": True,
                "recommended": True,
                "connection_fields": [
                    "host",
                    "port",
                    "username",
                    "password",
                    "database",
                ],
            },
            {
                "id": "mysql",
                "name": "MySQL",
                "description": "World's most popular open-source database, great for web applications",
                "icon": "database",
                "popular": True,
                "recommended": False,
                "connection_fields": [
                    "host",
                    "port",
                    "username",
                    "password",
                    "database",
                ],
            },
            {
                "id": "supabase",
                "name": "Supabase",
                "description": "PostgreSQL with built-in APIs, authentication, and real-time subscriptions",
                "icon": "cloud",
                "popular": False,
                "recommended": True,
                "connection_fields": [
                    "project_url",
                    "api_key",
                    "database",
                ],
            },
            {
                "id": "snowflake",
                "name": "Snowflake",
                "description": "Cloud data warehouse platform for enterprise analytics and big data",
                "icon": "cloud",
                "popular": False,
                "recommended": False,
                "connection_fields": [
                    "account",
                    "username",
                    "password",
                    "warehouse",
                    "database",
                    "schema",
                ],
            },
        ]
    }


@router.post(
    "/reset-conversation",
    summary="Reset Conversation Context",
)
async def reset_conversation(
    current_user: User = Depends(get_current_admin),
):
    """
    Reset the conversation context to start fresh.
    
    Useful when admin wants to start a new setup process
    or when there's an error and they want to restart.
    """
    logger.info("admin_setup.conversation_reset", user_id=current_user.id)
    
    return {
        "message": "Conversation reset successfully",
        "context": {
            "state": "start",
            "database_type": None,
            "connection_details": {},
            "conversation_history": [],
        },
    }














