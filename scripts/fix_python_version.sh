#!/bin/bash

# Script to fix Python version compatibility issue
# AgentMedha requires Python 3.11 or 3.12, but asyncpg doesn't support 3.13 yet

set -e

echo "🐍 Python Version Fix for AgentMedha"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check current Python version
CURRENT_PYTHON=$(python3 --version)
echo "Current Python: $CURRENT_PYTHON"
echo ""

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    print_error "pyenv is not installed"
    echo ""
    echo "Installing pyenv..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install pyenv
            print_success "pyenv installed via Homebrew"
        else
            print_error "Homebrew not found. Please install Homebrew first:"
            echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    else
        # Linux
        curl https://pyenv.run | bash
        print_success "pyenv installed"
    fi
    
    # Add pyenv to shell
    echo ""
    print_info "Adding pyenv to shell configuration..."
    
    if [ -f ~/.zshrc ]; then
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
        echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
        echo 'eval "$(pyenv init -)"' >> ~/.zshrc
        print_success "Added to ~/.zshrc"
    fi
    
    if [ -f ~/.bashrc ]; then
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
        echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
        echo 'eval "$(pyenv init -)"' >> ~/.bashrc
        print_success "Added to ~/.bashrc"
    fi
    
    # Initialize pyenv for current session
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
else
    print_success "pyenv is already installed"
fi

echo ""
print_info "Installing Python 3.12.7 (recommended for AgentMedha)..."
echo ""

# Install Python 3.12.7
if pyenv versions | grep -q "3.12.7"; then
    print_success "Python 3.12.7 is already installed"
else
    print_info "This may take a few minutes..."
    pyenv install 3.12.7
    print_success "Python 3.12.7 installed"
fi

echo ""
print_info "Configuring backend to use Python 3.12.7..."

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

# Set local Python version
pyenv local 3.12.7
print_success "Set Python 3.12.7 for backend directory"

# Add Poetry to PATH for current session
export PATH="$HOME/.local/bin:$PATH"

# Remove existing virtual environment
if [ -d ".venv" ]; then
    print_info "Removing existing virtual environment..."
    rm -rf .venv
fi

# Configure Poetry to use the correct Python
print_info "Configuring Poetry to use Python 3.12..."
poetry env use 3.12
print_success "Poetry environment configured"

echo ""
print_info "Installing dependencies with Poetry..."
print_info "This will take a few minutes..."
echo ""

poetry install

if [ $? -eq 0 ]; then
    echo ""
    print_success "All done! Backend dependencies installed successfully."
    echo ""
    echo "Next steps:"
    echo "  1. Restart your terminal or run: source ~/.zshrc"
    echo "  2. Create .env file: cd backend && cp .env.example .env"
    echo "  3. Add your OPENAI_API_KEY to .env"
    echo "  4. Start infrastructure: docker-compose up -d"
    echo "  5. Run migrations: poetry run alembic upgrade head"
    echo "  6. Start backend: poetry run uvicorn app.main:app --reload"
else
    print_error "Installation failed. Please check the errors above."
    exit 1
fi














