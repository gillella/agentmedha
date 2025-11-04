# AgentMedha - Quick Start Guide

Get up and running with AgentMedha in 5 minutes!

## Prerequisites

- Docker Desktop installed
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

## Step 1: Environment Setup

Create a `.env` file in the project root:

```bash
# Copy the example
cp .env.example .env

# Edit and add your OpenAI API key
nano .env
```

Minimum required configuration:
```bash
OPENAI_API_KEY="sk-your-key-here"
SECRET_KEY="change-this-to-a-random-32-char-string"
```

## Step 2: Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

## Step 3: Initialize Database

```bash
# Create database tables
docker-compose exec backend python -c "
from app.models.base import init_db
import asyncio
asyncio.run(init_db())
"

# Create demo user (optional)
docker-compose exec backend python -c "
from app.models import User, AsyncSessionLocal
from app.services.auth import AuthService
import asyncio

async def create_demo_user():
    async with AsyncSessionLocal() as db:
        user = User(
            email='admin@agentmedha.com',
            username='admin',
            full_name='Admin User',
            hashed_password=AuthService.hash_password('admin123'),
            is_active=True,
            is_superuser=True
        )
        db.add(user)
        await db.commit()
        print('✅ Demo user created: admin / admin123')

asyncio.run(create_demo_user())
"
```

## Step 4: Access the Application

Open your browser and navigate to:

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

## Step 5: Try Your First Query

1. Login with demo credentials:
   - Username: `admin`
   - Password: `admin123`

2. Ask a question:
   ```
   Show me total sales by region
   ```

3. View the generated SQL and results!

## Common Commands

```bash
# Stop all services
docker-compose stop

# Restart services
docker-compose restart

# View logs
docker-compose logs -f [service_name]

# Access backend shell
docker-compose exec backend bash

# Access database
docker-compose exec db psql -U agentmedha

# Clean up everything
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

```bash
# Change ports in docker-compose.yml
# Default ports: 3000 (frontend), 8000 (backend), 5432 (postgres)
```

### OpenAI API Error

```bash
# Verify your API key is set correctly
docker-compose exec backend printenv | grep OPENAI
```

### Database Connection Error

```bash
# Wait for database to be ready
docker-compose logs db

# Restart backend
docker-compose restart backend
```

### Frontend Not Loading

```bash
# Check backend is running
curl http://localhost:8000/health

# Rebuild frontend
docker-compose up -d --build frontend
```

## Next Steps

- Read the full [Getting Started Guide](./GETTING_STARTED.md)
- Connect your own database
- Customize the configuration
- Explore the [API Documentation](http://localhost:8000/docs)

## Need Help?

- Check the logs: `docker-compose logs`
- Read the [FAQ](./docs/FAQ.md)
- Open an issue on GitHub

---

**Happy querying! 🚀**














