"""
Query Orchestrator Service

Orchestrates the full conversational query flow:
1. Session management
2. Discovery (if needed)
3. Context retrieval
4. SQL generation
5. Query execution
6. Result formatting
7. Visualization suggestion
"""
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
import structlog

from app.models.user import User
from app.models.database import DatabaseConnection
from app.models.session import MessageRole, MessageType
from app.services.session_manager import SessionManager, get_session_manager
from app.services.context_manager import get_context_manager
from app.agents.sql_agent import get_sql_agent
from app.services.discovery import DiscoveryService
from app.services.cache import cache

logger = structlog.get_logger(__name__)


class QueryOrchestrator:
    """
    Orchestrates conversational query processing.
    
    Handles:
    - Session lifecycle
    - Data source discovery
    - Context-aware SQL generation
    - Query execution
    - Result formatting
    - Visualization suggestions
    """
    
    def __init__(
        self,
        db: AsyncSession,
        user: User
    ):
        self.db = db
        self.user = user
        self.session_manager = get_session_manager(db)
        self.context_manager = get_context_manager(db, cache)
        self.sql_agent = get_sql_agent(db)
        self.discovery_service = DiscoveryService(db)
    
    async def process_message(
        self,
        message: str,
        session_id: Optional[int] = None,
        data_source_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a user message.
        
        Flow:
        1. Get or create session
        2. If no data source, run discovery
        3. If data source selected, generate SQL
        4. Execute query
        5. Format results
        6. Suggest visualization
        7. Return response
        
        Args:
            message: User message
            session_id: Optional existing session ID
            data_source_id: Optional data source ID
            
        Returns:
            Response dict
        """
        logger.info(
            "query.processing",
            user_id=self.user.id,
            session_id=session_id,
            message_length=len(message)
        )
        
        # Step 1: Get or create session
        session = await self._get_or_create_session(session_id, data_source_id)
        
        # Add user message
        await self.session_manager.add_message(
            session_id=session.id,
            role=MessageRole.USER,
            content=message,
            message_type=MessageType.USER_MESSAGE
        )
        
        # Step 2: Check if we need discovery
        if not session.data_source_id and not data_source_id:
            return await self._handle_discovery(session, message)
        
        # Update session data source if provided
        if data_source_id and session.data_source_id != data_source_id:
            await self.session_manager.set_data_source(session.id, data_source_id)
            session.data_source_id = data_source_id
        
        # Step 3: Generate and execute SQL query
        return await self._handle_query(session, message)
    
    async def _get_or_create_session(
        self,
        session_id: Optional[int],
        data_source_id: Optional[int]
    ):
        """Get existing session or create new one"""
        if session_id:
            session = await self.session_manager.get_session(
                session_id,
                user_id=self.user.id,
                load_messages=False
            )
            if session:
                return session
        
        # Create new session
        return await self.session_manager.create_session(
            user_id=self.user.id,
            data_source_id=data_source_id
        )
    
    async def _handle_discovery(
        self,
        session,
        message: str
    ) -> Dict[str, Any]:
        """Handle data source discovery"""
        logger.info("query.discovery", session_id=session.id)
        
        # Run discovery
        discovery_results = await self.discovery_service.discover_data_sources(
            query=message,
            user_id=self.user.id,
            limit=5
        )
        
        if not discovery_results:
            response_content = (
                "I couldn't find any data sources matching your query. "
                "Please try rephrasing or contact your admin to set up data sources."
            )
            
            await self.session_manager.add_message(
                session_id=session.id,
                role=MessageRole.ASSISTANT,
                content=response_content,
                message_type=MessageType.INFO
            )
            
            return {
                "session_id": session.id,
                "message_type": "info",
                "content": response_content,
                "data_sources": []
            }
        
        # Format discovery response
        response_content = self._format_discovery_response(discovery_results)
        
        # Store assistant message
        await self.session_manager.add_message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content=response_content,
            message_type=MessageType.DISCOVERY,
            metadata={
                "discovery_results": [
                    {
                        "id": ds.id,
                        "name": ds.name,
                        "display_name": ds.display_name,
                        "score": ds.score if hasattr(ds, 'score') else 0
                    }
                    for ds in discovery_results
                ]
            }
        )
        
        return {
            "session_id": session.id,
            "message_type": "discovery",
            "content": response_content,
            "data_sources": [
                {
                    "id": ds.id,
                    "name": ds.name,
                    "display_name": ds.display_name,
                    "description": ds.description,
                    "database_type": ds.database_type,
                    "keywords": ds.keywords,
                    "connection_status": ds.connection_status
                }
                for ds in discovery_results
            ]
        }
    
    async def _handle_query(
        self,
        session,
        message: str
    ) -> Dict[str, Any]:
        """Handle SQL query generation and execution"""
        logger.info("query.sql_generation", session_id=session.id)
        
        try:
            # Get data source
            data_source = await self._get_data_source(session.data_source_id)
            if not data_source:
                return await self._error_response(
                    session,
                    "Data source not found or not accessible.",
                    "DATA_SOURCE_NOT_FOUND"
                )
            
            # Get schema information
            schema_info = await self._get_schema_info(data_source)
            
            # Get conversation context
            conversation_context = await self.session_manager.get_context_from_history(
                session.id,
                last_n_messages=5
            )
            
            # Get business context
            context_result = await self.context_manager.get_context_for_query(
                query=message,
                database_id=data_source.id,
                tables=list(conversation_context.get("tables_used", [])) or None,
                user_permissions={"role": self.user.role, "user_id": self.user.id},
                max_tokens=4000,
                use_cache=True
            )
            
            # Generate SQL using context-aware agent
            sql_result = await self.sql_agent.generate_query(
                question=message,
                schema=schema_info,
                database_type=data_source.database_type,
                database_id=data_source.id,
                user_permissions={"role": self.user.role, "user_id": self.user.id},
                conversation_history=conversation_context.get("conversation_summary", [])
            )
            
            if not sql_result.get("success"):
                return await self._error_response(
                    session,
                    sql_result.get("message", "Failed to generate SQL query."),
                    "SQL_GENERATION_FAILED"
                )
            
            sql_query = sql_result["query"]
            sql_explanation = sql_result.get("explanation", "")
            
            # Execute query
            results, error = await self._execute_query(data_source, sql_query)
            
            if error:
                return await self._error_response(
                    session,
                    f"Query execution failed: {error}",
                    "QUERY_EXECUTION_FAILED",
                    sql_query=sql_query
                )
            
            # Suggest visualization
            viz_config = self._suggest_visualization(results, sql_query)
            
            # Generate suggested follow-ups
            suggested_actions = self._generate_suggestions(results, sql_query, message)
            
            # Format response
            response_content = self._format_query_response(
                results,
                sql_explanation
            )
            
            # Store assistant message
            await self.session_manager.add_message(
                session_id=session.id,
                role=MessageRole.ASSISTANT,
                content=response_content,
                message_type=MessageType.QUERY_RESULT,
                sql_query=sql_query,
                sql_explanation=sql_explanation,
                results=results,
                visualization_config=viz_config,
                context_stats=context_result.get("stats"),
                suggested_actions=suggested_actions
            )
            
            # Update session context
            await self.session_manager.update_session_context(
                session.id,
                {
                    "last_tables": list(conversation_context.get("tables_used", [])),
                    "last_query": sql_query
                }
            )
            
            logger.info(
                "query.success",
                session_id=session.id,
                result_count=len(results),
                viz_type=viz_config.get("type") if viz_config else None
            )
            
            return {
                "session_id": session.id,
                "message_type": "query_result",
                "content": response_content,
                "sql_query": sql_query,
                "sql_explanation": sql_explanation,
                "results": results[:100],  # Limit frontend results
                "result_count": len(results),
                "visualization": viz_config,
                "suggested_actions": suggested_actions,
                "context_stats": context_result.get("stats")
            }
            
        except Exception as e:
            logger.error("query.error", session_id=session.id, error=str(e), exc_info=True)
            return await self._error_response(
                session,
                f"An unexpected error occurred: {str(e)}",
                "UNEXPECTED_ERROR"
            )
    
    async def _get_data_source(self, data_source_id: int) -> Optional[DatabaseConnection]:
        """Get data source by ID"""
        query = select(DatabaseConnection).where(Database.id == data_source_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_schema_info(self, data_source: DatabaseConnection) -> Dict[str, Any]:
        """Get schema information for data source"""
        # Simplified schema retrieval - in production, use full schema service
        try:
            query = text("""
                SELECT 
                    table_schema,
                    table_name,
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_schema, table_name, ordinal_position
                LIMIT 1000
            """)
            
            result = await self.db.execute(query)
            rows = result.fetchall()
            
            schema = {}
            for row in rows:
                table_key = f"{row[0]}.{row[1]}"
                if table_key not in schema:
                    schema[table_key] = {"columns": []}
                
                schema[table_key]["columns"].append({
                    "name": row[2],
                    "type": row[3],
                    "nullable": row[4] == "YES"
                })
            
            return schema
            
        except Exception as e:
            logger.error("schema.retrieval_failed", error=str(e))
            return {}
    
    async def _execute_query(
        self,
        data_source: DatabaseConnection,
        sql_query: str
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Execute SQL query"""
        try:
            result = await self.db.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()
            
            # Convert to list of dicts
            results = [
                {col: self._serialize_value(val) for col, val in zip(columns, row)}
                for row in rows
            ]
            
            return results, None
            
        except Exception as e:
            logger.error("query.execution_error", error=str(e), sql=sql_query)
            return [], str(e)
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize value for JSON"""
        from datetime import datetime, date
        from decimal import Decimal
        from uuid import UUID
        
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, UUID):
            return str(value)
        elif isinstance(value, bytes):
            return value.decode('utf-8', errors='replace')
        return value
    
    def _suggest_visualization(
        self,
        results: List[Dict[str, Any]],
        sql_query: str
    ) -> Optional[Dict[str, Any]]:
        """Suggest visualization configuration"""
        if not results or len(results) == 0:
            return None
        
        num_rows = len(results)
        num_cols = len(results[0].keys()) if results else 0
        sql_lower = sql_query.lower()
        
        # Time series detection
        if any(keyword in sql_lower for keyword in ["date", "time", "timestamp"]) and num_rows > 2:
            return {
                "type": "line_chart",
                "title": "Trend Over Time",
                "suggested": True
            }
        
        # Group by → bar chart
        if "group by" in sql_lower and num_rows <= 20:
            return {
                "type": "bar_chart",
                "title": "Comparison",
                "suggested": True
            }
        
        # Count → bar chart
        if "count(" in sql_lower:
            return {
                "type": "bar_chart",
                "title": "Count Distribution",
                "suggested": True
            }
        
        # Default: table
        return {
            "type": "table",
            "title": "Results",
            "suggested": False
        }
    
    def _generate_suggestions(
        self,
        results: List[Dict[str, Any]],
        sql_query: str,
        original_question: str
    ) -> List[str]:
        """Generate suggested follow-up actions"""
        suggestions = []
        
        if len(results) > 0:
            sql_lower = sql_query.lower()
            
            # If not grouped, suggest grouping
            if "group by" not in sql_lower:
                suggestions.append("Show me by category")
                suggestions.append("Break this down by region")
            
            # If no limit, suggest top N
            if "limit" not in sql_lower:
                suggestions.append("Show me top 10")
            
            # If no time filter, suggest time-based
            if "date" not in sql_lower and "time" not in sql_lower:
                suggestions.append("Show me for this year")
                suggestions.append("Compare to last month")
            
            # Always offer export
            suggestions.append("Export these results")
        
        return suggestions[:3]  # Max 3 suggestions
    
    def _format_discovery_response(
        self,
        data_sources: List[DatabaseConnection]
    ) -> str:
        """Format discovery response message"""
        if len(data_sources) == 0:
            return "I couldn't find any data sources matching your query."
        
        count = len(data_sources)
        response = f"I found {count} data source{'s' if count > 1 else ''} that might help:\n\n"
        
        for ds in data_sources:
            response += f"• **{ds.display_name}**"
            if ds.description:
                response += f" - {ds.description[:100]}"
            response += "\n"
        
        response += "\nPlease select a data source to continue."
        return response
    
    def _format_query_response(
        self,
        results: List[Dict[str, Any]],
        explanation: str
    ) -> str:
        """Format query result response message"""
        count = len(results)
        
        if count == 0:
            return "I executed your query but didn't find any results."
        
        response = f"I found {count} result{'s' if count != 1 else ''}.\n\n"
        
        if explanation:
            response += f"{explanation}\n\n"
        
        # Add quick summary for small result sets
        if count <= 3 and results:
            response += "Here's what I found:\n"
            for i, row in enumerate(results[:3], 1):
                row_str = ", ".join([f"{k}: {v}" for k, v in list(row.items())[:3]])
                response += f"{i}. {row_str}\n"
        
        return response
    
    async def _error_response(
        self,
        session,
        error_message: str,
        error_code: str,
        sql_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create error response"""
        await self.session_manager.add_message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content=error_message,
            message_type=MessageType.ERROR,
            sql_query=sql_query,
            error_message=error_message,
            error_code=error_code
        )
        
        return {
            "session_id": session.id,
            "message_type": "error",
            "content": error_message,
            "error_code": error_code,
            "sql_query": sql_query
        }


def get_query_orchestrator(db: AsyncSession, user: User) -> QueryOrchestrator:
    """Factory function to create QueryOrchestrator"""
    return QueryOrchestrator(db, user)

