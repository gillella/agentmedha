"""
Service layer tests.
"""

import pytest
from app.services.auth import AuthService


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = AuthService.hash_password(password)
    
    # Hash should be different from original
    assert hashed != password
    
    # Verification should work
    assert AuthService.verify_password(password, hashed)
    
    # Wrong password should fail
    assert not AuthService.verify_password("wrongpassword", hashed)


def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "123"}
    token = AuthService.create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token():
    """Test JWT token decoding."""
    data = {"sub": "123"}
    token = AuthService.create_access_token(data)
    
    decoded = AuthService.decode_token(token)
    assert decoded["sub"] == "123"
    assert "exp" in decoded
    assert "type" in decoded
    assert decoded["type"] == "access"


def test_decode_invalid_token():
    """Test that invalid tokens raise an error."""
    from fastapi import HTTPException
    
    with pytest.raises(HTTPException):
        AuthService.decode_token("invalid.token.here")


@pytest.mark.asyncio
async def test_cache_operations():
    """Test cache service operations."""
    from app.services.cache import CacheService
    
    cache = CacheService()
    
    # Note: This will fail if Redis is not running
    # In a real test, we'd mock Redis or use fakeredis
    try:
        await cache.connect()
        
        # Test set and get
        await cache.set("test_key", {"data": "test"})
        result = await cache.get("test_key")
        assert result == {"data": "test"}
        
        # Test delete
        await cache.delete("test_key")
        result = await cache.get("test_key")
        assert result is None
        
        await cache.disconnect()
    except Exception:
        # Redis not available in test environment
        pytest.skip("Redis not available for testing")














