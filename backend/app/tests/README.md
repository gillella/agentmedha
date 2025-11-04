# Testing Guide

This directory contains tests for the AgentMedha backend.

## Test Structure

```
tests/
├── conftest.py           # Pytest fixtures and configuration
├── test_api.py          # API endpoint tests
├── test_services.py     # Service layer tests
└── test_agents.py       # Agent tests
```

## Running Tests

### Run All Tests
```bash
cd backend
poetry run pytest
```

### Run Specific Test File
```bash
poetry run pytest app/tests/test_api.py
```

### Run with Coverage
```bash
poetry run pytest --cov=app --cov-report=html
```

### Run Specific Test
```bash
poetry run pytest app/tests/test_api.py::test_health_check -v
```

## Test Database

Tests use an in-memory SQLite database that is created and destroyed for each test session.

## Writing Tests

### Unit Tests
Test individual functions and methods in isolation:

```python
def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = AuthService.hash_password(password)
    assert AuthService.verify_password(password, hashed)
```

### Async Tests
Use `@pytest.mark.asyncio` for async tests:

```python
@pytest.mark.asyncio
async def test_register_user(async_client):
    """Test user registration."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
```

### Using Fixtures
Fixtures are defined in `conftest.py`:

```python
async def test_with_user(test_user, auth_token):
    """Test with authenticated user."""
    # test_user provides a test user instance
    # auth_token provides a JWT token for that user
    assert test_user.email == "test@example.com"
```

## Test Coverage Goals

- **API Endpoints**: 100% - all endpoints should have tests
- **Services**: 90%+ - critical business logic fully covered
- **Models**: 80%+ - test relationships and constraints
- **Agents**: 80%+ - test core functionality (may mock LLM calls)

## Mocking External Services

For external services (Redis, LLMs, etc.), use mocking:

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock_llm():
    with patch('openai.AsyncOpenAI') as mock_client:
        mock_client.return_value.chat.completions.create = AsyncMock(
            return_value={"choices": [{"message": {"content": "SELECT * FROM users"}}]}
        )
        # Your test here
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Before deployments

## Debugging Tests

### Run with verbose output
```bash
poetry run pytest -v
```

### Run with print statements
```bash
poetry run pytest -s
```

### Run with debugger
```bash
poetry run pytest --pdb
```

## Test Data

Test data is generated using fixtures and factories. Keep test data:
- Minimal but realistic
- Self-documenting (clear variable names)
- Isolated (each test creates its own data)














