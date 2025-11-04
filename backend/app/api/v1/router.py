"""
API V1 Router
Aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import admin_setup, auth, database, discover, query, simple_chat, mcp_servers, chat_query, chat_refinement
from app.api.v1 import context

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    simple_chat.router,
    prefix="/simple",
    tags=["Simple Chat"],
)

api_router.include_router(
    mcp_servers.router,
    prefix="/mcp",
    tags=["MCP Servers"],
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

api_router.include_router(
    admin_setup.router,
    prefix="/admin/setup",
    tags=["Admin Setup"],
)

api_router.include_router(
    database.router,
    prefix="/databases",
    tags=["Databases"],
)

api_router.include_router(
    discover.router,
    prefix="",
    tags=["Discovery"],
)

api_router.include_router(
    query.router,
    prefix="/query",
    tags=["Queries"],
)

api_router.include_router(
    context.router,
    prefix="/context",
    tags=["Context Engineering"],
)

api_router.include_router(
    chat_query.router,
    prefix="/chat",
    tags=["Conversational Query"],
)

api_router.include_router(
    chat_refinement.router,
    prefix="/chat",
    tags=["Query Refinement"],
)

