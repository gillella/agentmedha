#!/bin/bash
# AgentMedha Development Startup Script
# This script starts all services and opens the UI in your browser

set -e

echo "🚀 Starting AgentMedha Development Environment..."
echo ""

# Change to project directory
cd "$(dirname "$0")/.."

# Start Docker services
echo "📦 Starting infrastructure (PostgreSQL, Redis, Prometheus, Grafana)..."
docker-compose up -d db redis prometheus grafana
sleep 5

# Start backend
echo "🔧 Starting backend API..."
docker-compose up -d backend
sleep 8

# Check if frontend is already running
if lsof -i :5173 > /dev/null 2>&1; then
    echo "✅ Frontend already running on port 5173"
else
    echo "🎨 Starting frontend..."
    cd frontend
    npm run dev > /tmp/agentmedha-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "   Frontend PID: $FRONTEND_PID"
    cd ..
    sleep 5
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ AgentMedha is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Services:"
echo "   • Frontend:   http://localhost:5173"
echo "   • Backend:    http://localhost:8000"
echo "   • API Docs:   http://localhost:8000/docs"
echo "   • Grafana:    http://localhost:3001"
echo "   • Prometheus: http://localhost:9090"
echo ""
echo "🔐 Demo Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""

# Wait a moment for everything to be ready
sleep 2

# Open the UI in browser
echo "🌐 Opening AgentMedha in your browser..."
open http://localhost:5173

echo ""
echo "✨ Ready to go! Happy analyzing! ✨"
echo ""














