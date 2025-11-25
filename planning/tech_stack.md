# Technology Stack

## Core Frameworks
- **Orchestration**: **LangGraph**
    - Why: Best-in-class for building stateful, multi-agent workflows with cyclic graphs (Supervisor pattern).
- **Language**: **Python 3.11+**
    - Why: Dominant ecosystem for AI/ML.

## LLM & Model Selection
- **Primary Model**: **Gemini 3 Family** (Latest/Best available).
- **Model Abstraction**: **LiteLLM** or **LangChain ChatModels**.
    - Why: Allows easy swapping between Gemini, OpenAI, Anthropic, and local models (Ollama/vLLM) without code changes.

## Data & Memory
- **Vector Database**: **Qdrant**
    - Why: High performance, rust-based, excellent filtering, and local/cloud flexibility.
- **State Persistence**: **PostgreSQL** (Async)
    - Why: Robust storage for LangGraph checkpointers.

## Evaluation & Observability (The "Evals Stack")
- **Tracing & Monitoring**: **LangSmith**
    - Why: Native integration with LangGraph for debugging steps.
- **Telemetry & Experiments**: **Langfuse**
    - Why: Open source observability, prompt management, and scoring.
- **Retrieval Scoring**: **RAGAS**
    - Why: Standard metrics for RAG (Context Precision, Recall).
- **Faithfulness & Hallucination**: **TruLens**
    - Why: Feedback functions to verify if the answer is grounded in context.
- **Embedding Visualization**: **Phoenix (Arize)**
    - Why: Visualize clusters of data to detect drift or anomalies.

## Integrations
- **Email**: **Model Context Protocol (MCP)**
    - Standardized interface for connecting to data sources.
- **Social Media**: Tweepy (X), LinkedIn API.
- **Finance**: Plaid API (or CSV import + Pandas analysis).
- **Home**: Home Assistant API / Python SDKs.
- **PetKit**: `py-petkit` or custom API wrapper.

## Development Tools
- **Package Management**: `uv` (for speed) or `poetry`.
- **Linting/Formatting**: `ruff`.
- **Testing**: `pytest`.
