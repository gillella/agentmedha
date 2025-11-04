"""
SQL Agent
Generates SQL queries from natural language using LLM.
Implements 12 Factor Agents Principle #1: Single-Purpose Agents
"""

from typing import Any, Dict, Optional

import structlog
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.schema_manager import SchemaManager
from app.services.context_manager import ContextManager
from app.services.cache import cache

logger = structlog.get_logger()


class SQLAgent:
    """
    Agent responsible for SQL query generation from natural language.
    
    This agent:
    1. Receives analysis plan from Planner Agent
    2. Gets relevant schema information
    3. Generates SQL query using LLM
    4. Validates and formats the query
    
    Principle #1: Single-Purpose Agent - focused only on SQL generation
    """

    def __init__(self, db: Optional[Session] = None):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.schema_manager = SchemaManager()
        self.db = db
        self.context_manager = ContextManager(db=db, cache=cache) if db else None

    async def generate_query(
        self,
        question: str,
        schema: Dict[str, Any],
        database_type: str = "postgresql",
        context: Optional[Dict[str, Any]] = None,
        database_id: Optional[int] = None,
        user_permissions: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Generate SQL query from natural language question.
        
        Args:
            question: Natural language question
            schema: Database schema metadata
            database_type: Type of database (postgresql, mysql, etc.)
            context: Optional context from previous queries
            
        Returns:
            Dictionary with:
                - sql: Generated SQL query
                - explanation: Human-readable explanation
                - confidence: Confidence score (0-1)
        """
        logger.info(
            "sql_agent.generating_query",
            question_preview=question[:50],
            database_type=database_type,
        )

        # Find relevant tables
        relevant_tables = self.schema_manager.find_relevant_tables(question, schema)
        
        # Get detailed schema for relevant tables
        detailed_schema = self.schema_manager.get_detailed_schema(
            schema, relevant_tables
        )
        
        # Get business context (metrics, glossary, rules, examples)
        business_context = None
        if self.context_manager and database_id and user_permissions:
            try:
                context_result = await self.context_manager.get_context_for_query(
                    query=question,
                    database_id=database_id,
                    tables=relevant_tables,
                    user_permissions=user_permissions,
                    max_tokens=4000,  # Reserve space for schema and response
                    include_examples=True,
                    use_cache=True
                )
                business_context = context_result.get("context")
                logger.info(
                    "sql_agent.context_retrieved",
                    context_tokens=context_result["stats"]["context_tokens"],
                    metrics_count=context_result["metadata"]["metrics_count"],
                    cache_hit=context_result["stats"]["cache_hit"]
                )
            except Exception as e:
                logger.warning(
                    "sql_agent.context_retrieval_failed",
                    error=str(e)
                )
                # Continue without business context if retrieval fails
        
        # Build prompt with business context
        prompt = self._build_prompt(
            question=question,
            schema=detailed_schema,
            database_type=database_type,
            business_context=business_context,
            context=context,
        )
        
        # Generate SQL using LLM
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert SQL query generator. "
                            "Generate syntactically correct SQL queries based on "
                            "natural language questions and database schemas."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=settings.openai_max_tokens,
            )
            
            generated_text = response.choices[0].message.content or ""
            
            # Extract SQL from response
            sql = self._extract_sql(generated_text)
            
            # Validate SQL
            validation = self._validate_sql(sql)
            
            if not validation["valid"]:
                logger.warning(
                    "sql_agent.invalid_sql",
                    reason=validation["reason"],
                    sql_preview=sql[:100],
                )
                raise ValueError(f"Invalid SQL: {validation['reason']}")
            
            logger.info(
                "sql_agent.query_generated",
                sql_preview=sql[:100],
                token_usage=response.usage.total_tokens if response.usage else 0,
            )
            
            return {
                "sql": sql,
                "explanation": self._generate_explanation(sql, question),
                "confidence": 0.9,  # Placeholder
                "token_usage": response.usage.total_tokens if response.usage else 0,
            }
            
        except Exception as e:
            logger.error(
                "sql_agent.generation_failed",
                error=str(e),
                question_preview=question[:50],
            )
            raise

    def _build_prompt(
        self,
        question: str,
        schema: str,
        database_type: str,
        business_context: Optional[str],
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Build prompt for LLM with business context."""
        prompt_parts = [
            f"Generate a {database_type.upper()} SQL query for the following question:\n",
            f"Question: {question}\n\n",
        ]
        
        # Add business context (metrics, glossary, rules, examples)
        if business_context:
            prompt_parts.append("=== BUSINESS CONTEXT ===\n")
            prompt_parts.append(business_context)
            prompt_parts.append("\n\n")
        
        # Add database schema
        prompt_parts.append("=== DATABASE SCHEMA ===\n")
        prompt_parts.append(schema)
        prompt_parts.append("\n\n")
        
        # Add context from previous queries
        if context and context.get("previous_query"):
            prompt_parts.append(
                f"Previous query context: {context['previous_query']}\n\n"
            )
        
        prompt_parts.extend([
            "=== REQUIREMENTS ===\n",
            "1. Use business metrics and definitions from the BUSINESS CONTEXT when available\n",
            "2. Apply business rules (fiscal calendar, filters, etc.) from the context\n",
            "3. Use appropriate JOINs based on foreign key relationships in the schema\n",
            "4. Include all necessary WHERE clauses and filters\n",
            "5. Use clear and readable formatting with proper indentation\n",
            "6. Limit results to 1000 rows if not specified\n",
            "7. Use ONLY SELECT statements (no INSERT, UPDATE, DELETE, DROP, etc.)\n",
            "8. Wrap the SQL in ```sql code blocks\n",
            "9. Follow the business glossary for term definitions\n\n",
            "SQL Query:\n",
        ])
        
        return "".join(prompt_parts)

    def _extract_sql(self, text: str) -> str:
        """Extract SQL from LLM response."""
        # Remove markdown code blocks
        text = text.strip()
        
        # Look for SQL code block
        if "```sql" in text.lower():
            start = text.lower().index("```sql") + 6
            end = text.index("```", start)
            sql = text[start:end].strip()
        elif "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            sql = text[start:end].strip()
        else:
            sql = text.strip()
        
        return sql

    def _validate_sql(self, sql: str) -> Dict[str, Any]:
        """
        Validate SQL query for safety.
        
        Returns:
            Dictionary with 'valid' (bool) and 'reason' (str) keys
        """
        sql_upper = sql.upper().strip()
        
        # Check for dangerous operations
        dangerous_keywords = [
            "DROP",
            "DELETE",
            "TRUNCATE",
            "ALTER",
            "CREATE",
            "INSERT",
            "UPDATE",
            "GRANT",
            "REVOKE",
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return {
                    "valid": False,
                    "reason": f"Dangerous keyword detected: {keyword}",
                }
        
        # Must be a SELECT query
        if not sql_upper.startswith("SELECT"):
            return {
                "valid": False,
                "reason": "Only SELECT queries are allowed",
            }
        
        # Basic SQL injection checks
        if ";" in sql and not sql.strip().endswith(";"):
            return {
                "valid": False,
                "reason": "Multiple statements not allowed",
            }
        
        return {"valid": True, "reason": ""}

    def _generate_explanation(self, sql: str, question: str) -> str:
        """Generate human-readable explanation of SQL query."""
        # Simple explanation for now
        return f"This query retrieves data to answer: '{question}'"


# Factory function to create SQL agent with db session
def get_sql_agent(db: Optional[Session] = None) -> SQLAgent:
    """Get SQL agent instance with optional database session for context."""
    return SQLAgent(db=db)

# Global SQL agent instance (without context - for backward compatibility)
sql_agent = SQLAgent()













