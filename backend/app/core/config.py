"""
Application Configuration
Implements 12 Factor Agents Principle #3: Configuration Management
All configuration from environment variables, separate from code.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="BI Agent API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    allowed_origins: str = Field(
        default="http://localhost:3000", alias="ALLOWED_ORIGINS"
    )

    @field_validator("allowed_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        return [origin.strip() for origin in v.split(",")]

    # Security
    secret_key: str = Field(..., alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(
        default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # LLM Configuration
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field(
        default="gpt-4-turbo-2024-04-09", alias="OPENAI_MODEL"
    )
    openai_temperature: float = Field(default=0.0, alias="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=2000, alias="OPENAI_MAX_TOKENS")

    # Alternative LLM
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(
        default="claude-3-sonnet-20240229", alias="ANTHROPIC_MODEL"
    )

    # Database
    database_url: str = Field(..., alias="DATABASE_URL")
    database_pool_size: int = Field(default=10, alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, alias="DATABASE_MAX_OVERFLOW")
    database_pool_recycle: int = Field(default=3600, alias="DATABASE_POOL_RECYCLE")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")

    # Vector Database
    pinecone_api_key: Optional[str] = Field(default=None, alias="PINECONE_API_KEY")
    pinecone_environment: str = Field(
        default="us-west1-gcp-free", alias="PINECONE_ENVIRONMENT"
    )
    pinecone_index: str = Field(default="bi-agent-queries", alias="PINECONE_INDEX")

    # Vanna.AI
    vanna_api_key: Optional[str] = Field(default=None, alias="VANNA_API_KEY")
    vanna_model: str = Field(default="bi-agent-model", alias="VANNA_MODEL")

    # Rate Limiting
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, alias="RATE_LIMIT_PERIOD")

    # Query Configuration
    max_query_timeout: int = Field(default=60, alias="MAX_QUERY_TIMEOUT")
    max_result_rows: int = Field(default=100000, alias="MAX_RESULT_ROWS")
    default_result_limit: int = Field(default=1000, alias="DEFAULT_RESULT_LIMIT")

    # Monitoring
    prometheus_port: int = Field(default=9090, alias="PROMETHEUS_PORT")
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    enable_tracing: bool = Field(default=False, alias="ENABLE_TRACING")
    jaeger_agent_host: str = Field(default="localhost", alias="JAEGER_AGENT_HOST")
    jaeger_agent_port: int = Field(default=6831, alias="JAEGER_AGENT_PORT")

    # Email (optional)
    smtp_host: Optional[str] = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, alias="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: Optional[str] = Field(default=None, alias="SMTP_FROM")

    # Slack (optional)
    slack_webhook_url: Optional[str] = Field(default=None, alias="SLACK_WEBHOOK_URL")
    slack_bot_token: Optional[str] = Field(default=None, alias="SLACK_BOT_TOKEN")

    # Feature Flags
    enable_query_caching: bool = Field(default=True, alias="ENABLE_QUERY_CACHING")
    enable_semantic_search: bool = Field(
        default=True, alias="ENABLE_SEMANTIC_SEARCH"
    )
    enable_auto_insights: bool = Field(default=True, alias="ENABLE_AUTO_INSIGHTS")
    enable_predictive_analytics: bool = Field(
        default=False, alias="ENABLE_PREDICTIVE_ANALYTICS"
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Convenience export
settings = get_settings()

