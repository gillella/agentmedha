#!/bin/bash
# AgentMedha Development Stop Script
# This script stops all services gracefully

set -e

echo "🛑 Stopping AgentMedha Development Environment..."
echo ""

# Change to project directory
cd "$(dirname "$0")/.."

# Stop frontend
echo "🎨 Stopping frontend..."
pkill -f "agentmedha/frontend" 2>/dev/null && echo "   ✅ Frontend stopped" || echo "   ℹ️  Frontend not running"

# Stop Docker services
echo "📦 Stopping Docker services..."
docker-compose stop

echo ""
echo "✅ All services stopped!"
echo ""














