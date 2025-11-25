# Implementation Roadmap

## Phase 1: Foundation & Supervisor Skeleton
**Goal**: Set up the monorepo, core infrastructure, and the basic Supervisor agent.
- [ ] Initialize Monorepo (Git, Python/uv).
- [ ] Configure Environment Variables & Secrets management.
- [ ] Setup LangGraph StateGraph for the Supervisor.
- [ ] Implement basic "Chat" capability (Supervisor talking back without tools).
- [ ] Integrate LangSmith for tracing.

## Phase 2: Memory & Evaluation Framework
**Goal**: Give the agent memory and set up the quality control harness.
- [ ] Setup Qdrant (Docker or Cloud).
- [ ] Implement Memory Module (Save/Retrieve conversation history).
- [ ] Setup Evaluation Pipeline:
    - [ ] Langfuse integration.
    - [ ] RAGAS baseline tests.
    - [ ] TruLens feedback functions.
    - [ ] Phoenix installation.

## Phase 3: The First Worker - Email (MCP)
**Goal**: Implement the first real capability using MCP.
- [ ] Research/Setup MCP server for Email (e.g., Gmail).
- [ ] Create `EmailWorker` subgraph.
- [ ] Define tools: `read_email`, `draft_reply`.
- [ ] Connect Supervisor to EmailWorker.
- [ ] Test end-to-end flow: "Read my emails" -> Supervisor -> EmailWorker -> Response.

## Phase 4: Finance & Social Workers
**Goal**: Expand capabilities to Finance and Social Media.
- [ ] **Finance Worker**:
    - [ ] Mock data ingestion (or Plaid sandbox).
    - [ ] Analysis tools (Pandas/LLM).
- [ ] **Social Worker**:
    - [ ] X/LinkedIn API setup.
    - [ ] Drafting and Posting tools.

## Phase 5: Home & Pet Workers (IoT)
**Goal**: Connect to physical world APIs.
- [ ] **Home Worker**: Connect to Home Assistant API.
- [ ] **PetKit Worker**: Connect to PetKit API.

## Phase 6: Refinement & UI
**Goal**: Polish the experience and add a user interface.
- [ ] Build a simple frontend (Streamlit or Chainlit).
- [ ] Run extensive evals and optimize prompts.
- [ ] "Human-in-the-loop" UI for approving actions.
