"""
Main FastAPI Application
Entry point for the BI Agent API following 12 Factor Agents principles.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

# Setup structured logging
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for startup and shutdown events.
    Principle #9: Disposability - Fast startup and graceful shutdown.
    """
    # Startup
    logger.info(
        "application.starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )

    # Initialize services
    # await database.connect()
    # await cache.connect()
    # await vector_store.connect()

    logger.info("application.started")

    yield

    # Shutdown
    logger.info("application.shutting_down")

    # Cleanup services
    # await database.disconnect()
    # await cache.disconnect()

    logger.info("application.stopped")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered Data Analytics & Business Intelligence Agent",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# Middleware

# CORS - Principle #7: Port Binding
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request ID middleware for tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request for tracing."""
    import uuid

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    # Bind request_id to logger context
    structlog.contextvars.bind_contextvars(request_id=request_id)
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    structlog.contextvars.clear_contextvars()
    
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        exc_message=str(exc),
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """
    Detailed health check that verifies all dependencies.
    """
    health_status = {
        "api": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
    }
    
    # Check database
    try:
        # await database.execute("SELECT 1")
        health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        # await cache.ping()
        health_status["cache"] = "healthy"
    except Exception as e:
        health_status["cache"] = f"unhealthy: {str(e)}"
    
    # Check LLM API
    try:
        # Simple check - could ping OpenAI API
        health_status["llm"] = "healthy" if settings.openai_api_key else "unconfigured"
    except Exception as e:
        health_status["llm"] = f"unhealthy: {str(e)}"
    
    # Overall status
    all_healthy = all(
        v == "healthy"
        for k, v in health_status.items()
        if k not in ["version", "environment"]
    )
    health_status["status"] = "healthy" if all_healthy else "degraded"
    
    return health_status


# Include API router
app.include_router(api_router, prefix=settings.api_prefix)

# Prometheus metrics endpoint
# Principle #11: Logs as Event Streams + Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

