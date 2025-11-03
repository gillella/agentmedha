# Technology Stack
## Detailed Technology Selection and Rationale

**Version:** 1.0  
**Date:** November 3, 2025

---

## Table of Contents

1. [Backend Stack](#backend-stack)
2. [AI/ML Stack](#aiml-stack)
3. [Frontend Stack](#frontend-stack)
4. [Data Layer](#data-layer)
5. [Infrastructure](#infrastructure)
6. [Development Tools](#development-tools)
7. [Technology Comparisons](#technology-comparisons)
8. [Cost Analysis](#cost-analysis)

---

## 1. Backend Stack

### 1.1 API Framework: FastAPI

**Selected**: FastAPI 0.104+  
**Language**: Python 3.11+

**Why FastAPI:**

✅ **Pros:**
- Exceptional performance (one of the fastest Python frameworks)
- Built-in async/await support for non-blocking I/O
- Automatic OpenAPI documentation
- Pydantic integration for type safety and validation
- Native WebSocket support
- Easy testing with pytest
- Modern Python features (type hints, async)
- Large community and ecosystem

**Alternatives Considered:**

| Framework | Pros | Cons | Why Not Selected |
|-----------|------|------|------------------|
| Flask | Simple, flexible, large ecosystem | No async support, slower | Doesn't support async natively |
| Django | Full-featured, admin panel, ORM | Heavy, slower, monolithic | Too heavyweight for API-only service |
| Express.js | Mature, large ecosystem | JavaScript/TypeScript, less type-safe | Python better for data/AI tasks |

**Example Implementation:**

```python
# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_router
from app.core.config import settings

app = FastAPI(
    title="BI Agent API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Dependencies:**

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
```

---

## 2. AI/ML Stack

### 2.1 LLM Provider: OpenAI GPT-4

**Selected**: OpenAI GPT-4 Turbo (gpt-4-turbo-2024-04-09)

**Why OpenAI GPT-4:**

✅ **Pros:**
- Best-in-class text-to-SQL performance
- 128K context window (fits large schemas)
- Function calling for structured outputs
- JSON mode for reliable parsing
- Low latency (<2s for most requests)
- Excellent documentation and support
- Reliable uptime (>99.9%)

**Cost**: ~$0.01/1K input tokens, ~$0.03/1K output tokens

**Alternatives:**

| Provider | Model | Pros | Cons | Use Case |
|----------|-------|------|------|----------|
| Anthropic | Claude 3.5 Sonnet | 200K context, strong reasoning | Higher cost | Fallback option |
| Google | Gemini Pro | Free tier, good performance | Less proven for SQL | Development/testing |
| Open Source | Llama 3 70B | Self-hosted, no API costs | Requires GPU infrastructure | Future consideration |
| Open Source | SQLCoder 15B | Specialized for SQL | Limited general capabilities | SQL generation only |

**Example Configuration:**

```python
# backend/app/core/llm.py
from openai import AsyncOpenAI
from app.core.config import settings

class LLMProvider:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
    
    async def generate(
        self,
        messages: list,
        temperature: float = None,
        max_tokens: int = 2000,
        json_mode: bool = False
    ):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"} if json_mode else None
        )
        return response.choices[0].message.content

llm = LLMProvider()
```

### 2.2 Agent Framework: LangChain + LangGraph

**Selected**: LangChain 0.1.0, LangGraph 0.1.0

**Why LangChain + LangGraph:**

✅ **Pros:**
- Comprehensive agent abstractions
- Built-in memory management
- Tool integration framework
- Prompt template management
- LangGraph for complex workflows with state management
- Large community and ecosystem
- Excellent documentation

**Alternatives:**

| Framework | Pros | Cons | Why Not Selected |
|-----------|------|------|------------------|
| AutoGen | Microsoft-backed, multi-agent conversations | Less mature, fewer integrations | Narrower scope |
| CrewAI | Simple multi-agent setup | Less flexible, fewer features | Too opinionated |
| Custom | Full control, lightweight | More dev time, reinventing wheel | Not justified for this project |

**Example Implementation:**

```python
# backend/app/agents/workflow.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict
from app.agents.planner import PlannerAgent
from app.agents.sql import SQLAgent
from app.agents.visualization import VisualizationAgent
from app.agents.insight import InsightAgent

class AgentState(TypedDict):
    user_id: str
    session_id: str
    question: str
    context: Dict
    analysis_plan: Optional[Dict]
    sql_query: Optional[str]
    results: Optional[List[Dict]]
    visualization: Optional[Dict]
    insights: Optional[List[str]]
    errors: List[Dict]

def create_workflow():
    workflow = StateGraph(AgentState)
    
    # Initialize agents
    planner = PlannerAgent()
    sql_agent = SQLAgent()
    viz_agent = VisualizationAgent()
    insight_agent = InsightAgent()
    
    # Add nodes
    workflow.add_node("planner", planner.run)
    workflow.add_node("sql_generator", sql_agent.run)
    workflow.add_node("visualizer", viz_agent.run)
    workflow.add_node("insight_generator", insight_agent.run)
    
    # Add edges
    workflow.add_edge("planner", "sql_generator")
    workflow.add_edge("sql_generator", "visualizer")
    workflow.add_edge("visualizer", "insight_generator")
    workflow.add_edge("insight_generator", END)
    
    workflow.set_entry_point("planner")
    
    return workflow.compile()

agent_workflow = create_workflow()
```

**Dependencies:**

```toml
[tool.poetry.dependencies]
langchain = "^0.1.0"
langgraph = "^0.1.0"
langchain-openai = "^0.0.2"
langchain-community = "^0.0.10"
```

### 2.3 Text-to-SQL: Vanna.AI + Custom Pipeline

**Selected**: Vanna.AI 0.3+ with custom enhancements

**Why Vanna.AI:**

✅ **Pros:**
- RAG-based approach (learns from examples)
- Schema-aware
- Self-improving (learns from corrections)
- Multi-database support
- Open source
- Easy integration

**Approach**: Hybrid

1. **Vanna.AI** for schema understanding and example-based learning
2. **Custom LLM pipeline** for complex queries and optimization
3. **Fallback chain** for reliability

**Example Implementation:**

```python
# backend/app/services/text_to_sql.py
from vanna.remote import VannaDefault
from app.core.llm import llm
from app.services.schema import schema_manager

class TextToSQLService:
    def __init__(self):
        self.vanna = VannaDefault(
            model=settings.VANNA_MODEL,
            api_key=settings.VANNA_API_KEY
        )
        self.trained = False
    
    async def train_on_schema(self, database_id: str):
        """Train Vanna on database schema"""
        schema = schema_manager.get_schema(database_id)
        
        # Train on DDL
        for table_name, table_info in schema.items():
            ddl = schema_manager.get_ddl(table_name)
            self.vanna.train(ddl=ddl)
        
        # Train on documentation
        docs = schema_manager.get_documentation(database_id)
        for doc in docs:
            self.vanna.train(documentation=doc)
        
        # Train on historical successful queries
        queries = await self.get_successful_queries(database_id)
        for query in queries:
            self.vanna.train(
                question=query['question'],
                sql=query['sql']
            )
        
        self.trained = True
    
    async def generate_sql(
        self,
        question: str,
        database_id: str,
        schema_context: Dict
    ) -> str:
        """Generate SQL from natural language"""
        
        # Method 1: Try Vanna (fast, learned patterns)
        try:
            sql = self.vanna.generate_sql(question)
            if self._validate_sql(sql):
                return sql
        except Exception as e:
            logger.warning(f"Vanna failed: {e}")
        
        # Method 2: Custom LLM pipeline (more flexible)
        sql = await self._generate_with_llm(
            question,
            schema_context
        )
        
        return sql
    
    async def _generate_with_llm(
        self,
        question: str,
        schema_context: Dict
    ) -> str:
        """Generate SQL using custom LLM pipeline"""
        
        # Get similar queries for few-shot learning
        similar = schema_manager.get_similar_queries(question, top_k=3)
        
        prompt = self._build_prompt(question, schema_context, similar)
        
        sql = await llm.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        return sql
```

**Dependencies:**

```toml
[tool.poetry.dependencies]
vanna = "^0.3.0"
sqlparse = "^0.4.4"
sqlalchemy = "^2.0.25"
```

---

## 3. Frontend Stack

### 3.1 Framework: React 18 + TypeScript

**Selected**: React 18.2+ with TypeScript 5.0+

**Why React + TypeScript:**

✅ **Pros:**
- Most popular frontend framework (huge ecosystem)
- Component-based architecture
- Virtual DOM for performance
- TypeScript for type safety and better DX
- Excellent tooling and IDE support
- React 18 concurrent features
- Server Components (future upgrade path)

**Alternatives:**

| Framework | Pros | Cons | Why Not Selected |
|-----------|------|------|------------------|
| Vue 3 | Simpler learning curve, composition API | Smaller ecosystem | React ecosystem stronger |
| Angular | Full-featured, enterprise-ready | Steeper learning curve, heavyweight | Overkill for this project |
| Svelte | Fastest, no virtual DOM | Smaller ecosystem, fewer jobs | Less proven at scale |

**Project Structure:**

```
frontend/
├── src/
│   ├── components/
│   │   ├── QueryInterface/
│   │   ├── Visualization/
│   │   ├── Dashboard/
│   │   └── Common/
│   ├── hooks/
│   │   ├── useQuery.ts
│   │   ├── useVisualization.ts
│   │   └── useAuth.ts
│   ├── services/
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── store/
│   │   └── index.ts
│   ├── types/
│   │   └── index.ts
│   └── utils/
│       └── formatters.ts
├── package.json
└── tsconfig.json
```

### 3.2 State Management: Zustand + React Query

**Selected**: Zustand 4.4+ for global state, React Query 5.0+ for server state

**Why This Combination:**

✅ **Pros:**
- **Zustand**: Minimal boilerplate, simple API, TypeScript-first
- **React Query**: Automatic caching, background refetching, optimistic updates
- Clear separation: Zustand for UI state, React Query for server data
- No prop drilling
- DevTools support

**Alternatives:**

| Tool | Pros | Cons | Why Not Selected |
|------|------|------|------------------|
| Redux | Most popular, mature | Boilerplate-heavy, complex | Too much overhead |
| Recoil | Facebook-backed, atoms | Less mature, smaller community | Zustand simpler |
| Context API | Built-in, no dependencies | Performance issues, prop drilling | Not scalable |

**Example Implementation:**

```typescript
// frontend/src/store/queryStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface QueryState {
  currentQuery: string;
  queryHistory: string[];
  results: any[];
  isLoading: boolean;
  error: string | null;
  
  setCurrentQuery: (query: string) => void;
  addToHistory: (query: string) => void;
  setResults: (results: any[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useQueryStore = create<QueryState>()(
  devtools(
    (set) => ({
      currentQuery: '',
      queryHistory: [],
      results: [],
      isLoading: false,
      error: null,
      
      setCurrentQuery: (query) => set({ currentQuery: query }),
      addToHistory: (query) => set((state) => ({
        queryHistory: [query, ...state.queryHistory].slice(0, 50)
      })),
      setResults: (results) => set({ results }),
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
    }),
    { name: 'QueryStore' }
  )
);

// Usage with React Query
import { useQuery, useMutation } from '@tanstack/react-query';
import { executeQuery } from '@/services/api';

function QueryInterface() {
  const { currentQuery, setResults, setLoading } = useQueryStore();
  
  const mutation = useMutation({
    mutationFn: executeQuery,
    onSuccess: (data) => {
      setResults(data.results);
    },
  });
  
  const handleSubmit = () => {
    mutation.mutate({ question: currentQuery });
  };
  
  return (
    // Component JSX
  );
}
```

### 3.3 Visualization: Plotly.js

**Selected**: Plotly.js 2.27+ (via react-plotly.js)

**Why Plotly:**

✅ **Pros:**
- Highly interactive (zoom, pan, hover, click)
- Professional-looking charts out of the box
- Supports 40+ chart types
- 3D visualization support
- Export to static images
- Dash framework for dashboards
- Good performance (<10K points)
- TypeScript support

**Alternatives:**

| Library | Pros | Cons | Why Not Selected |
|---------|------|------|------------------|
| D3.js | Maximum flexibility, powerful | Steep learning curve, verbose | Overkill, slower dev time |
| Chart.js | Simple, lightweight | Less interactive, fewer chart types | Limited capabilities |
| Recharts | React-native, composable | Smaller feature set | Plotly more powerful |
| Apache ECharts | Feature-rich, performant | Less React-friendly | Integration complexity |

**Example Implementation:**

```typescript
// frontend/src/components/Visualization/ChartRenderer.tsx
import Plot from 'react-plotly.js';
import { useMemo } from 'react';

interface ChartRendererProps {
  data: any[];
  config: {
    chart_type: string;
    x_axis: string;
    y_axis: string;
    title: string;
  };
}

export function ChartRenderer({ data, config }: ChartRendererProps) {
  const plotlyData = useMemo(() => {
    if (config.chart_type === 'bar') {
      return [{
        type: 'bar',
        x: data.map(d => d[config.x_axis]),
        y: data.map(d => d[config.y_axis]),
        marker: { color: '#3b82f6' },
      }];
    }
    
    if (config.chart_type === 'line') {
      return [{
        type: 'scatter',
        mode: 'lines+markers',
        x: data.map(d => d[config.x_axis]),
        y: data.map(d => d[config.y_axis]),
        line: { color: '#3b82f6', width: 2 },
      }];
    }
    
    // Add more chart types...
    
    return [];
  }, [data, config]);
  
  const layout = {
    title: config.title,
    autosize: true,
    xaxis: { title: config.x_axis },
    yaxis: { title: config.y_axis },
    hovermode: 'closest',
  };
  
  return (
    <Plot
      data={plotlyData}
      layout={layout}
      config={{ responsive: true, displayModeBar: true }}
      style={{ width: '100%', height: '100%' }}
    />
  );
}
```

### 3.4 UI Components: Tailwind CSS + Radix UI

**Selected**: Tailwind CSS 3.4+ + Radix UI primitives

**Why This Combination:**

✅ **Pros:**
- **Tailwind**: Utility-first, rapid development, small bundle size
- **Radix**: Unstyled, accessible components (WAI-ARIA compliant)
- Full design control
- Consistent design system
- Excellent DX with autocomplete
- Dark mode support built-in

**Example:**

```typescript
// frontend/src/components/Common/Button.tsx
import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/utils/cn';

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        default: "bg-blue-600 text-white hover:bg-blue-700",
        outline: "border border-gray-300 bg-transparent hover:bg-gray-100",
        ghost: "hover:bg-gray-100 hover:text-gray-900",
      },
      size: {
        default: "h-10 py-2 px-4",
        sm: "h-9 px-3 rounded-md",
        lg: "h-11 px-8 rounded-md",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
```

**Dependencies:**

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-plotly.js": "^2.6.0",
    "plotly.js": "^2.27.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.4.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-select": "^2.0.0",
    "tailwindcss": "^3.4.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

---

## 4. Data Layer

### 4.1 Primary Database: PostgreSQL

**Selected**: PostgreSQL 14+

**Why PostgreSQL:**

✅ **Pros:**
- Open source, mature, battle-tested
- ACID compliant
- Rich feature set (JSON, full-text search, extensions)
- Excellent performance
- Strong community and tooling
- pgvector extension for embeddings
- Good ORM support (SQLAlchemy)

**Usage in our system:**
- Metadata store (schema docs, user data)
- Query history
- Configuration
- Audit logs

### 4.2 Caching: Redis

**Selected**: Redis 7.2+

**Why Redis:**

✅ **Pros:**
- Extremely fast (sub-millisecond latency)
- Simple key-value model
- Rich data structures (strings, hashes, lists, sets)
- Pub/sub for real-time features
- Optional persistence
- Clustering support

**Usage in our system:**
- Query result caching
- Session management
- Rate limiting
- Real-time notifications (pub/sub)

**Example:**

```python
# backend/app/services/cache.py
from redis import asyncio as aioredis
import json
from typing import Optional, Any
from app.core.config import settings

class CacheService:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ):
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )
    
    async def delete(self, key: str):
        await self.redis.delete(key)

cache = CacheService()
```

### 4.3 Vector Database: Pinecone

**Selected**: Pinecone (managed service)

**Why Pinecone:**

✅ **Pros:**
- Fully managed (no infrastructure)
- Excellent performance (<100ms queries)
- Scalable to billions of vectors
- Simple API
- Built-in filtering
- Generous free tier

**Alternatives:**

| Database | Pros | Cons | Why Not Selected |
|----------|------|------|------------------|
| Weaviate | Open source, self-hosted | More complex setup | We want managed |
| Qdrant | Fast, open source | Smaller community | Pinecone more mature |
| pgvector | Uses existing PostgreSQL | Limited features, slower | Not specialized enough |

**Usage in our system:**
- Store query embeddings for semantic search
- Store table/column embeddings for schema search
- Find similar historical queries

**Example:**

```python
# backend/app/services/vector_store.py
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def encode(self, text: str) -> list:
        return self.encoder.encode(text).tolist()
    
    async def upsert_query(
        self,
        query_id: str,
        question: str,
        sql: str,
        metadata: dict
    ):
        embedding = self.encode(question)
        
        self.index.upsert(
            vectors=[(
                query_id,
                embedding,
                {
                    "question": question,
                    "sql": sql,
                    **metadata
                }
            )],
            namespace="queries"
        )
    
    async def search_similar_queries(
        self,
        question: str,
        top_k: int = 5
    ):
        embedding = self.encode(question)
        
        results = self.index.query(
            vector=embedding,
            top_k=top_k,
            namespace="queries",
            include_metadata=True
        )
        
        return [
            {
                "id": match.id,
                "score": match.score,
                "question": match.metadata["question"],
                "sql": match.metadata["sql"],
            }
            for match in results.matches
        ]

vector_store = VectorStore()
```

---

## 5. Infrastructure

### 5.1 Containerization: Docker

**Why Docker:**
- Consistent environments (dev/staging/prod)
- Easy dependency management
- Portable across clouds
- Efficient resource usage
- Large ecosystem

**Example docker-compose.yml:**

```yaml
version: '3.8'

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/biagent
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=biagent
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### 5.2 Orchestration: Kubernetes

**Selected**: Kubernetes 1.28+

**Why Kubernetes:**
- Industry standard for container orchestration
- Auto-scaling (HPA, VPA)
- Self-healing
- Rolling updates
- Service discovery
- Multi-cloud portability

**Alternative**: AWS ECS (simpler but less portable)

---

## 6. Development Tools

### 6.1 Version Control & CI/CD

- **Git**: Version control
- **GitHub**: Repository hosting, code review
- **GitHub Actions**: CI/CD pipelines

**Example CI/CD:**

```yaml
# .github/workflows/backend-ci.yml
name: Backend CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install
      
      - name: Run tests
        run: |
          cd backend
          poetry run pytest --cov=app tests/
      
      - name: Lint
        run: |
          cd backend
          poetry run black --check app/
          poetry run isort --check app/
          poetry run mypy app/
```

### 6.2 Code Quality

- **Black**: Code formatting (Python)
- **isort**: Import sorting (Python)
- **mypy**: Static type checking (Python)
- **Prettier**: Code formatting (TypeScript)
- **ESLint**: Linting (TypeScript)
- **pytest**: Testing (Python)
- **Jest**: Testing (TypeScript)

---

## 7. Cost Analysis

### Monthly Cost Estimate (100 active users)

| Service | Usage | Cost |
|---------|-------|------|
| **OpenAI API** | 10K requests/day, avg 2K tokens | $300 |
| **Pinecone** | 100K queries/day, 1M vectors | $70 (standard) |
| **AWS Infrastructure** | 2x t3.large, RDS, ElastiCache | $400 |
| **Monitoring** | Prometheus/Grafana (self-hosted) | $0 |
| **Total** | | **~$770/month** |

**Per User**: ~$7.70/month

**Cost Optimization Strategies:**
1. Aggressive caching (reduce LLM calls by 50%)
2. Query result caching (reduce DB load)
3. Auto-scaling (pay for what you use)
4. Reserved instances (30-40% savings)

**Projected Costs at Scale:**

| Users | Monthly Cost | Per User |
|-------|-------------|----------|
| 100 | $770 | $7.70 |
| 500 | $2,500 | $5.00 |
| 1,000 | $4,000 | $4.00 |
| 5,000 | $15,000 | $3.00 |

---

## 8. Technology Decision Matrix

### Quick Reference

| Category | Technology | Maturity | Community | Performance | Cost |
|----------|-----------|----------|-----------|-------------|------|
| **Backend** | FastAPI | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free |
| **Frontend** | React + TS | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free |
| **LLM** | OpenAI GPT-4 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$$ |
| **Agents** | LangGraph | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free |
| **Text-to-SQL** | Vanna.AI | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | Free |
| **Viz** | Plotly | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free |
| **Database** | PostgreSQL | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free |
| **Cache** | Redis | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $ |
| **Vector DB** | Pinecone | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $$ |

---

**Document Owner**: Technical Lead  
**Last Updated**: November 3, 2025  
**Next Review**: Q2 2025

