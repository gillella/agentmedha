# Gmail MCP Server Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY gmail_mcp_server.py .
COPY gmail_http_server.py .

# Create credentials directory
RUN mkdir -p /app/credentials

# Environment variables
ENV GMAIL_CREDENTIALS_PATH=/app/credentials/gmail_oauth_credentials.json
ENV GMAIL_TOKEN_PATH=/app/credentials/gmail_oauth_token.json
ENV PYTHONUNBUFFERED=1

# Expose HTTP port
EXPOSE 8001

# Run the HTTP server (can also run MCP server via different entrypoint)
CMD ["python", "-m", "uvicorn", "gmail_http_server:app", "--host", "0.0.0.0", "--port", "8001"]
