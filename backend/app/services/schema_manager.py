"""
Schema Manager Service
Manages database schema metadata, documentation, and semantic search.
Implements RAG (Retrieval Augmented Generation) for query generation.
"""

from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy import inspect

from app.services.cache import cache
from app.services.database_connector import DatabaseConnector, DatabaseConnectorFactory

logger = structlog.get_logger()


class SchemaManager:
    """
    Manages database schema metadata and semantic search.
    
    Features:
    - Schema discovery and caching
    - Documentation management
    - Semantic search for relevant tables
    - Query example storage
    """

    def __init__(self):
        self._schema_cache: Dict[int, Dict] = {}

    async def get_schema(
        self,
        database_id: int,
        connection_string: str,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Get database schema with caching.
        
        Args:
            database_id: Database connection ID
            connection_string: Database connection URL
            force_refresh: Force schema refresh
            
        Returns:
            Schema metadata dictionary
        """
        # Check cache first
        if not force_refresh:
            cached_schema = await cache.get_schema(database_id)
            if cached_schema:
                logger.info(
                    "schema.cache_hit",
                    database_id=database_id,
                )
                return cached_schema

        # Connect and extract schema
        connector = DatabaseConnectorFactory.create(connection_string)
        
        try:
            connector.connect()
            schema = connector.get_schema()
            
            # Cache the schema
            await cache.set_schema(database_id, schema, ttl=3600)  # 1 hour
            
            logger.info(
                "schema.extracted",
                database_id=database_id,
                table_count=len(schema.get("tables", {})),
            )
            
            return schema
            
        finally:
            connector.disconnect()

    def get_schema_summary(self, schema: Dict[str, Any]) -> str:
        """
        Generate human-readable schema summary for LLM prompts.
        
        Args:
            schema: Schema metadata dictionary
            
        Returns:
            Formatted schema description
        """
        tables = schema.get("tables", {})
        
        summary_parts = []
        
        for table_name, table_info in tables.items():
            # Table header
            summary_parts.append(f"\nTable: {table_name}")
            
            # Columns
            summary_parts.append("Columns:")
            for col in table_info.get("columns", []):
                col_desc = f"  - {col['name']} ({col['type']})"
                if not col.get("nullable", True):
                    col_desc += " NOT NULL"
                summary_parts.append(col_desc)
            
            # Primary keys
            primary_keys = table_info.get("primary_keys", [])
            if primary_keys:
                summary_parts.append(f"Primary Key: {', '.join(primary_keys)}")
            
            # Foreign keys
            foreign_keys = table_info.get("foreign_keys", [])
            if foreign_keys:
                summary_parts.append("Foreign Keys:")
                for fk in foreign_keys:
                    fk_desc = (
                        f"  - {fk['columns']} -> "
                        f"{fk['referred_table']}.{fk['referred_columns']}"
                    )
                    summary_parts.append(fk_desc)
        
        return "\n".join(summary_parts)

    def get_detailed_schema(
        self, 
        schema: Dict[str, Any], 
        table_names: List[str]
    ) -> str:
        """
        Get detailed schema information for specific tables.
        
        Args:
            schema: Full schema dictionary
            table_names: List of table names to include
            
        Returns:
            Detailed schema description
        """
        tables = schema.get("tables", {})
        
        # Filter to requested tables
        filtered_tables = {
            name: info
            for name, info in tables.items()
            if name in table_names
        }
        
        # Add related tables (via foreign keys)
        related_tables = set()
        for table_info in filtered_tables.values():
            for fk in table_info.get("foreign_keys", []):
                related_table = fk.get("referred_table")
                if related_table and related_table not in filtered_tables:
                    related_tables.add(related_table)
        
        # Include related tables
        for related_table in related_tables:
            if related_table in tables:
                filtered_tables[related_table] = tables[related_table]
        
        # Generate detailed description
        return self.get_schema_summary({"tables": filtered_tables})

    def find_relevant_tables(
        self, 
        question: str, 
        schema: Dict[str, Any]
    ) -> List[str]:
        """
        Find tables relevant to the user's question.
        
        Uses simple keyword matching for now.
        TODO: Integrate with vector store for semantic search.
        
        Args:
            question: Natural language question
            schema: Database schema
            
        Returns:
            List of relevant table names
        """
        question_lower = question.lower()
        tables = schema.get("tables", {})
        
        relevant = []
        
        for table_name, table_info in tables.items():
            # Check table name
            if table_name.lower() in question_lower:
                relevant.append(table_name)
                continue
            
            # Check column names
            for col in table_info.get("columns", []):
                col_name = col["name"].lower()
                if col_name in question_lower or col_name.replace("_", " ") in question_lower:
                    if table_name not in relevant:
                        relevant.append(table_name)
                    break
        
        # If no matches, return all tables (for simple schemas)
        if not relevant and len(tables) <= 10:
            relevant = list(tables.keys())
        
        logger.info(
            "schema.relevant_tables_found",
            question_preview=question[:50],
            table_count=len(relevant),
            tables=relevant,
        )
        
        return relevant

    def get_table_sample(
        self,
        connection_string: str,
        table_name: str,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Get sample rows from a table.
        
        Args:
            connection_string: Database connection URL
            table_name: Table to sample
            limit: Number of rows to return
            
        Returns:
            List of sample rows
        """
        connector = DatabaseConnectorFactory.create(connection_string)
        
        try:
            connector.connect()
            sql = f"SELECT * FROM {table_name} LIMIT {limit}"
            rows = connector.execute_query(sql)
            return rows
        except Exception as e:
            logger.warning(
                "schema.sample_failed",
                table_name=table_name,
                error=str(e),
            )
            return []
        finally:
            connector.disconnect()

    async def store_successful_query(
        self,
        database_id: int,
        question: str,
        sql: str,
        success: bool,
    ) -> None:
        """
        Store a query example for future reference.
        
        TODO: Implement vector store integration for semantic search.
        
        Args:
            database_id: Database connection ID
            question: Natural language question
            sql: Generated SQL
            success: Whether query was successful
        """
        # For now, just log it
        logger.info(
            "schema.query_stored",
            database_id=database_id,
            question_preview=question[:50],
            success=success,
        )
        
        # TODO: Store in vector database for RAG
        # await vector_store.upsert_query(...)

    def get_similar_queries(
        self,
        database_id: int,
        question: str,
        top_k: int = 3,
    ) -> List[Dict[str, str]]:
        """
        Find similar historical queries.
        
        TODO: Implement vector store integration.
        
        Args:
            database_id: Database connection ID
            question: Natural language question
            top_k: Number of similar queries to return
            
        Returns:
            List of similar query examples
        """
        # Placeholder - return empty for now
        # TODO: Query vector store
        return []


# Global schema manager instance
schema_manager = SchemaManager()














