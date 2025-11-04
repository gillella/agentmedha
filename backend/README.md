# AgentMedha Backend

FastAPI-based backend for AgentMedha - AI-powered Data Analytics & Business Intelligence Agent.

## Quick Start

```bash
# Install dependencies
poetry install

# Create .env file
cp .env.example .env
# Edit .env and add OPENAI_API_KEY

# Run database migrations
poetry run alembic upgrade head

# Start the server
poetry run uvicorn app.main:app --reload
```

## Documentation

See the main project README and documentation in the root directory.

## API Documentation

When running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json














