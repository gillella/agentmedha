"""
Natural language to SQL query endpoint
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import openai
import os
import json
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from app.models.base import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.services.mcp_manager import get_mcp_manager
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")


def serialize_value(value: Any) -> Any:
    """Convert Python objects to JSON-serializable types"""
    if isinstance(value, UUID):
        return str(value)
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    elif value is None:
        return None
    else:
        return value


class QueryRequest(BaseModel):
    """Request model for natural language query"""
    question: str
    conversation_history: Optional[List[Dict[str, str]]] = []


class QueryResponse(BaseModel):
    """Response model for natural language query"""
    answer: str
    sql_query: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    tables_used: Optional[List[str]] = None
    visualization_suggestion: Optional[str] = None


@router.post("/query", response_model=QueryResponse)
async def natural_language_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process a natural language query against discovered resources.
    
    This endpoint:
    1. Discovers available tables from MCP servers
    2. Generates SQL query using GPT-4
    3. Executes the query
    4. Formats and returns results
    """
    try:
        logger.info("query.natural_language", question=request.question, user_id=current_user.id)
        
        # Get available resources (tables) from all MCP servers
        manager = get_mcp_manager()
        servers = await manager.list_servers(db, status="active")
        
        # Get all resources from PostgreSQL servers
        all_resources = []
        postgres_server = None
        
        for server in servers:
            if server.server_type in ["postgresql", "postgres"]:
                postgres_server = server
                resources = await manager.list_resources(db, str(server.id), refresh=False)
                all_resources.extend(resources)
        
        if not postgres_server:
            return QueryResponse(
                answer="I couldn't find any active PostgreSQL databases. Please connect a database first.",
                sql_query=None,
                results=None
            )
        
        if not all_resources:
            return QueryResponse(
                answer="I couldn't find any discovered tables. Please discover resources from your databases first.",
                sql_query=None,
                results=None
            )
        
        # Get table schema information
        table_schemas = await get_table_schemas(db, postgres_server, all_resources)
        
        # Generate SQL query using GPT-4
        sql_query = await generate_sql_query(
            question=request.question,
            table_schemas=table_schemas,
            conversation_history=request.conversation_history
        )
        
        if not sql_query:
            return QueryResponse(
                answer="I couldn't generate a SQL query for your question. Could you please rephrase it?",
                sql_query=None,
                results=None
            )
        
        # Execute the SQL query
        try:
            result = await db.execute(text(sql_query))
            rows = result.fetchall()
            
            # Convert rows to list of dicts with proper serialization
            columns = result.keys()
            results = [
                {col: serialize_value(val) for col, val in zip(columns, row)}
                for row in rows
            ]
            
            # Generate natural language answer
            answer = await generate_answer(
                question=request.question,
                sql_query=sql_query,
                results=results
            )
            
            # Extract tables used
            tables_used = extract_tables_from_query(sql_query, all_resources)
            
            # Suggest visualization if applicable
            viz_suggestion = suggest_visualization(results, sql_query)
            
            logger.info("query.success", 
                       rows_returned=len(results), 
                       tables_used=len(tables_used))
            
            return QueryResponse(
                answer=answer,
                sql_query=sql_query,
                results=results[:100],  # Limit to 100 rows for UI
                tables_used=tables_used,
                visualization_suggestion=viz_suggestion
            )
            
        except Exception as e:
            logger.error("query.execution_failed", error=str(e), sql=sql_query)
            return QueryResponse(
                answer=f"I generated a query, but there was an error executing it: {str(e)}",
                sql_query=sql_query,
                results=None
            )
    
    except Exception as e:
        logger.error("query.failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )


async def get_table_schemas(
    db: AsyncSession,
    postgres_server,
    resources: List
) -> Dict[str, Dict[str, Any]]:
    """Get schema information for discovered tables"""
    schemas = {}
    
    for resource in resources:
        if resource.resource_type == "table":
            full_name = resource.name
            
            # Parse schema.table format
            if '.' in full_name:
                schema_name, table_name = full_name.split('.', 1)
            else:
                schema_name = 'public'
                table_name = full_name
            
            try:
                # Get column information
                query = text(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = :table_name
                    AND table_schema = :schema_name
                    ORDER BY ordinal_position
                """)
                
                result = await db.execute(query, {"table_name": table_name, "schema_name": schema_name})
                columns = result.fetchall()
                
                # Use full_name (schema.table) as key to avoid conflicts
                schemas[full_name] = {
                    "columns": [
                        {
                            "name": col[0],
                            "type": col[1],
                            "nullable": col[2] == "YES"
                        }
                        for col in columns
                    ],
                    "description": resource.resource_metadata.get("description") if resource.resource_metadata else None
                }
            except Exception as e:
                logger.warning(f"Failed to get schema for {full_name}: {str(e)}")
                continue
    
    return schemas


async def generate_sql_query(
    question: str,
    table_schemas: Dict[str, Dict[str, Any]],
    conversation_history: List[Dict[str, str]]
) -> Optional[str]:
    """Generate SQL query using GPT-4"""
    
    # Build schema description
    schema_description = "Available tables and their columns:\n\n"
    for table_name, schema in table_schemas.items():
        schema_description += f"Table: {table_name}\n"
        if schema.get("description"):
            schema_description += f"Description: {schema['description']}\n"
        schema_description += "Columns:\n"
        for col in schema["columns"]:
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            schema_description += f"  - {col['name']} ({col['type']}) {nullable}\n"
        schema_description += "\n"
    
    # Build conversation context
    context = ""
    if conversation_history:
        context = "Previous conversation:\n"
        for msg in conversation_history[-3:]:  # Last 3 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            context += f"{role}: {content}\n"
        context += "\n"
    
    # Create prompt
    prompt = f"""{context}Database Schema:
{schema_description}

User Question: {question}

Generate a PostgreSQL SQL query to answer this question. Return ONLY the SQL query, nothing else.
Use proper PostgreSQL syntax. Include LIMIT 100 by default if not specified.
If the question cannot be answered with the available tables, return "UNABLE_TO_ANSWER".
"""
    
    try:
        response = openai.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": "You are an expert SQL query generator. Generate only valid PostgreSQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Clean up the query
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        sql_query = sql_query.strip()
        
        if sql_query == "UNABLE_TO_ANSWER":
            return None
        
        return sql_query
        
    except Exception as e:
        logger.error("query.generation_failed", error=str(e))
        return None


async def generate_answer(
    question: str,
    sql_query: str,
    results: List[Dict[str, Any]]
) -> str:
    """Generate natural language answer from query results"""
    
    if not results:
        return "I executed the query, but didn't find any results."
    
    # Summarize results
    result_summary = f"Found {len(results)} result(s).\n\n"
    if len(results) <= 5:
        result_summary += json.dumps(results, indent=2, default=str)
    else:
        result_summary += f"First 5 results:\n{json.dumps(results[:5], indent=2, default=str)}"
    
    prompt = f"""Question: {question}

SQL Query executed:
{sql_query}

Results:
{result_summary}

Generate a concise, natural language answer to the user's question based on these results.
Be specific and mention key numbers or insights."""
    
    try:
        response = openai.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": "You are a helpful data analyst. Provide clear, concise answers based on query results."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error("answer.generation_failed", error=str(e))
        # Fallback to simple answer
        return f"I found {len(results)} result(s). {result_summary}"


def extract_tables_from_query(sql_query: str, resources: List) -> List[str]:
    """Extract table names mentioned in the SQL query"""
    tables_used = []
    sql_lower = sql_query.lower()
    
    for resource in resources:
        if resource.resource_type == "table":
            table_name = resource.name
            if table_name.lower() in sql_lower:
                tables_used.append(table_name)
    
    return tables_used


def suggest_visualization(results: List[Dict[str, Any]], sql_query: str) -> Optional[str]:
    """Suggest appropriate visualization for the results"""
    if not results or len(results) == 0:
        return None
    
    # Count columns
    num_columns = len(results[0].keys()) if results else 0
    num_rows = len(results)
    
    sql_lower = sql_query.lower()
    
    # Time series data
    if any(keyword in sql_lower for keyword in ["date", "time", "timestamp"]) and num_rows > 2:
        return "line_chart"
    
    # Aggregations (GROUP BY)
    if "group by" in sql_lower and num_rows <= 20:
        return "bar_chart"
    
    # Count queries
    if "count(" in sql_lower:
        return "bar_chart"
    
    # Many rows, few columns
    if num_rows > 10 and num_columns <= 3:
        return "table"
    
    return "table"
