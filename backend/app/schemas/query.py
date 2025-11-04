"""
Query Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryCreate(BaseModel):
    """Schema for creating a new query."""
    
    natural_language_query: str = Field(..., min_length=1, max_length=5000)
    database_connection_id: int


class QueryExecute(BaseModel):
    """Schema for executing a query."""
    
    question: str = Field(..., min_length=1, max_length=5000)
    database_id: int
    context: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Schema for query response."""
    
    id: int
    user_id: int
    database_connection_id: int
    natural_language_query: str
    generated_sql: Optional[str]
    status: str
    execution_time_ms: Optional[int]
    row_count: Optional[int]
    error_message: Optional[str]
    analysis_plan: Optional[Dict[str, Any]]
    visualization_config: Optional[Dict[str, Any]]
    insights: Optional[List[str]]
    is_cached: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueryResultResponse(BaseModel):
    """Schema for query result with data."""
    
    query: QueryResponse
    data: List[Dict[str, Any]]
    columns: List[str]
    column_types: Dict[str, str]














