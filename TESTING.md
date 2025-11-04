# Testing AgentMedha

This guide covers testing strategies and procedures for AgentMedha.

## Table of Contents

1. [Test Structure](#test-structure)
2. [Running Tests](#running-tests)
3. [Backend Testing](#backend-testing)
4. [Frontend Testing](#frontend-testing)
5. [Integration Testing](#integration-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)

## Test Structure

```
agentmedha/
├── backend/
│   └── app/
│       └── tests/
│           ├── conftest.py        # Pytest fixtures
│           ├── test_api.py        # API tests
│           ├── test_services.py   # Service tests
│           └── test_agents.py     # Agent tests
├── frontend/
│   └── src/
│       └── __tests__/
│           ├── components/        # Component tests
│           ├── hooks/             # Hook tests
│           └── utils/             # Utility tests
└── scripts/
    └── verify_setup.sh           # Setup verification
```

## Running Tests

### Quick Test Run

```bash
# Backend tests
cd backend
poetry run pytest

# Frontend tests
cd frontend
npm test

# Verify setup
./scripts/verify_setup.sh
```

### With Coverage

```bash
# Backend with coverage
cd backend
poetry run pytest --cov=app --cov-report=html

# Frontend with coverage
cd frontend
npm test -- --coverage
```

## Backend Testing

### Unit Tests

Test individual functions and classes:

```bash
# Run all unit tests
poetry run pytest -m unit

# Run specific test file
poetry run pytest app/tests/test_services.py

# Run specific test
poetry run pytest app/tests/test_services.py::test_password_hashing -v
```

### API Tests

Test REST endpoints:

```bash
# Run API tests
poetry run pytest app/tests/test_api.py

# Test specific endpoint
poetry run pytest app/tests/test_api.py::test_health_check -v
```

### Agent Tests

Test AI agent functionality:

```bash
# Run agent tests
poetry run pytest app/tests/test_agents.py

# Skip slow tests
poetry run pytest -m "not slow"
```

### Testing Best Practices

1. **Use Fixtures**: Leverage pytest fixtures for common setup
2. **Mock External Services**: Mock LLM calls, external APIs
3. **Test Edge Cases**: Include error conditions, invalid inputs
4. **Keep Tests Fast**: Mock expensive operations
5. **Isolate Tests**: Each test should be independent

Example test:

```python
@pytest.mark.asyncio
async def test_user_registration(async_client):
    """Test user can register successfully."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepass123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "hashed_password" not in data
```

## Frontend Testing

### Component Tests

Test React components with React Testing Library:

```bash
# Run component tests
npm test src/components

# Watch mode for development
npm test -- --watch
```

### Hook Tests

Test custom React hooks:

```bash
npm test src/hooks
```

### Integration Tests

Test user flows:

```bash
npm test src/__tests__/integration
```

### Frontend Testing Best Practices

1. **Test User Behavior**: Focus on what users see and do
2. **Avoid Implementation Details**: Don't test internal state
3. **Use Data-Testid**: For complex queries
4. **Mock API Calls**: Use MSW or similar tools
5. **Test Accessibility**: Include a11y tests

Example test:

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryPage } from './QueryPage';

test('user can submit a query', async () => {
  render(<QueryPage />);
  
  const input = screen.getByPlaceholderText(/enter your question/i);
  await userEvent.type(input, 'Show me total sales');
  
  const button = screen.getByRole('button', { name: /submit/i });
  await userEvent.click(button);
  
  await waitFor(() => {
    expect(screen.getByText(/results/i)).toBeInTheDocument();
  });
});
```

## Integration Testing

Test complete workflows across services:

### Manual Integration Testing

1. **Start Infrastructure**:
```bash
docker-compose up -d
```

2. **Start Backend**:
```bash
cd backend
poetry run uvicorn app.main:app --reload
```

3. **Start Frontend**:
```bash
cd frontend
npm run dev
```

4. **Test Workflows**:
   - User registration and login
   - Database connection setup
   - Query submission and results
   - Visualization rendering

### Automated Integration Testing

```bash
# Run integration test suite
./scripts/run_integration_tests.sh
```

## Performance Testing

### Backend Performance

```bash
# Load testing with locust
cd backend
poetry run locust -f tests/locustfile.py
```

### Query Performance

Monitor:
- SQL generation time
- Query execution time
- Response time
- Token usage

### Frontend Performance

```bash
# Lighthouse CI
npm run lighthouse

# Bundle size analysis
npm run analyze
```

## Security Testing

### Backend Security

1. **Authentication Tests**:
```bash
poetry run pytest app/tests/test_auth.py
```

2. **SQL Injection Tests**:
```bash
poetry run pytest app/tests/test_security.py::test_sql_injection
```

3. **Rate Limiting Tests**:
```bash
poetry run pytest app/tests/test_rate_limiting.py
```

### Frontend Security

1. **XSS Protection**: Test input sanitization
2. **CSRF Protection**: Verify token validation
3. **Secure Storage**: Test token storage

### Security Scanning

```bash
# Backend dependency scan
poetry run safety check

# Frontend dependency scan
npm audit

# Code quality scan
poetry run bandit -r app/
```

## Continuous Integration

Tests run automatically on:

- **Pull Requests**: All tests must pass
- **Main Branch**: Full test suite + integration tests
- **Pre-Deployment**: Security scans + performance tests

### CI Configuration

See `.github/workflows/tests.yml` for GitHub Actions configuration.

## Test Data Management

### Test Fixtures

Located in `backend/app/tests/fixtures/`:
- Sample database schemas
- Example queries
- Mock LLM responses

### Test Database

- Uses in-memory SQLite for speed
- Isolated per test session
- Automatically cleaned up

## Debugging Tests

### Backend Debugging

```bash
# Run with debugger
poetry run pytest --pdb

# Verbose output
poetry run pytest -vv

# Show print statements
poetry run pytest -s
```

### Frontend Debugging

```bash
# Debug mode
npm test -- --debug

# Update snapshots
npm test -- -u
```

## Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| API Endpoints | 100% |
| Services | 90%+ |
| Agents | 85%+ |
| Models | 80%+ |
| Frontend Components | 80%+ |
| Frontend Hooks | 90%+ |

## Reporting Issues

When tests fail:

1. **Check Logs**: Review test output and logs
2. **Reproduce Locally**: Verify the failure locally
3. **Document**: Include error messages and stack traces
4. **Create Issue**: File a GitHub issue with details

## Further Reading

- [Pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Best Practices](https://testingjavascript.com/)














