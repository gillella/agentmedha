# Getting Started Guide
## Data Analytics & Business Intelligence Agent

This guide will help you set up and run the BI Agent locally for development.

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: [Download here](https://www.python.org/downloads/)
- **Node.js 18+**: [Download here](https://nodejs.org/)
- **Poetry**: Python dependency manager
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```
- **Docker & Docker Compose**: [Get Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Git**: Version control
- **OpenAI API Key**: [Get one here](https://platform.openai.com/)

---

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Data Analytics  and Business Intelligence Agent"
```

### 2. Start Infrastructure Services

```bash
# Start PostgreSQL, Redis, and monitoring tools
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379
- Prometheus on port 9090
- Grafana on port 3001

### 3. Set Up Backend

```bash
cd backend

# Install dependencies
poetry install

# Copy environment file
cp env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY="sk-..."

# Run database migrations
poetry run alembic upgrade head

# Start the API server
poetry run uvicorn app.main:app --reload
```

Backend will be running at: http://localhost:8000

API docs available at: http://localhost:8000/docs

### 4. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be running at: http://localhost:3000

### 5. Test the System

Open your browser to http://localhost:3000 and try asking:

> "What are the top 5 products by revenue?"

---

## Detailed Setup

### Backend Setup

#### 1. Install Python Dependencies

```bash
cd backend
poetry install --with dev
```

#### 2. Configure Environment

Edit `backend/.env` with your settings:

```bash
# Required
OPENAI_API_KEY="sk-..."  # Get from https://platform.openai.com/

# Database (default works with docker-compose)
DATABASE_URL="postgresql+asyncpg://biagent:biagent@localhost:5432/biagent"

# Redis (default works with docker-compose)
REDIS_URL="redis://localhost:6379/0"

# Optional: Vector Database for semantic search
PINECONE_API_KEY="..."  # Get from https://www.pinecone.io/
```

#### 3. Initialize Database

```bash
# Create database tables
poetry run alembic upgrade head

# (Optional) Seed with sample data
poetry run python scripts/seed_database.py
```

#### 4. Run Backend

```bash
# Development mode (with auto-reload)
poetry run uvicorn app.main:app --reload

# Or with custom host/port
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 5. Verify Backend

Open http://localhost:8000/docs to see the API documentation.

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

### Frontend Setup

#### 1. Install Node Dependencies

```bash
cd frontend
npm install
```

#### 2. Configure Environment

Create `frontend/.env.local`:

```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

#### 3. Run Frontend

```bash
npm run dev
```

Open http://localhost:3000 in your browser.

### Docker Compose Services

The `docker-compose.yml` includes:

```yaml
services:
  postgres:    # Database for metadata
  redis:       # Cache and session store
  prometheus:  # Metrics collection
  grafana:     # Metrics visualization
```

Useful commands:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Reset everything (⚠️ deletes data)
docker-compose down -v
```

---

## Connecting Your Database

To analyze your own data, you need to connect a database:

### Option 1: Via UI (Easiest)

1. Open http://localhost:3000
2. Go to Settings → Databases
3. Click "Add Database"
4. Fill in connection details:
   - **Name**: My Database
   - **Type**: PostgreSQL / MySQL / Snowflake / BigQuery
   - **Host**: database-hostname
   - **Port**: 5432 (PostgreSQL default)
   - **Database**: your_database_name
   - **Username**: your_username
   - **Password**: your_password
5. Click "Test Connection"
6. If successful, click "Save"

### Option 2: Via API

```bash
curl -X POST http://localhost:8000/api/v1/databases \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Database",
    "type": "postgresql",
    "connection_string": "postgresql://user:pass@host:5432/dbname"
  }'
```

### Option 3: Environment Variable

Add to `backend/.env`:

```bash
# Target database to analyze
TARGET_DB_URL="postgresql://user:pass@host:5432/dbname"
```

---

## Testing Your First Query

### Via UI

1. Open http://localhost:3000
2. Select your connected database
3. Type a question in natural language:
   - "Show me total sales by month"
   - "What are the top 10 customers by revenue?"
   - "How many orders were placed today?"
4. Press Enter or click "Ask"
5. View the generated SQL, results, and visualization

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are total sales by product category?",
    "database_id": "your-database-id"
  }'
```

Response:
```json
{
  "query_id": "abc123",
  "sql": "SELECT category, SUM(amount) FROM sales GROUP BY category",
  "results": [...],
  "visualization": {...},
  "insights": [...]
}
```

---

## Development Workflow

### Running Tests

#### Backend Tests

```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_agents.py

# Run with verbose output
poetry run pytest -v
```

#### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

### Code Quality

#### Backend

```bash
cd backend

# Format code
poetry run black app/
poetry run isort app/

# Lint
poetry run pylint app/
poetry run mypy app/

# Check all
poetry run black --check app/ && \
poetry run isort --check app/ && \
poetry run mypy app/
```

#### Frontend

```bash
cd frontend

# Format code
npm run format

# Lint
npm run lint

# Type check
npm run type-check
```

### Database Migrations

When you change database models:

```bash
cd backend

# Create a new migration
poetry run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
poetry run alembic upgrade head

# Rollback last migration
poetry run alembic downgrade -1
```

---

## Troubleshooting

### Backend won't start

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
cd backend
poetry install
# Make sure you're running commands with 'poetry run'
```

**Problem**: `Connection refused` when connecting to database

**Solution**:
```bash
# Make sure Docker services are running
docker-compose ps

# Restart services
docker-compose restart postgres redis
```

### Frontend won't start

**Problem**: `Module not found` errors

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem**: API requests failing with CORS errors

**Solution**: Check `backend/.env` has correct `ALLOWED_ORIGINS`:
```bash
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173"
```

### LLM API Issues

**Problem**: `Invalid API key` or `Rate limit exceeded`

**Solution**:
- Verify your OpenAI API key in `backend/.env`
- Check your OpenAI account has credits: https://platform.openai.com/usage
- Check rate limits: https://platform.openai.com/account/limits

**Problem**: Queries are slow or timing out

**Solution**:
- Enable query caching: `ENABLE_QUERY_CACHING=true` in `.env`
- Reduce context by limiting schema size
- Use a faster model (though less accurate): `OPENAI_MODEL="gpt-3.5-turbo"`

### Docker Issues

**Problem**: Ports already in use

**Solution**:
```bash
# Find what's using the port
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :8000  # API

# Kill the process or change ports in docker-compose.yml
```

**Problem**: Containers keep restarting

**Solution**:
```bash
# Check logs
docker-compose logs postgres
docker-compose logs redis

# Often it's a permission issue with data volumes
docker-compose down -v  # ⚠️ Deletes data
docker-compose up -d
```

---

## Next Steps

Now that you have the system running:

1. **Connect Your Database**: Follow the "Connecting Your Database" section above
2. **Try Example Queries**: See [EXAMPLES.md](./EXAMPLES.md) for query examples
3. **Explore the API**: Check out the API docs at http://localhost:8000/docs
4. **Read the Architecture**: Understand how it works in [ARCHITECTURE.md](./ARCHITECTURE.md)
5. **Customize Agents**: Learn how to customize agent behavior in [docs/CUSTOMIZATION.md](./docs/CUSTOMIZATION.md)

---

## Getting Help

- **Documentation**: Check the `docs/` folder
- **Examples**: See `EXAMPLES.md` for query examples
- **API Reference**: http://localhost:8000/docs (when running)
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Ask questions on GitHub Discussions

---

## Development Tips

### Hot Reload

Both backend and frontend support hot reload:
- **Backend**: Changes to `app/` automatically reload the server
- **Frontend**: Changes instantly reflect in the browser

### Debugging

#### Backend Debugging (VS Code)

Add to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

#### Frontend Debugging (Chrome DevTools)

1. Open http://localhost:3000
2. Press F12 to open DevTools
3. Set breakpoints in the Sources tab

### Performance Profiling

#### Backend

```bash
cd backend

# Profile with py-spy
poetry add --dev py-spy
poetry run py-spy record -o profile.svg -- python -m uvicorn app.main:app
```

#### Frontend

Use React DevTools Profiler:
1. Install React DevTools extension
2. Open DevTools → Profiler tab
3. Record a session
4. Analyze component render times

---

**Happy Coding! 🚀**

For more help, see our [full documentation](./docs/) or open an issue.

