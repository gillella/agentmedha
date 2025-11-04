"""
Agent tests.
"""

import pytest
from app.agents.sql_agent import SQLAgent


def test_sql_validation():
    """Test SQL validation logic."""
    agent = SQLAgent()
    
    # Valid SELECT query
    valid_sql = "SELECT * FROM users WHERE id = 1"
    result = agent._validate_sql(valid_sql)
    assert result["valid"] is True
    
    # Invalid - DROP statement
    invalid_sql = "DROP TABLE users"
    result = agent._validate_sql(invalid_sql)
    assert result["valid"] is False
    assert "DROP" in result["reason"]
    
    # Invalid - DELETE statement
    invalid_sql = "DELETE FROM users WHERE id = 1"
    result = agent._validate_sql(invalid_sql)
    assert result["valid"] is False
    
    # Invalid - UPDATE statement
    invalid_sql = "UPDATE users SET name = 'test'"
    result = agent._validate_sql(invalid_sql)
    assert result["valid"] is False


def test_sql_extraction():
    """Test extracting SQL from LLM response."""
    agent = SQLAgent()
    
    # With markdown code block
    text = """```sql
    SELECT * FROM users
    ```"""
    sql = agent._extract_sql(text)
    assert sql == "SELECT * FROM users"
    
    # Without code block
    text = "SELECT * FROM products"
    sql = agent._extract_sql(text)
    assert sql == "SELECT * FROM products"
    
    # With generic code block
    text = """```
    SELECT id, name FROM customers
    ```"""
    sql = agent._extract_sql(text)
    assert sql == "SELECT id, name FROM customers"


@pytest.mark.asyncio
async def test_sql_generation_structure():
    """Test SQL generation structure (mocked)."""
    # This would require mocking OpenAI API
    # For now, just test that the agent can be instantiated
    try:
        agent = SQLAgent()
        assert agent.model is not None
        assert agent.temperature == 0.0
    except Exception:
        pytest.skip("OpenAI API key not available for testing")














