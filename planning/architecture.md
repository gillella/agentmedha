# agentMedha Architecture

## Overview
agentMedha is a personal AI assistant designed using the **Supervisor Pattern (Hub-and-Spoke)**. It acts as a central brain that coordinates specialized worker agents to manage various aspects of the user's life, including email, social media, finance, home security, and pet care.

## Architectural Pattern: Supervisor (Hub-and-Spoke)
The system is composed of a top-level **Supervisor Agent** (`agentMedha`) and multiple **Worker Agents**.

### 1. Supervisor Agent (`agentMedha`)
- **Role**: The Brain / Orchestrator.
- **Responsibilities**:
    - **Input Processing**: Receives natural language requests from the user.
    - **State Management**: Maintains the global conversation state and context.
    - **Planning**: Decomposes complex user requests into actionable sub-tasks.
    - **Delegation**: Routes tasks to the appropriate Worker Agent based on capability.
    - **Synthesis**: Aggregates results from workers and formulates the final response to the user.
    - **Guardrails**: Enforces safety, privacy, and policy checks before and after delegation.

### 2. Worker Agents
Specialized agents that perform specific domains of tasks. They can be implemented as sub-graphs or tools.

*   **Email Worker**:
    *   **Role**: Manage emails.
    *   **Integration**: Uses **MCP (Model Context Protocol)** to connect to email clients/servers.
    *   **Capabilities**: Read, summarize, draft, reply, organize.
*   **Social Media Worker**:
    *   **Role**: Manage social presence.
    *   **Integration**: APIs for X (Twitter), LinkedIn, etc.
    *   **Capabilities**: Draft posts, schedule posts, analyze engagement.
*   **Finance Analyst Worker**:
    *   **Role**: Financial insights.
    *   **Integration**: Plaid (or similar) for transaction data, LLM for analysis.
    *   **Capabilities**: Analyze spending, check balances, advice on budgeting.
*   **Home Security Worker**:
    *   **Role**: Home automation and monitoring.
    *   **Integration**: Home Assistant API, SmartThings, or direct device APIs.
    *   **Capabilities**: Check camera feeds (via description/alerts), control lights, monitor HVAC.
*   **PetKit Worker**:
    *   **Role**: Pet care management.
    *   **Integration**: PETKIT API.
    *   **Capabilities**: Monitor litter box usage, cleaning cycles, pet health metrics.

## Memory Systems
### 1. Short-term Memory (Thread State)
- **Mechanism**: LangGraph Checkpointers (Postgres or SQLite).
- **Usage**: Stores the current conversation history, active plan, and immediate context.

### 2. Long-term Memory (Vector Store)
- **Mechanism**: **Qdrant**.
- **Usage**:
    - **Episodic Memory**: Storing past interactions and decisions.
    - **Semantic Knowledge**: RAG for user preferences, financial history summaries, and documentation.

## 12-Factor Agent Principles
The architecture adheres to modern agentic best practices:
1.  **Observability**: Deep tracing with LangSmith and Langfuse.
2.  **Modularity**: Each worker is an independent module/graph.
3.  **Determinism**: Structured outputs and clear state transitions.
4.  **Security**: Credentials managed via environment variables; "Human-in-the-loop" for sensitive actions (e.g., posting to social media, spending money).

## Diagram
```mermaid
graph TD
    User[User] --> Supervisor[Supervisor Agent (agentMedha)]
    
    subgraph "Memory"
        STM[Short-term State]
        LTM[Qdrant Vector DB]
    end
    
    Supervisor <--> STM
    Supervisor <--> LTM
    
    Supervisor -->|Delegates| Email[Email Worker (MCP)]
    Supervisor -->|Delegates| Social[Social Media Worker]
    Supervisor -->|Delegates| Finance[Finance Worker]
    Supervisor -->|Delegates| Home[Home Security Worker]
    Supervisor -->|Delegates| Pet[PetKit Worker]
    
    Email -->|Result| Supervisor
    Social -->|Result| Supervisor
    Finance -->|Result| Supervisor
    Home -->|Result| Supervisor
    Pet -->|Result| Supervisor
```
