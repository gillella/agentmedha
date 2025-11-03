# AgentMedha
## AI-Powered Analytics & Business Intelligence

**Medha** — Sanskrit for "intelligence" and "wisdom" • **Medha Devi** — Goddess of intelligence, aspect of Saraswati

---

An AI-powered analytics platform that enables non-technical stakeholders to interact with complex databases using natural language, powered by multi-agent workflows following the **12 Factor Agents** methodology.

## 🎯 Overview

AgentMedha transforms how organizations interact with their data by:

- **Natural Language Queries**: Ask questions in plain English, get SQL results
- **Automated Insights**: AI-generated insights and recommendations
- **Interactive Dashboards**: Beautiful, interactive visualizations
- **Multi-Agent Workflow**: Specialized agents working together for comprehensive analytics
- **Enterprise-Ready**: Built for scale, security, and reliability

## 🌟 Key Features

### Natural Language SQL Query Agent
- Convert conversational questions to SQL
- Support for complex queries (joins, aggregations, subqueries)
- Schema-aware query generation
- Query safety validation
- >90% query accuracy

### Enterprise Analytics Workflow
- **Planner Agent**: Understands intent and plans analysis
- **SQL Agent**: Generates and executes optimized SQL
- **Visualization Agent**: Creates appropriate charts and dashboards
- **Insight Agent**: Generates natural language insights and recommendations

### Automated Data Analysis
- Statistical analysis (trends, patterns, outliers)
- Predictive analytics and forecasting
- Anomaly detection
- Period-over-period comparisons
- Executive summaries

### Interactive Visualizations
- Line charts, bar charts, pie charts, scatter plots, heat maps
- Real-time dashboard updates
- Drill-down capabilities
- Export to PNG, PDF, Excel
- Mobile-responsive design

## 🏗️ Architecture

Built on **12 Factor Agents** principles:

```
User Interface (React)
        ↓
API Gateway (FastAPI)
        ↓
Agent Orchestration (LangGraph)
    ↙   ↓   ↓   ↘
Planner  SQL  Viz  Insight
    ↘   ↓   ↓   ↙
Supporting Services
        ↓
Data Layer (Multiple DBs)
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture documentation.

## 📋 Project Status

**Phase**: Planning & Design Complete  
**Next**: Implementation Phase Starting

- [x] Project plan complete
- [x] Requirements documented
- [x] Architecture designed
- [x] Technology stack selected
- [ ] Implementation in progress
- [ ] Testing
- [ ] Beta launch

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 14+ (or other supported database)
- OpenAI API key (or other LLM provider)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd agentmedha

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Set up frontend
cd ../frontend
npm install

# Start development environment
docker-compose up -d  # Starts Redis, PostgreSQL, etc.

# Run backend
cd backend
uvicorn app.main:app --reload

# Run frontend (in another terminal)
cd frontend
npm start
```

Visit `http://localhost:3000` to access AgentMedha.

## 📚 Documentation

- [**Project Plan**](./PROJECT_PLAN.md) - Comprehensive project plan with roadmap
- [**Requirements**](./REQUIREMENTS.md) - Detailed functional and non-functional requirements
- [**Architecture**](./ARCHITECTURE.md) - System architecture and design
- [**Technology Stack**](./TECH_STACK.md) - Technology decisions and comparisons
- [**Getting Started**](./GETTING_STARTED.md) - Setup and development guide
- [**Project Summary**](./PROJECT_SUMMARY.md) - Executive summary

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/LLM**: OpenAI GPT-4, LangChain, LangGraph
- **Text-to-SQL**: Vanna.AI + Custom pipeline
- **Databases**: PostgreSQL, MySQL, Snowflake, BigQuery
- **Caching**: Redis
- **Vector DB**: Pinecone

### Frontend
- **Framework**: React 18 with TypeScript
- **State Management**: Zustand + React Query
- **Visualization**: Plotly.js
- **UI Components**: Tailwind CSS + Radix UI
- **Build Tool**: Vite

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack
- **Tracing**: Jaeger/OpenTelemetry

## 🏢 Use Cases

### Business Analyst
> "What were our top 5 products by revenue last quarter?"

