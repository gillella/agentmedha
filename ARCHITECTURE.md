# Data Analytics & Business Intelligence Agent
## System Architecture Document

**Version:** 1.0  
**Date:** November 3, 2025  
**Status:** Design Phase

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Agent Architecture](#agent-architecture)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Deployment Architecture](#deployment-architecture)
7. [Security Architecture](#security-architecture)
8. [Scalability & Performance](#scalability--performance)
9. [Disaster Recovery](#disaster-recovery)

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

The system follows a **microservices-based architecture** with **multi-agent orchestration** at its core. The architecture is designed according to the **12 Factor Agents** principles to ensure reliability, scalability, and maintainability.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Web Browser  │  │ Mobile App   │  │ API Clients  │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
└─────────┼──────────────────┼──────────────────┼──────────────────────┘
          │                  │                  │
          │         HTTPS / WSS / REST API      │
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼──────────────────────┐
│                    API Gateway / Load Balancer                        │
│                    (Kong / Nginx / Traefik)                           │
└──────────────────────────────┬────────────────────────────────────────┘
                               │
┌──────────────────────────────▼────────────────────────────────────────┐
│                     Application Layer (FastAPI)                       │
│  ┌────────────────────────────────────────────────────────┐          │
│  │              Agent Orchestration Layer                  │          │
│  │                    (LangGraph)                          │          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐│          │
│  │  │ Planner  │  │   SQL    │  │   Viz    │  │Insight ││          │
│  │  │  Agent   │  │  Agent   │  │  Agent   │  │ Agent  ││          │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘│          │
│  └───────┼─────────────┼─────────────┼────────────┼──────┘          │
│          │             │             │            │                  │
│  ┌───────▼─────────────▼─────────────▼────────────▼──────┐          │
│  │              Supporting Services Layer                  │          │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐│          │
│  │  │  Schema  │  │  Query   │  │ Vector  │  │ Session ││          │
│  │  │  Manager │  │  Cache   │  │  Store  │  │ Manager ││          │
│  │  └────┬─────┘  └────┬─────┘  └────┬────┘  └────┬────┘│          │
│  └───────┼─────────────┼──────────────┼───────────┼──────┘          │
└──────────┼─────────────┼──────────────┼───────────┼──────────────────┘
           │             │              │           │
┌──────────▼─────────────▼──────────────▼───────────▼──────────────────┐
│                         Data Layer                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   Redis  │  │ Vector   │  │Metadata  │  │  Target  │            │
│  │  Cache   │  │   DB     │  │   DB     │  │    DBs   │            │
│  │          │  │(Pinecone)│  │(Postgres)│  │(Multiple)│            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                    Observability Layer                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │Prometheus│  │  Grafana │  │  Jaeger  │  │   ELK    │            │
│  │ (Metrics)│  │ (Dashb.) │  │ (Tracing)│  │  (Logs)  │            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                    External Services                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ OpenAI   │  │   Auth   │  │  Email   │  │  Slack   │            │
│  │   API    │  │ Provider │  │ Service  │  │   API    │            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
└───────────────────────────────────────────────────────────────────────┘
```

### 1.2 Architectural Patterns

#### Microservices Architecture
- **Loose Coupling**: Each service is independent
- **Single Responsibility**: Each service has one purpose
- **Technology Diversity**: Different services can use different tech stacks
- **Independent Deployment**: Services can be deployed separately

#### Event-Driven Architecture
- **Asynchronous Communication**: Services communicate via events
- **Pub/Sub Pattern**: Message broker for event distribution
- **Event Sourcing**: Store events for audit and replay
- **CQRS**: Separate read and write models where appropriate

#### Multi-Agent System
- **Agent Autonomy**: Each agent operates independently
- **Collaborative Workflow**: Agents work together to achieve goals
- **State Management**: Centralized state for agent coordination
- **Error Recovery**: Built-in error handling and retry mechanisms

---

## 2. System Components

### 2.1 Frontend Application

**Technology**: React 18+ with TypeScript

**Components**:
```
frontend/
├── src/
│   ├── components/
│   │   ├── QueryInterface/
│   │   │   ├── QueryInput.tsx
│   │   │   ├── QuerySuggestions.tsx
│   │   │   └── QueryHistory.tsx
│   │   ├── Visualization/
│   │   │   ├── ChartRenderer.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   └── ChartEditor.tsx
│   │   ├── Results/
│   │   │   ├── DataTable.tsx
│   │   │   ├── InsightPanel.tsx
│   │   │   └── ExportMenu.tsx
│   │   └── Common/
│   │       ├── Layout.tsx
│   │       ├── Navigation.tsx
│   │       └── ErrorBoundary.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── websocket.ts
│   │   └── auth.ts
│   ├── store/
│   │   ├── querySlice.ts
│   │   ├── userSlice.ts
│   │   └── configureStore.ts
│   └── utils/
│       ├── formatters.ts
│       └── validators.ts
```

**Key Features**:
- **React Query**: Data fetching and caching
- **Zustand**: State management
- **Plotly.js**: Interactive visualizations
- **Monaco Editor**: SQL query editor
- **WebSocket**: Real-time updates

### 2.2 API Gateway

**Technology**: FastAPI with Uvicorn

**Structure**:
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── query.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── database.py
│   │   │   │   └── user.py
│   │   │   └── router.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   └── main.py
```

**Responsibilities**:
- Request routing
- Authentication/Authorization
- Rate limiting
- Request validation
- Response formatting
- Error handling
- API documentation (OpenAPI)

### 2.3 Agent Orchestration Layer

**Technology**: LangGraph + LangChain

**Agent Workflow**:
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict

class AgentState(TypedDict):
    """Shared state across all agents"""
    # Input
    user_id: str
    session_id: str
    question: str
    context: Dict
    
    # Planner output
    analysis_plan: Optional[Dict]
    required_tables: List[str]
    
    # SQL Agent output
    sql_query: Optional[str]
    sql_explanation: Optional[str]
    
    # Execution output
    results: Optional[List[Dict]]
    row_count: int
    execution_time: float
    
    # Visualization output
    visualization_config: Optional[Dict]
    chart_data: Optional[Dict]
    
    # Insight output
    insights: Optional[List[str]]
    recommendations: Optional[List[str]]
    follow_up_questions: Optional[List[str]]
    
    # Error handling
    errors: List[Dict]
    retry_count: int

# Define the workflow graph
workflow = StateGraph(AgentState)

# Add nodes (agents)
workflow.add_node("planner", planner_agent_node)
workflow.add_node("sql_generator", sql_agent_node)
workflow.add_node("validator", validation_node)
workflow.add_node("executor", execution_node)
workflow.add_node("visualizer", visualization_agent_node)
workflow.add_node("insight_generator", insight_agent_node)
workflow.add_node("error_handler", error_recovery_node)

# Add edges (flow control)
workflow.add_edge("planner", "sql_generator")
workflow.add_edge("sql_generator", "validator")

# Conditional routing based on validation
workflow.add_conditional_edges(
    "validator",
    route_after_validation,
    {
        "execute": "executor",
        "retry": "sql_generator",
        "error": "error_handler"
    }
)

workflow.add_edge("executor", "visualizer")
workflow.add_edge("visualizer", "insight_generator")
workflow.add_edge("insight_generator", END)
workflow.add_edge("error_handler", END)

# Set entry point
workflow.set_entry_point("planner")

# Compile the graph
app = workflow.compile()
```

### 2.4 Agent Implementations

#### 2.4.1 Planner Agent

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class AnalysisPlan(BaseModel):
    """Structured output from Planner Agent"""
    intent: str = Field(description="Type of analysis requested")
    metrics: List[str] = Field(description="Metrics to calculate")
    dimensions: List[str] = Field(description="Dimensions to group by")
    filters: Dict[str, Any] = Field(description="Filter conditions")
    time_range: Optional[Dict] = Field(description="Time range if applicable")
    aggregations: List[str] = Field(description="Required aggregations")
    complexity: str = Field(description="simple, medium, or complex")
    required_tables: List[str] = Field(description="Tables needed")
    steps: List[Dict] = Field(description="Multi-step analysis if needed")

class PlannerAgent:
    """Agent responsible for understanding intent and planning analysis"""
    
    def __init__(self, llm: ChatOpenAI, schema_manager):
        self.llm = llm
        self.schema_manager = schema_manager
        self.parser = PydanticOutputParser(pydantic_object=AnalysisPlan)
        self.prompt = self._create_prompt()
    
    def _create_prompt(self) -> ChatPromptTemplate:
        template = """You are a data analysis planning agent. Your job is to understand 
        the user's question and create a structured analysis plan.
        
        Available Schema:
        {schema_summary}
        
        User Question: {question}
        
        Previous Context: {context}
        
        Create a detailed analysis plan that includes:
        1. The type of analysis requested (trend, comparison, aggregation, etc.)
        2. Metrics to calculate
        3. Dimensions to analyze
        4. Any filters or conditions
        5. Time ranges if applicable
        6. Required tables from the schema
        7. Complexity level (simple, medium, complex)
        8. Break down into steps if it's a complex multi-part question
        
        {format_instructions}
        """
        
        return ChatPromptTemplate.from_template(template)
    
    async def plan(self, state: AgentState) -> AgentState:
        """Create analysis plan from user question"""
        
        # Get relevant schema information
        relevant_tables = self.schema_manager.find_relevant_tables(
            state["question"]
        )
        schema_summary = self.schema_manager.get_schema_summary(
            relevant_tables
        )
        
        # Generate plan
        messages = self.prompt.format_messages(
            schema_summary=schema_summary,
            question=state["question"],
            context=state.get("context", {}),
            format_instructions=self.parser.get_format_instructions()
        )
        
        response = await self.llm.agenerate([messages])
        plan = self.parser.parse(response.generations[0][0].text)
        
        # Update state
        state["analysis_plan"] = plan.dict()
        state["required_tables"] = plan.required_tables
        
        return state
```

#### 2.4.2 SQL Agent

```python
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase

class SQLAgent:
    """Agent responsible for SQL query generation and validation"""
    
    def __init__(self, llm: ChatOpenAI, db_connector, schema_manager):
        self.llm = llm
        self.db = db_connector
        self.schema_manager = schema_manager
        self.validator = QueryValidator()
        self.prompt = self._create_prompt()
    
    def _create_prompt(self) -> ChatPromptTemplate:
        template = """You are an expert SQL query generator. Generate a SQL query 
        based on the analysis plan.
        
        Analysis Plan:
        {analysis_plan}
        
        Database Schema for relevant tables:
        {schema_details}
        
        Example Queries (for reference):
        {example_queries}
        
        Requirements:
        1. Generate syntactically correct SQL for {database_type}
        2. Use appropriate JOINs based on foreign key relationships
        3. Include all necessary filters and aggregations
        4. Optimize for performance (use indexes, limit result set)
        5. Add comments explaining complex parts
        6. Use meaningful aliases
        7. Format the query for readability
        
        Generate ONLY the SQL query, nothing else.
        """
        
        return ChatPromptTemplate.from_template(template)
    
    async def generate_query(self, state: AgentState) -> AgentState:
        """Generate SQL query from analysis plan"""
        
        plan = state["analysis_plan"]
        tables = state["required_tables"]
        
        # Get detailed schema
        schema_details = self.schema_manager.get_detailed_schema(tables)
        
        # Get example queries (RAG approach)
        example_queries = self.schema_manager.get_similar_queries(
            state["question"],
            top_k=3
        )
        
        # Generate SQL
        messages = self.prompt.format_messages(
            analysis_plan=json.dumps(plan, indent=2),
            schema_details=schema_details,
            example_queries=example_queries,
            database_type=self.db.database_type
        )
        
        response = await self.llm.agenerate([messages])
        sql_query = response.generations[0][0].text.strip()
        
        # Clean up SQL (remove markdown code blocks if present)
        sql_query = self._clean_sql(sql_query)
        
        # Validate query
        is_valid, error = self.validator.validate(sql_query)
        
        if not is_valid:
            state["errors"].append({
                "agent": "sql_generator",
                "error": error,
                "query": sql_query
            })
        
        state["sql_query"] = sql_query
        state["sql_explanation"] = self._explain_query(sql_query)
        
        return state
    
    def _clean_sql(self, sql: str) -> str:
        """Remove markdown code blocks and clean SQL"""
        # Remove ```sql and ``` markers
        sql = re.sub(r'```sql\n?', '', sql)
        sql = re.sub(r'```\n?$', '', sql)
        return sql.strip()
    
    def _explain_query(self, sql: str) -> str:
        """Generate human-readable explanation of SQL query"""
        # Use LLM to generate explanation
        prompt = f"Explain this SQL query in simple terms:\n\n{sql}"
        response = self.llm.predict(prompt)
        return response
```

#### 2.4.3 Visualization Agent

```python
import pandas as pd
from typing import Dict, List, Any

class VisualizationAgent:
    """Agent responsible for creating visualizations"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.chart_selector = ChartTypeSelector()
    
    async def create_visualization(self, state: AgentState) -> AgentState:
        """Create visualization configuration from query results"""
        
        results = state["results"]
        plan = state["analysis_plan"]
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(results)
        
        # Determine appropriate chart type
        chart_type = self.chart_selector.select_chart_type(
            df=df,
            analysis_type=plan["intent"],
            metrics=plan["metrics"],
            dimensions=plan["dimensions"]
        )
        
        # Generate visualization config
        viz_config = self._create_viz_config(
            df=df,
            chart_type=chart_type,
            plan=plan
        )
        
        # Transform data for visualization
        chart_data = self._prepare_chart_data(df, viz_config)
        
        state["visualization_config"] = viz_config
        state["chart_data"] = chart_data
        
        return state
    
    def _create_viz_config(
        self, 
        df: pd.DataFrame, 
        chart_type: str, 
        plan: Dict
    ) -> Dict:
        """Create detailed visualization configuration"""
        
        config = {
            "chart_type": chart_type,
            "title": self._generate_title(plan),
            "x_axis": None,
            "y_axis": None,
            "color": None,
            "size": None,
            "facet": None,
            "layout": {},
            "styling": {}
        }
        
        # Determine axis mappings based on data types
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        datetime_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        if chart_type == "line":
            config["x_axis"] = datetime_columns[0] if datetime_columns else categorical_columns[0]
            config["y_axis"] = numeric_columns[0]
            if len(categorical_columns) > 1:
                config["color"] = categorical_columns[-1]
        
        elif chart_type == "bar":
            config["x_axis"] = categorical_columns[0]
            config["y_axis"] = numeric_columns[0]
        
        elif chart_type == "scatter":
            config["x_axis"] = numeric_columns[0]
            config["y_axis"] = numeric_columns[1] if len(numeric_columns) > 1 else numeric_columns[0]
            if categorical_columns:
                config["color"] = categorical_columns[0]
        
        elif chart_type == "pie":
            config["labels"] = categorical_columns[0]
            config["values"] = numeric_columns[0]
        
        # Add styling
        config["styling"] = {
            "color_scheme": "plotly",
            "font_family": "Inter, system-ui, sans-serif",
            "show_legend": True,
            "show_grid": True
        }
        
        return config
    
    def _generate_title(self, plan: Dict) -> str:
        """Generate appropriate chart title"""
        metrics_str = ", ".join(plan["metrics"])
        dimensions_str = " by " + ", ".join(plan["dimensions"]) if plan["dimensions"] else ""
        return f"{metrics_str}{dimensions_str}"
    
    def _prepare_chart_data(self, df: pd.DataFrame, config: Dict) -> Dict:
        """Transform DataFrame into format expected by visualization library"""
        
        # Convert DataFrame to plotly-compatible format
        chart_data = {
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
        
        return chart_data

class ChartTypeSelector:
    """Logic for selecting appropriate chart type"""
    
    def select_chart_type(
        self, 
        df: pd.DataFrame, 
        analysis_type: str,
        metrics: List[str],
        dimensions: List[str]
    ) -> str:
        """Select best chart type for the data and analysis"""
        
        num_rows = len(df)
        num_metrics = len(metrics)
        num_dimensions = len(dimensions)
        
        # Time series = line chart
        if any(df.dtypes == 'datetime64[ns]'):
            return "line"
        
        # Single metric, multiple categories = bar chart
        if num_metrics == 1 and num_dimensions == 1 and num_rows <= 20:
            return "bar"
        
        # Composition (parts of whole) = pie chart
        if analysis_type == "composition" and num_rows <= 10:
            return "pie"
        
        # Two metrics = scatter plot
        if num_metrics >= 2:
            return "scatter"
        
        # Many rows = table
        if num_rows > 50:
            return "table"
        
        # Default to bar chart
        return "bar"
```

#### 2.4.4 Insight Agent

```python
from typing import List, Dict
import numpy as np
from scipy import stats

class InsightAgent:
    """Agent responsible for generating insights from data"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.stat_analyzer = StatisticalAnalyzer()
    
    async def generate_insights(self, state: AgentState) -> AgentState:
        """Generate insights from query results"""
        
        df = pd.DataFrame(state["results"])
        plan = state["analysis_plan"]
        
        insights = []
        
        # Statistical insights
        stat_insights = self.stat_analyzer.analyze(df, plan)
        insights.extend(stat_insights)
        
        # LLM-generated insights
        llm_insights = await self._generate_llm_insights(df, plan, state["question"])
        insights.extend(llm_insights)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(df, insights, plan)
        
        # Generate follow-up questions
        follow_ups = await self._generate_follow_up_questions(
            state["question"],
            insights,
            plan
        )
        
        state["insights"] = insights
        state["recommendations"] = recommendations
        state["follow_up_questions"] = follow_ups
        
        return state
    
    async def _generate_llm_insights(
        self, 
        df: pd.DataFrame, 
        plan: Dict,
        original_question: str
    ) -> List[str]:
        """Use LLM to generate contextual insights"""
        
        # Create summary statistics
        summary = self._create_data_summary(df)
        
        prompt = f"""Analyze this data and provide 3-5 key insights.
        
        Original Question: {original_question}
        
        Analysis Plan: {json.dumps(plan, indent=2)}
        
        Data Summary:
        {summary}
        
        Sample Data:
        {df.head(10).to_string()}
        
        Provide insights that:
        1. Answer the original question
        2. Highlight interesting patterns or trends
        3. Identify anomalies or outliers
        4. Provide business context
        5. Are specific and actionable
        
        Format each insight as a single sentence.
        """
        
        response = await self.llm.apredict(prompt)
        
        # Parse insights from response
        insights = [
            line.strip().lstrip('- ').lstrip('•').strip()
            for line in response.split('\n')
            if line.strip() and len(line.strip()) > 20
        ]
        
        return insights[:5]  # Limit to top 5
    
    def _create_data_summary(self, df: pd.DataFrame) -> str:
        """Create textual summary of dataframe"""
        summary_parts = [
            f"Total rows: {len(df)}",
            f"Columns: {', '.join(df.columns.tolist())}",
            "\nNumerical Summary:"
        ]
        
        # Add numerical column summaries
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            summary_parts.append(numeric_df.describe().to_string())
        
        return "\n".join(summary_parts)

class StatisticalAnalyzer:
    """Perform statistical analysis on data"""
    
    def analyze(self, df: pd.DataFrame, plan: Dict) -> List[str]:
        """Perform statistical analysis and generate insights"""
        insights = []
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            # Trend detection
            if len(df) > 3:
                trend = self._detect_trend(df[col].values)
                if trend:
                    insights.append(trend)
            
            # Outlier detection
            outliers = self._detect_outliers(df[col].values)
            if outliers:
                insights.append(outliers)
            
            # Variance analysis
            variance = self._analyze_variance(df[col].values)
            if variance:
                insights.append(variance)
        
        return insights
    
    def _detect_trend(self, values: np.ndarray) -> Optional[str]:
        """Detect trend in time series"""
        if len(values) < 3:
            return None
        
        # Simple linear regression
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        if abs(r_value) > 0.7 and p_value < 0.05:
            direction = "increasing" if slope > 0 else "decreasing"
            strength = "strong" if abs(r_value) > 0.9 else "moderate"
            return f"Data shows a {strength} {direction} trend (R² = {r_value**2:.2f})"
        
        return None
    
    def _detect_outliers(self, values: np.ndarray) -> Optional[str]:
        """Detect outliers using IQR method"""
        Q1 = np.percentile(values, 25)
        Q3 = np.percentile(values, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = values[(values < lower_bound) | (values > upper_bound)]
        
        if len(outliers) > 0:
            return f"Detected {len(outliers)} outlier(s) in the data"
        
        return None
```

### 2.5 Supporting Services

#### Schema Manager

```python
from typing import Dict, List, Optional
from sqlalchemy import create_engine, inspect, MetaData
from sentence_transformers import SentenceTransformer
import pinecone

class SchemaManager:
    """Manages database schema metadata and semantic search"""
    
    def __init__(
        self,
        db_url: str,
        vector_store_config: Dict,
        metadata_store_config: Dict
    ):
        # Database connection
        self.engine = create_engine(db_url)
        self.inspector = inspect(self.engine)
        self.metadata = MetaData()
        
        # Vector store for semantic search
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_index = self._init_vector_store(vector_store_config)
        
        # Metadata store
        self.metadata_db = create_engine(metadata_store_config['url'])
    
    def discover_schema(self) -> Dict:
        """Discover complete database schema"""
        schema = {
            "database": self.engine.url.database,
            "tables": {}
        }
        
        for table_name in self.inspector.get_table_names():
            table_info = self._extract_table_info(table_name)
            schema["tables"][table_name] = table_info
            
            # Create embeddings and store
            self._index_table(table_name, table_info)
        
        return schema
    
    def _extract_table_info(self, table_name: str) -> Dict:
        """Extract detailed information about a table"""
        return {
            "name": table_name,
            "columns": self.inspector.get_columns(table_name),
            "primary_keys": self.inspector.get_pk_constraint(table_name),
            "foreign_keys": self.inspector.get_foreign_keys(table_name),
            "indexes": self.inspector.get_indexes(table_name),
            "description": self._get_table_description(table_name),
            "row_count": self._get_row_count(table_name),
            "sample_data": self._get_sample_data(table_name)
        }
    
    def find_relevant_tables(
        self, 
        question: str, 
        top_k: int = 5
    ) -> List[str]:
        """Find tables relevant to the question using semantic search"""
        
        # Create embedding for question
        question_embedding = self.embedding_model.encode(question).tolist()
        
        # Search vector store
        results = self.vector_index.query(
            vector=question_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Extract table names
        relevant_tables = [
            match.metadata['table_name']
            for match in results.matches
        ]
        
        return relevant_tables
    
    def get_schema_summary(self, table_names: List[str]) -> str:
        """Get textual summary of schema for tables"""
        summary_parts = []
        
        for table_name in table_names:
            table_info = self._extract_table_info(table_name)
            
            summary = f"\nTable: {table_name}\n"
            summary += f"Description: {table_info['description']}\n"
            summary += "Columns:\n"
            
            for col in table_info['columns']:
                summary += f"  - {col['name']} ({col['type']})"
                if not col['nullable']:
                    summary += " NOT NULL"
                summary += "\n"
            
            # Add relationships
            if table_info['foreign_keys']:
                summary += "Relationships:\n"
                for fk in table_info['foreign_keys']:
                    summary += f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n"
            
            summary_parts.append(summary)
        
        return "\n".join(summary_parts)
    
    def get_similar_queries(
        self, 
        question: str, 
        top_k: int = 3
    ) -> List[Dict]:
        """Retrieve similar historical queries (RAG approach)"""
        
        # Create embedding
        embedding = self.embedding_model.encode(question).tolist()
        
        # Search query history
        results = self.vector_index.query(
            vector=embedding,
            top_k=top_k,
            namespace="queries",
            include_metadata=True
        )
        
        similar_queries = [
            {
                "question": match.metadata['question'],
                "sql": match.metadata['sql'],
                "success": match.metadata['success']
            }
            for match in results.matches
            if match.metadata.get('success', False)
        ]
        
        return similar_queries
```

---

## 3. Data Flow

### 3.1 Query Execution Flow

```
1. User Input
   │
   ├─> Frontend validates input
   │   └─> WebSocket connection established
   │
2. API Gateway
   │
   ├─> Authenticate user (JWT validation)
   ├─> Check rate limits
   ├─> Create session
   └─> Route to orchestrator
   │
3. Planner Agent
   │
   ├─> Parse question
   ├─> Check conversation context
   ├─> Find relevant tables (semantic search)
   ├─> Create analysis plan
   └─> Pass to SQL Agent
   │
4. SQL Agent
   │
   ├─> Retrieve schema details
   ├─> Get similar queries (RAG)
   ├─> Generate SQL with LLM
   ├─> Clean and format SQL
   └─> Pass to Validator
   │
5. Validator
   │
   ├─> Check for dangerous operations
   ├─> Validate syntax
   ├─> Estimate query cost
   ├─> If invalid: return to SQL Agent (retry)
   └─> If valid: pass to Executor
   │
6. Executor
   │
   ├─> Check query cache
   │   ├─> If cached: return cached result
   │   └─> If not cached: continue
   │
   ├─> Execute SQL query
   ├─> Handle pagination
   ├─> Cache results
   └─> Pass results to Visualization Agent
   │
7. Visualization Agent
   │
   ├─> Analyze result data
   ├─> Select chart type
   ├─> Generate visualization config
   ├─> Prepare chart data
   └─> Pass to Insight Agent
   │
8. Insight Agent
   │
   ├─> Perform statistical analysis
   ├─> Generate insights with LLM
   ├─> Create recommendations
   ├─> Suggest follow-up questions
   └─> Return complete response
   │
9. API Response
   │
   ├─> Format response
   ├─> Log to audit trail
   ├─> Update metrics
   └─> Send to frontend
   │
10. Frontend Display
    │
    ├─> Render visualization
    ├─> Display insights
    ├─> Show recommendations
    └─> Update query history
```

### 3.2 Error Recovery Flow

```
Error Detected
   │
   ├─> Classify error type
   │   ├─> SQL syntax error
   │   ├─> Database connection error
   │   ├─> Timeout error
   │   └─> Permission error
   │
   ├─> Determine recovery strategy
   │   │
   │   ├─> Automatic Recovery
   │   │   ├─> Retry with backoff
   │   │   ├─> Reformulate query
   │   │   └─> Use cached result
   │   │
   │   └─> User Intervention
   │       ├─> Request clarification
   │       ├─> Suggest corrections
   │       └─> Provide error details
   │
   └─> Log error for analysis
```

---

## 4. Security Architecture

### 4.1 Authentication Flow

```
User Login
   │
   ├─> [SSO Provider] or [Email/Password]
   │
   ├─> Validate credentials
   │
   ├─> Generate JWT token
   │   ├─> Access token (15 min expiry)
   │   └─> Refresh token (7 days expiry)
   │
   └─> Return tokens to client

Authenticated Request
   │
   ├─> Extract JWT from Authorization header
   │
   ├─> Validate JWT signature
   │
   ├─> Check expiration
   │   ├─> If expired: reject (401)
   │   └─> If valid: continue
   │
   ├─> Extract user_id and roles
   │
   └─> Attach to request context
```

### 4.2 Authorization Model

```
Request for Database Query
   │
   ├─> Check user permissions
   │   ├─> Database-level access
   │   ├─> Table-level access
   │   └─> Row-level security
   │
   ├─> Validate SQL query
   │   ├─> Parse SQL
   │   ├─> Extract tables/columns
   │   └─> Check permissions for each
   │
   ├─> Apply row-level filters
   │   └─> Inject WHERE clause if needed
   │
   └─> Execute with validated permissions
```

### 4.3 Data Protection

```
Data at Rest:
  - Database: AES-256 encryption
  - File Storage: S3 server-side encryption
  - Backups: Encrypted with KMS

Data in Transit:
  - API: TLS 1.3
  - Database connections: SSL/TLS
  - Internal services: mTLS

PII Handling:
  - Identify PII columns in schema
  - Mask PII in results (if user lacks permission)
  - Log PII access to audit trail
  - Support right-to-deletion (GDPR)
```

---

## 5. Scalability & Performance

### 5.1 Horizontal Scaling

**API Gateway:**
- Multiple instances behind load balancer
- Stateless design
- Session data in Redis
- Auto-scaling based on CPU/memory

**Agent Workers:**
- Agent pool pattern
- Queue-based distribution
- Parallel processing where possible
- Auto-scaling based on queue depth

**Caching Strategy:**
```
L1 Cache (Application):
  - In-memory LRU cache
  - Schema metadata
  - User preferences
  - TTL: 5 minutes

L2 Cache (Redis):
  - Query results
  - Rendered visualizations
  - User sessions
  - TTL: 1 hour (configurable)

L3 Cache (CDN):
  - Static assets
  - Public dashboards
  - TTL: 24 hours
```

### 5.2 Database Optimization

**Connection Pooling:**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

**Query Optimization:**
- Automatic EXPLAIN ANALYZE for slow queries
- Index suggestions based on query patterns
- Query plan caching
- Result set pagination

---

## 6. Disaster Recovery

### 6.1 Backup Strategy

**Application Data:**
- Metadata database: Daily full + hourly incremental
- User data: Real-time replication
- Query history: Daily snapshots
- Retention: 30 days

**Recovery Objectives:**
- RPO (Recovery Point Objective): 1 hour
- RTO (Recovery Time Objective): 4 hours

### 6.2 High Availability

**Architecture:**
```
Active-Active Setup:
  - Multiple regions
  - Load balancing across regions
  - Data replication
  - Failover < 30 seconds

Database:
  - Primary-replica setup
  - Automatic failover
  - Read replicas for scaling
  - Point-in-time recovery
```

---

**Document Status**: Design Complete  
**Next Review**: Implementation Phase  
**Document Owner**: Principal Architect

