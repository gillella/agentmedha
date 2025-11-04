"""
Database Connector Service
Implements 12 Factor Agents Principle #4: External Tool Integration
Provides abstraction over multiple database types.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import structlog
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

logger = structlog.get_logger()


class DatabaseConnector(ABC):
    """Abstract base class for database connectors."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine: Optional[Engine] = None
        self._connected = False

    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    def execute_query(self, sql: str, timeout: int = 60) -> List[Dict[str, Any]]:
        """Execute SQL query and return results."""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema metadata."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if connection is healthy."""
        pass


class PostgreSQLConnector(DatabaseConnector):
    """PostgreSQL database connector."""

    def connect(self) -> None:
        """Connect to PostgreSQL database."""
        try:
            self.engine = create_engine(
                self.connection_string,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 10},
            )
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self._connected = True
            logger.info("database.postgresql.connected")
        except Exception as e:
            logger.error("database.postgresql.connection_failed", error=str(e))
            raise

    def disconnect(self) -> None:
        """Disconnect from PostgreSQL."""
        if self.engine:
            self.engine.dispose()
            self._connected = False
            logger.info("database.postgresql.disconnected")

    def execute_query(self, sql: str, timeout: int = 60) -> List[Dict[str, Any]]:
        """Execute query on PostgreSQL."""
        if not self._connected or not self.engine:
            raise RuntimeError("Not connected to database")

        try:
            with self.engine.connect() as conn:
                # Set query timeout
                conn.execute(text(f"SET statement_timeout = {timeout * 1000}"))
                
                # Execute query
                result = conn.execute(text(sql))
                
                # Convert to list of dicts
                columns = result.keys()
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                
                logger.info(
                    "database.query_executed",
                    database_type="postgresql",
                    row_count=len(rows),
                )
                
                return rows
                
        except SQLAlchemyError as e:
            logger.error(
                "database.query_failed",
                database_type="postgresql",
                error=str(e),
                sql=sql[:100],  # Log first 100 chars
            )
            raise

    def get_schema(self) -> Dict[str, Any]:
        """Get PostgreSQL schema."""
        if not self._connected or not self.engine:
            raise RuntimeError("Not connected to database")

        inspector = inspect(self.engine)
        schema = {"tables": {}}

        for table_name in inspector.get_table_names():
            table_info = {
                "name": table_name,
                "columns": [],
                "primary_keys": [],
                "foreign_keys": [],
                "indexes": [],
            }

            # Get columns
            for column in inspector.get_columns(table_name):
                table_info["columns"].append({
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                    "default": column.get("default"),
                })

            # Get primary keys
            pk = inspector.get_pk_constraint(table_name)
            table_info["primary_keys"] = pk.get("constrained_columns", [])

            # Get foreign keys
            for fk in inspector.get_foreign_keys(table_name):
                table_info["foreign_keys"].append({
                    "columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                })

            # Get indexes
            for index in inspector.get_indexes(table_name):
                table_info["indexes"].append({
                    "name": index["name"],
                    "columns": index["column_names"],
                    "unique": index.get("unique", False),
                })

            schema["tables"][table_name] = table_info

        logger.info(
            "database.schema_extracted",
            database_type="postgresql",
            table_count=len(schema["tables"]),
        )

        return schema

    def test_connection(self) -> bool:
        """Test PostgreSQL connection."""
        try:
            if not self.engine:
                return False
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False


class MySQLConnector(DatabaseConnector):
    """MySQL database connector."""

    def connect(self) -> None:
        """Connect to MySQL database."""
        try:
            # Convert postgresql+asyncpg to mysql+pymysql if needed
            connection_string = self.connection_string.replace(
                "postgresql", "mysql+pymysql"
            )
            
            self.engine = create_engine(
                connection_string,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 10},
            )
            
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self._connected = True
            logger.info("database.mysql.connected")
        except Exception as e:
            logger.error("database.mysql.connection_failed", error=str(e))
            raise

    def disconnect(self) -> None:
        """Disconnect from MySQL."""
        if self.engine:
            self.engine.dispose()
            self._connected = False
            logger.info("database.mysql.disconnected")

    def execute_query(self, sql: str, timeout: int = 60) -> List[Dict[str, Any]]:
        """Execute query on MySQL."""
        if not self._connected or not self.engine:
            raise RuntimeError("Not connected to database")

        try:
            with self.engine.connect() as conn:
                # Set query timeout for MySQL
                conn.execute(text(f"SET SESSION max_execution_time = {timeout * 1000}"))
                
                result = conn.execute(text(sql))
                columns = result.keys()
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                
                logger.info(
                    "database.query_executed",
                    database_type="mysql",
                    row_count=len(rows),
                )
                
                return rows
                
        except SQLAlchemyError as e:
            logger.error(
                "database.query_failed",
                database_type="mysql",
                error=str(e),
                sql=sql[:100],
            )
            raise

    def get_schema(self) -> Dict[str, Any]:
        """Get MySQL schema (similar to PostgreSQL)."""
        return self._get_generic_schema("mysql")

    def test_connection(self) -> bool:
        """Test MySQL connection."""
        try:
            if not self.engine:
                return False
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def _get_generic_schema(self, db_type: str) -> Dict[str, Any]:
        """Generic schema extraction (works for most SQL databases)."""
        if not self._connected or not self.engine:
            raise RuntimeError("Not connected to database")

        inspector = inspect(self.engine)
        schema = {"tables": {}}

        for table_name in inspector.get_table_names():
            table_info = {
                "name": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                    }
                    for col in inspector.get_columns(table_name)
                ],
            }
            schema["tables"][table_name] = table_info

        return schema


class DatabaseConnectorFactory:
    """
    Factory for creating database connectors.
    Implements 12 Factor Agents Principle #4: External Tool Integration
    """

    @staticmethod
    def create(connection_string: str) -> DatabaseConnector:
        """
        Create appropriate connector based on connection string.
        
        Args:
            connection_string: Database connection URL
            
        Returns:
            DatabaseConnector instance
            
        Raises:
            ValueError: If database type is not supported
        """
        parsed = urlparse(connection_string)
        scheme = parsed.scheme.lower()

        if "postgresql" in scheme or "postgres" in scheme:
            return PostgreSQLConnector(connection_string)
        elif "mysql" in scheme:
            return MySQLConnector(connection_string)
        else:
            raise ValueError(f"Unsupported database type: {scheme}")

    @staticmethod
    def get_supported_types() -> List[str]:
        """Get list of supported database types."""
        return ["postgresql", "mysql"]














