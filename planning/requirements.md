# Requirements Document

## 1. Functional Requirements

### 1.1 Supervisor (agentMedha)
- **FR-01**: Must accept natural language queries from the user.
- **FR-02**: Must classify intent and route to the correct worker.
- **FR-03**: Must maintain context across multiple turns of conversation.
- **FR-04**: Must provide a consolidated summary of actions taken by workers.

### 1.2 Email Worker
- **FR-05**: Connect to email providers via MCP.
- **FR-06**: Fetch unread emails and summarize them.
- **FR-07**: Draft replies for user approval.
- **FR-08**: Search for specific emails based on queries.

### 1.3 Social Media Worker
- **FR-09**: Draft posts for X (Twitter) and LinkedIn.
- **FR-10**: Schedule posts for future publication.
- **FR-11**: Read and summarize notifications/mentions.

### 1.4 Finance Worker
- **FR-12**: Ingest credit card transaction data.
- **FR-13**: Calculate current balances across accounts.
- **FR-14**: Detect anomalies (e.g., "Why is my bill so high?").
- **FR-15**: Provide spending insights (e.g., "How much on coffee this month?").

### 1.5 Home Security Worker
- **FR-16**: Report status of lights, locks, and cameras.
- **FR-17**: Control devices (turn off lights, lock doors) upon request.
- **FR-18**: Monitor HVAC status.

### 1.6 PetKit Worker
- **FR-19**: Report litter box usage statistics (frequency, duration).
- **FR-20**: Alert on cleaning status or abnormalities.

## 2. Technical Requirements

### 2.1 Architecture & Code
- **TR-01**: Monorepo structure.
- **TR-02**: Python 3.11+ codebase.
- **TR-03**: Type hinting (mypy) and strict linting (ruff).
- **TR-04**: 12-Factor Agent principles (config in env, stateless processes where possible).

### 2.2 AI & Data
- **TR-05**: Flexible LLM backend (Gemini 3 default, swappable).
- **TR-06**: Qdrant for vector storage.
- **TR-07**: LangGraph for state management.

### 2.3 Observability & Evals
- **TR-08**: All runs traced in LangSmith.
- **TR-09**: Evaluation pipeline using RAGAS/TruLens for retrieval and generation quality.
- **TR-10**: Phoenix for embedding visualization.

### 2.4 Security
- **TR-11**: No API keys committed to code (use `.env`).
- **TR-12**: "Human-in-the-loop" confirmation for write actions (posting, sending email).
