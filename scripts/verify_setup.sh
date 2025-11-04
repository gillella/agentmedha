#!/bin/bash

# AgentMedha Setup Verification Script
# This script verifies that the development environment is properly configured

set -e  # Exit on any error

echo "🔍 AgentMedha Setup Verification"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check Docker
echo "1. Checking Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker installed: $DOCKER_VERSION"
else
    print_error "Docker not found. Please install Docker."
    exit 1
fi

# Check Docker Compose
echo ""
echo "2. Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_success "Docker Compose installed: $COMPOSE_VERSION"
else
    print_error "Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Check if Docker daemon is running
echo ""
echo "3. Checking Docker daemon..."
if docker info &> /dev/null; then
    print_success "Docker daemon is running"
else
    print_error "Docker daemon is not running. Please start Docker."
    exit 1
fi

# Check Python
echo ""
echo "4. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python installed: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.11+."
    exit 1
fi

# Check Poetry
echo ""
echo "5. Checking Poetry..."
if command -v poetry &> /dev/null; then
    POETRY_VERSION=$(poetry --version)
    print_success "Poetry installed: $POETRY_VERSION"
else
    print_error "Poetry not found. Please install Poetry."
    echo "   Install with: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check Node.js
echo ""
echo "6. Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js installed: $NODE_VERSION"
else
    print_error "Node.js not found. Please install Node.js 18+."
    exit 1
fi

# Check npm/yarn
echo ""
echo "7. Checking package manager..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm installed: $NPM_VERSION"
else
    print_error "npm not found."
    exit 1
fi

# Check infrastructure services
echo ""
echo "8. Checking infrastructure services..."
SERVICES_RUNNING=0

if docker ps | grep -q agentmedha-postgres; then
    print_success "PostgreSQL container is running"
    ((SERVICES_RUNNING++))
else
    print_info "PostgreSQL container not running"
fi

if docker ps | grep -q agentmedha-redis; then
    print_success "Redis container is running"
    ((SERVICES_RUNNING++))
else
    print_info "Redis container not running"
fi

if docker ps | grep -q agentmedha-prometheus; then
    print_success "Prometheus container is running"
    ((SERVICES_RUNNING++))
else
    print_info "Prometheus container not running"
fi

if docker ps | grep -q agentmedha-grafana; then
    print_success "Grafana container is running"
    ((SERVICES_RUNNING++))
else
    print_info "Grafana container not running"
fi

if [ $SERVICES_RUNNING -eq 0 ]; then
    print_info "No infrastructure services running. Start them with: docker-compose up -d"
fi

# Check backend dependencies
echo ""
echo "9. Checking backend dependencies..."
if [ -d "backend" ]; then
    cd backend
    if [ -f "poetry.lock" ]; then
        print_success "Backend dependencies locked"
        if poetry check &> /dev/null; then
            print_success "Backend poetry configuration valid"
        else
            print_error "Backend poetry configuration invalid"
        fi
    else
        print_info "Backend dependencies not installed. Run: cd backend && poetry install"
    fi
    cd ..
else
    print_error "Backend directory not found"
fi

# Check frontend dependencies
echo ""
echo "10. Checking frontend dependencies..."
if [ -d "frontend" ]; then
    if [ -d "frontend/node_modules" ]; then
        print_success "Frontend dependencies installed"
    else
        print_info "Frontend dependencies not installed. Run: cd frontend && npm install"
    fi
else
    print_error "Frontend directory not found"
fi

# Check environment files
echo ""
echo "11. Checking environment configuration..."
if [ -f "backend/.env" ]; then
    print_success "Backend .env file exists"
else
    print_info "Backend .env not found. Copy from .env.example and configure."
fi

# Summary
echo ""
echo "================================"
echo "✨ Verification Complete!"
echo ""
if [ $SERVICES_RUNNING -eq 4 ]; then
    print_success "All infrastructure services are running!"
    print_info "You can now start the backend and frontend."
elif [ $SERVICES_RUNNING -gt 0 ]; then
    print_info "Some services are running. Check which ones need to be started."
else
    print_info "Start infrastructure with: docker-compose up -d"
fi

echo ""
echo "Next steps:"
echo "  1. Start infrastructure: docker-compose up -d"
echo "  2. Set up backend: cd backend && poetry install && poetry run alembic upgrade head"
echo "  3. Start backend: cd backend && poetry run uvicorn app.main:app --reload"
echo "  4. Set up frontend: cd frontend && npm install"
echo "  5. Start frontend: cd frontend && npm run dev"
echo ""