AgentMedha automatically:
1. Understands you want revenue analysis
2. Identifies the relevant tables (products, sales)
3. Generates and executes the SQL query
4. Creates a bar chart visualization
5. Provides insights like "Revenue up 15% vs previous quarter"

### Data Analyst
> "Show me customer churn rate by segment for the last 6 months, and compare it to industry benchmarks"

AgentMedha handles multi-step analysis:
1. Calculates churn rate by segment
2. Performs period-over-period comparison
3. Creates trend visualization
4. Generates insights and recommendations

### Executive
> "Give me an executive summary of our Q3 performance"

AgentMedha provides:
1. Key metrics dashboard
2. Highlights and lowlights
3. Comparisons to targets and previous periods
4. Actionable recommendations

## 🔐 Security

- **Authentication**: JWT + OAuth 2.0 + SSO
- **Authorization**: Role-based access control (RBAC) + Row-level security
- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Audit Logging**: Complete audit trail of all queries
- **SQL Injection Prevention**: Multi-layer validation
- **Compliance**: GDPR, SOC 2, HIPAA ready

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Query Accuracy | >90% | TBD |
| Query Latency (P95) | <5s | TBD |
| User Satisfaction | >4.5/5 | TBD |
| Daily Active Users | 100+ | TBD |
| System Uptime | >99.9% | TBD |

## 🗺️ Roadmap

### Q1 2025 (Current)
- [x] Project planning
- [x] Architecture design
- [ ] Core agent implementation
- [ ] Basic UI

### Q2 2025
- [ ] Advanced features
- [ ] Performance optimization
- [ ] Beta testing
- [ ] Production deployment

### Q3 2025
- [ ] Enterprise features
- [ ] Advanced analytics
- [ ] Collaboration tools

### Q4 2025
- [ ] AI enhancements
- [ ] Mobile app
- [ ] International expansion

See [PROJECT_PLAN.md](./PROJECT_PLAN.md) for detailed roadmap.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📖 12 Factor Agents Principles

AgentMedha strictly adheres to the 12 Factor Agents methodology:

1. ✅ **Single-Purpose Agents**: Each agent has one clear responsibility
2. ✅ **Explicit Dependencies**: All dependencies versioned and declared
3. ✅ **Configuration Management**: Config in environment, not code
4. ✅ **External Tool Integration**: Databases as attachable resources
5. ✅ **Deterministic Deployment**: Reproducible builds and deployments
6. ✅ **Stateless Execution**: Agents maintain no internal state
7. ✅ **Port Binding**: Services exposed via port binding
8. ✅ **Concurrency**: Horizontal scaling through process instances
9. ✅ **Disposability**: Fast startup and graceful shutdown
10. ✅ **Dev/Prod Parity**: Minimal environment differences
11. ✅ **Logs as Event Streams**: Structured logging to stdout
12. ✅ **Admin Processes**: One-off tasks as separate processes

Learn more: https://mainstream.dev/12-factor-agents

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Technical Lead**: [Name]
- **Product Manager**: [Name]
- **Backend Engineers**: [Names]
- **Frontend Engineers**: [Names]
- **Data Scientists**: [Names]

## 📞 Contact & Support

- **Email**: support@agentmedha.com
- **Documentation**: https://docs.agentmedha.com
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Slack**: #agentmedha-support

## 🙏 Acknowledgments

- Inspired by LinkedIn's AI-powered SQL Bot
- Built on top of amazing open-source projects: LangChain, FastAPI, React, Plotly
- Following the 12 Factor Agents methodology by Mainstream.dev
- Special thanks to the AI/ML community for their research and tools

## 🎨 About the Name

**Medha** (Sanskrit: मेधा) means "intelligence," "wisdom," and "mental power."

**Medha Devi** is the Hindu goddess of intelligence and wisdom, often considered an aspect of Saraswati, the goddess of knowledge, music, arts, and learning.

The name **AgentMedha** embodies our mission: to bring intelligence and wisdom to data analysis, empowering everyone to make informed decisions.

---

**Built with ❤️ using 12 Factor Agents principles**

*Empowering intelligence through data • AgentMedha*
