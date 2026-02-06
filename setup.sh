#!/bin/bash

# ============================================
# Football Agent - Local Development Setup
# ============================================
# Cross-platform script for Linux, macOS, and Windows (Git Bash/WSL)
# Requirements: Python 3.11+, Node.js 18+, npm
# Usage: ./setup.sh
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}"
    echo "========================================"
    echo "   Football Agent - Local Dev Setup"
    echo "========================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "mac" ;;
        MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

# Activate virtual environment based on OS
activate_venv() {
    local os_type=$(detect_os)
    if [ "$os_type" = "windows" ]; then
        source .venv/Scripts/activate
    else
        source .venv/bin/activate
    fi
}

# Check if .env file exists, create from example if not
setup_env() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning ".env file created from .env.example"
            print_warning "Please add your LLM API key (Groq or OpenAI) to .env"
            echo ""
            echo "The agent supports two LLM providers:"
            echo "  1) Groq (faster, recommended)"
            echo "  2) OpenAI (GPT-4o)"
            echo ""
            read -p "Which provider do you want to use? (1/2): " provider_choice
            
            if [ "$provider_choice" = "1" ]; then
                read -p "Enter your GROQ_API_KEY: " api_key
                if [ -n "$api_key" ]; then
                    if [[ "$(detect_os)" == "mac" ]]; then
                        sed -i '' "s|your_groq_api_key_here|$api_key|g" .env
                    else
                        sed -i "s|your_groq_api_key_here|$api_key|g" .env
                    fi
                    print_success "GROQ_API_KEY saved to .env"
                fi
            elif [ "$provider_choice" = "2" ]; then
                read -p "Enter your OPENAI_API_KEY: " api_key
                if [ -n "$api_key" ]; then
                    if [[ "$(detect_os)" == "mac" ]]; then
                        sed -i '' "s|your_openai_api_key_here|$api_key|g" .env
                    else
                        sed -i "s|your_openai_api_key_here|$api_key|g" .env
                    fi
                    print_success "OPENAI_API_KEY saved to .env"
                fi
            else
                print_warning "Skipped. Please manually add your API key to .env"
            fi
        else
            print_error ".env.example not found!"
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
}

# Cleanup function
cleanup() {
    echo ""
    print_info "Shutting down services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    print_success "Services stopped"
    exit 0
}

# Main
main() {
    print_header
    
    local os_type=$(detect_os)
    print_info "Detected OS: $os_type"
    echo ""
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.11+"
        echo "  Download: https://www.python.org/downloads/"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    print_success "Python $PYTHON_VERSION found"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+"
        echo "  Download: https://nodejs.org/"
        exit 1
    fi
    NODE_VERSION=$(node -v)
    print_success "Node.js $NODE_VERSION found"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    print_success "npm found"
    
    # Setup environment file
    setup_env
    
    echo ""
    
    # Setup Python virtual environment
    print_info "Setting up Python virtual environment..."
    if [ ! -d ".venv" ]; then
        $PYTHON_CMD -m venv .venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment exists"
    fi
    
    # Activate venv and install dependencies
    print_info "Installing Python dependencies..."
    activate_venv
    pip install -q -e .
    print_success "Python dependencies installed"
    
    # Install frontend dependencies
    print_info "Installing frontend dependencies..."
    cd frontend-react
    npm install --silent 2>/dev/null || npm install
    cd ..
    print_success "Frontend dependencies installed"
    
    echo ""
    print_success "Setup complete!"
    echo ""
    
    # Start services
    print_info "Starting backend server on port 8000..."
    activate_venv
    
    # Start backend in background
    uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    # Wait for backend to be ready
    print_info "Waiting for backend to start..."
    sleep 4
    
    # Start frontend
    print_info "Starting frontend server..."
    cd frontend-react
    npm run dev -- --host &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    sleep 3
    
    echo ""
    echo -e "${GREEN}========================================"
    echo -e "   Services Running!"
    echo -e "========================================${NC}"
    echo ""
    echo -e "${CYAN}  Backend API:  ${NC}http://localhost:8000"
    echo -e "${CYAN}  API Docs:     ${NC}http://localhost:8000/docs"
    echo -e "${CYAN}  Frontend:     ${NC}http://localhost:3000"
    echo ""
    print_info "Press Ctrl+C to stop all services"
    echo ""
    
    # Wait for Ctrl+C
    trap cleanup SIGINT SIGTERM
    wait
}

# Run main
main
