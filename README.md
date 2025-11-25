# agentMedha

agentMedha is a personal AI assistant designed using the **Supervisor Pattern (Hub-and-Spoke)**. It acts as a central brain that coordinates specialized worker agents to manage various aspects of the user's life.

## Architecture

See [Architecture Document](planning/architecture.md) for details.

## Setup

1.  **Install `uv`**:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Install Dependencies**:
    ```bash
    uv sync
    ```

3.  **Environment Variables**:
    Copy `.env.example` to `.env` and fill in your API keys.
    ```bash
    cp .env.example .env
    ```

4.  **Run**:
    ```bash
    uv run python -m agent_medha.main
    ```
