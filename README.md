# AgentMedha 🧠

> AI-Powered Data Analytics & Business Intelligence Agent

AgentMedha is an intelligent data analytics platform that enables non-technical users to interact with databases using natural language. Built following the **12 Factor Agents** methodology, it provides enterprise-grade reliability, scalability, and maintainability.

## ✨ Features

- **Natural Language SQL**: Ask questions in plain English, get SQL automatically
- **Multi-Agent System**: Specialized AI agents work together for comprehensive analytics
- **Smart Visualizations**: Automatic chart selection and interactive dashboards
- **Automated Insights**: AI-generated insights and recommendations
- **Enterprise Security**: JWT authentication, RBAC, audit logging
- **Multi-Database Support**: PostgreSQL, MySQL, Snowflake, BigQuery
- **Query Caching**: Smart caching for improved performance
- **Real-time Monitoring**: Prometheus & Grafana integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           React Frontend (Vite)             │
│     Natural Language Query Interface        │
└────────────────┬────────────────────────────┘
                 │ REST API / WebSocket
┌────────────────▼────────────────────────────┐
│         FastAPI Backend (Python)            │
│     ┌───────────────────────────────┐      │
│     │   Multi-Agent Orchestration   │      │
│     │  (LangGraph + LangChain)      │      │
│     │                                │      │
│     │  Planner → SQL → Viz → Insight │      │
│     └───────────────────────────────┘      │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│  PostgreSQL | Redis | Pinecone (optional)  │
│  Metadata | Cache | Vector Store           │
└─────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key
- 8GB RAM minimum

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd agentmedha
```

2. **Set up environment variables**

```bash
# Copy example files
cp .env.example .env
cp backend/env.example backend/.env

# Edit .env and add your OpenAI API key
# Minimum required: OPENAI_API_KEY
```

3. **Start the stack**

```bash
docker-compose up -d
```

4. **Initialize the database**

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create a demo user
docker-compose exec backend python -m app.scripts.create_demo_user
```

5. **Access the application**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### Demo Credentials

- **Username**: `admin`
- **Password**: `admin123`

## 📖 Documentation

- [Getting Started Guide](./GETTING_STARTED.md) - Complete setup instructions
- [Project Plan](./PROJECT_PLAN.md) - Comprehensive development plan
- [Architecture](./ARCHITECTURE.md) - System architecture details
- [Tech Stack](./TECH_STACK.md) - Technology decisions
- [Requirements](./REQUIREMENTS.md) - Functional & non-functional requirements

## 🛠️ Development

### Backend Development

```bash
cd backend

# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload

# Run tests
poetry run pytest

# Format code
poetry run black app/
poetry run isort app/
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

## 🧪 Testing

```bash
# Backend tests
cd backend
poetry run pytest --cov=app tests/

# Frontend tests
cd frontend
npm test
```

## 📊 Monitoring

AgentMedha includes built-in monitoring with Prometheus and Grafana:

- **Metrics endpoint**: http://localhost:8000/metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001

Key metrics tracked:
- Query execution time
- Query success rate
- Agent performance
- Cache hit rate
- API response times

## 🔒 Security

- JWT-based authentication
- Role-based access control (RBAC)
- SQL injection prevention
- Rate limiting
- Audit logging
- Encrypted connections

## 🏢 12 Factor Agents Principles

AgentMedha is built following the [12 Factor Agents](https://mainstream.dev/12-factor-agents) methodology:

1. ✅ **Single-Purpose Agents** - Each agent has one clear responsibility
2. ✅ **Explicit Dependencies** - All dependencies pinned in `pyproject.toml`
3. ✅ **Configuration Management** - Environment variables via Pydantic Settings
4. ✅ **External Tool Integration** - Database abstraction layer
5. ✅ **Deterministic Deployment** - Docker images with reproducible builds
6. ✅ **Stateless Execution** - State externalized to Redis/Database
7. ✅ **Port Binding** - FastAPI self-contained server
8. ✅ **Concurrency** - Horizontal scaling support
9. ✅ **Disposability** - Fast startup (<10s), graceful shutdown
10. ✅ **Dev/Prod Parity** - Same containers and infrastructure
11. ✅ **Logs as Event Streams** - Structured JSON logging to stdout
12. ✅ **Admin Processes** - Database migrations via Alembic

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📧 Support

- **Documentation**: Check the `/docs` directory
- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [OpenAI](https://openai.com/)
- UI components from [Radix UI](https://www.radix-ui.com/)
- Visualizations with [Plotly](https://plotly.com/)
- Multi-agent orchestration with [LangGraph](https://langchain-ai.github.io/langgraph/)

---

**Built with ❤️ following 12 Factor Agents principles**

Version: 0.1.0 | Status: Development
