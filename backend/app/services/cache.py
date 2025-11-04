"""
Redis Cache Service
Implements caching for query results, schema metadata, and sessions.
Principle #6: Stateless Execution - externalize state to Redis
"""

import hashlib
import json
from typing import Any, Optional

from redis import asyncio as aioredis
from redis.asyncio import Redis
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class CacheService:
    """
    Redis-based caching service.
    
    Features:
    - Query result caching
    - Schema metadata caching
    - Session management
    - Rate limiting data
    """

    def __init__(self) -> None:
        self.redis: Optional[Redis] = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis = await aioredis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test connection
            await self.redis.ping()
            self._connected = True
            logger.info("cache.connected", redis_url=settings.redis_url.split("@")[-1])
        except Exception as e:
            logger.error("cache.connection_failed", error=str(e))
            raise

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self._connected = False
            logger.info("cache.disconnected")

    async def ping(self) -> bool:
        """Check if Redis is connected."""
        if not self.redis:
            return False
        try:
            return await self.redis.ping()
        except Exception:
            return False

    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix."""
        return f"{prefix}:{identifier}"

    def _hash_query(self, sql: str, database_id: int) -> str:
        """Generate deterministic hash for SQL query."""
        content = f"{database_id}:{sql.strip().lower()}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._connected or not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("cache.get_failed", key=key, error=str(e))
            return None

    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        if not self._connected or not self.redis:
            return False
        
        try:
            ttl = ttl or settings.cache_ttl
            serialized = json.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning("cache.set_failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._connected or not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning("cache.delete_failed", key=key, error=str(e))
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        Returns number of keys deleted.
        """
        if not self._connected or not self.redis:
            return 0
        
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info("cache.pattern_deleted", pattern=pattern, count=deleted)
                return deleted
            return 0
        except Exception as e:
            logger.warning("cache.delete_pattern_failed", pattern=pattern, error=str(e))
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._connected or not self.redis:
            return False
        
        try:
            return bool(await self.redis.exists(key))
        except Exception:
            return False

    # Query-specific caching methods

    async def get_query_result(
        self, 
        sql: str, 
        database_id: int
    ) -> Optional[dict]:
        """Get cached query result."""
        if not settings.enable_query_caching:
            return None
        
        cache_key = self._hash_query(sql, database_id)
        key = self._generate_key("query_result", cache_key)
        return await self.get(key)

    async def set_query_result(
        self,
        sql: str,
        database_id: int,
        result: dict,
        ttl: Optional[int] = None,
    ) -> str:
        """
        Cache query result.
        Returns the cache key.
        """
        if not settings.enable_query_caching:
            return ""
        
        cache_key = self._hash_query(sql, database_id)
        key = self._generate_key("query_result", cache_key)
        await self.set(key, result, ttl)
        
        logger.info(
            "cache.query_cached",
            cache_key=cache_key,
            database_id=database_id,
            ttl=ttl or settings.cache_ttl,
        )
        
        return cache_key

    # Schema caching

    async def get_schema(self, database_id: int) -> Optional[dict]:
        """Get cached schema metadata."""
        key = self._generate_key("schema", str(database_id))
        return await self.get(key)

    async def set_schema(
        self, 
        database_id: int, 
        schema: dict, 
        ttl: int = 3600
    ) -> bool:
        """Cache schema metadata (1 hour TTL by default)."""
        key = self._generate_key("schema", str(database_id))
        return await self.set(key, schema, ttl)

    # Session management

    async def set_session(
        self, 
        session_id: str, 
        data: dict, 
        ttl: int = 900
    ) -> bool:
        """Store session data (15 min TTL by default)."""
        key = self._generate_key("session", session_id)
        return await self.set(key, data, ttl)

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        key = self._generate_key("session", session_id)
        return await self.get(key)

    async def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        key = self._generate_key("session", session_id)
        return await self.delete(key)

    # Rate limiting

    async def check_rate_limit(
        self, 
        user_id: int, 
        limit: int = 100, 
        window: int = 60
    ) -> tuple[bool, int]:
        """
        Check if user has exceeded rate limit.
        Returns (is_allowed, remaining_requests).
        """
        key = self._generate_key("rate_limit", f"{user_id}:{window}")
        
        if not self.redis:
            return True, limit
        
        try:
            current = await self.redis.get(key)
            
            if current is None:
                # First request in window
                await self.redis.setex(key, window, "1")
                return True, limit - 1
            
            count = int(current)
            
            if count >= limit:
                return False, 0
            
            # Increment counter
            await self.redis.incr(key)
            return True, limit - count - 1
            
        except Exception as e:
            logger.warning("rate_limit.check_failed", user_id=user_id, error=str(e))
            return True, limit  # Fail open


# Global cache instance
cache = CacheService()



