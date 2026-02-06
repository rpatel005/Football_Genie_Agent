# ⚽ Football Agent

An **agentic web application** for football analytics powered by **LangGraph**, **LangChain**, and **ChromaDB**. Built as a microservices architecture with separate backend API and frontend services.

![Football Agent](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Football Agent System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────┐         ┌──────────────────────────┐     │
│   │     Frontend     │  HTTP   │      Backend API          │     │
│   │   (Port 3000)    │◄───────►│     (Port 8000)           │     │
│   │                  │   REST  │                           │     │
│   │  • HTML/CSS/JS   │         │  • FastAPI               │     │
│   │  • Glassmorphism │         │  • LangGraph Agent       │     │
│   │  • Responsive    │         │  • LangChain Tools       │     │
│   └──────────────────┘         │  • ChromaDB Vector Store │     │
│                                │  • Groq / OpenAI LLM     │     │
│                                └──────────────────────────┘     │
│                                           │                      │
│                                           ▼                      │
│                                ┌──────────────────┐             │
│                                │    ChromaDB      │             │
│                                │  (Vector Store)  │             │
│                                └──────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 What It Does

Football Agent is an AI-powered assistant that understands your football-related questions in natural language and takes action to get you the information you need.

**Example queries:**
- "Show me today's Premier League matches"
- "Compare Manchester City and Arsenal stats"
- "Get the current league standings"
- "Find top scorers from Liverpool"
- "Save Chelsea to my favorites"

## ✨ Features

### 1. LangGraph Agent
- **Natural Language Understanding**: Supports Groq or OpenAI LLMs
- **Stateful Workflows**: LangGraph manages conversation state
- **Tool Execution**: 6 LangChain tools for football data
- **Semantic Search**: ChromaDB vector store for knowledge retrieval

### 2. Server-Side Tools (6 LangChain Tools)
| Tool | Description | Requires Approval |
|------|-------------|-------------------|
| `fetch_matches` | Get live/upcoming football matches with filters | No |
| `get_team_stats` | Get detailed team statistics | No |
| `get_league_standings` | Get league table with analysis | No |
| `search_players` | Search players by name, team, position | No |
| `save_favorite_team` | Save team to favorites | **Yes** ✅ |
| `search_knowledge` | Semantic search in knowledge base | No |

### 3. Client-Side Actions (4 Actions)
| Action | Description |
|--------|-------------|
| `filter_results` | Dynamic filtering and sorting of results |
| `export_data` | Download results as CSV or JSON |
| `update_chart` | Display visual charts for statistics |
| `add_to_watchlist` | Add matches to personal watchlist |

### 4. Knowledge System (ChromaDB)
- **Semantic Search**: Vector-based similarity search
- **Favorite Teams**: Save and track your favorite teams
- **Search History**: Recent queries for quick re-execution
- **Knowledge Influence**: UI shows when knowledge affected results

### 5. Modern UI Design
- 🎨 Glassmorphism effects with backdrop blur
- 🌈 Gradient backgrounds and accents
- ✨ Smooth CSS animations
- 📱 Fully responsive design
- 🌙 Dark theme optimized

## 🚀 Quick Start
 
### One-Command Setup (Linux / macOS / Windows Git Bash)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/sportsradar.git
cd sportsradar

# Run the setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Detect your OS (Linux, macOS, Windows)
- Check for Python 3.11+ and Node.js 18+
- Create `.env` from `.env.example`
- Prompt for your LLM API key (Groq or OpenAI)
- Create Python virtual environment
- Install all dependencies
- Start backend (port 8000) and frontend (port 3000)

Press `Ctrl+C` to stop all services.

### Option 1: Docker Compose (Recommended)

```bash
# Clone and set up environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY or OPENAI_API_KEY

# Run with Docker Compose
docker-compose up --build

# Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Option 2: Manual Setup (Development)

#### Terminal 1 - Backend API:
```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -e ".[dev]"

# Set up environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY or OPENAI_API_KEY

# Run backend
uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend:
```bash
cd frontend-react

# Install dependencies
npm install

# Start development server
npm run dev
```

### Option 3: PowerShell Scripts

```powershell
# Start both services
.\scripts\start-dev.ps1

# Or start individually
.\scripts\start-backend.ps1  # Backend on port 8000
.\scripts\start-frontend.ps1 # Frontend on port 3000
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# LLM API Keys (set at least one - Groq is checked first)
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Model names (optional - defaults provided)
GROQ_MODEL=qwen/qwen3-32b-instant
OPENAI_MODEL=gpt-4o

# Backend Configuration
BACKEND_PORT=8000
API_URL=http://localhost:8000/api

# Frontend Configuration  
FRONTEND_PORT=3000
FRONTEND_URL=http://localhost:3000
```

**LLM Provider Priority:**
1. If `GROQ_API_KEY` is set → uses Groq
2. Else if `OPENAI_API_KEY` is set → uses OpenAI

### Frontend API URL

Edit `frontend/index.html` to change the backend API URL:

```html
<script>
    window.FOOTBALL_API_URL = 'http://localhost:8000/api';
</script>
```

## 📁 Project Structure

```
sportsradar/
├── backend/                    # Backend API Microservice
│   ├── __init__.py
│   ├── server.py              # FastAPI REST API
│   ├── langgraph_agent.py     # LangGraph agent workflow
│   ├── langchain_tools.py     # LangChain tool definitions
│   ├── vector_store.py        # ChromaDB vector store
│   ├── football_data.py       # Football data service
│   ├── models.py              # Pydantic data models
│   └── Dockerfile             # Backend container
├── frontend/                   # Frontend Microservice
│   ├── index.html             # Main HTML page
│   ├── styles.css             # Glassmorphism CSS
│   ├── app.js                 # Frontend JavaScript
│   ├── package.json           # Node.js config
│   ├── nginx.conf             # Nginx configuration
│   └── Dockerfile             # Frontend container
├── scripts/                    # PowerShell scripts
│   ├── start-backend.ps1      # Start backend
│   ├── start-frontend.ps1     # Start frontend
│   └── start-dev.ps1          # Start both services
├── tests/                      # Test suite
│   ├── test_api.py
│   └── test_football_data.py
├── chroma_db/                  # ChromaDB data directory
├── docker-compose.yml          # Docker orchestration
├── pyproject.toml              # Python dependencies
├── .env.example                # Environment template
└── README.md
```

## 🔌 API Endpoints

### Base URLs
- **Backend API**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000`

### Agent Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/agent/chat` | Send message to agent |
| `POST` | `/api/agent/goal` | Legacy endpoint (→ chat) |
| `POST` | `/api/agent/approve` | Approve/reject actions |
| `GET` | `/api/agent/session/{id}` | Get session state |
| `GET` | `/api/agent/info` | Agent configuration info |

### Knowledge Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/knowledge` | Get knowledge items |
| `POST` | `/api/knowledge` | Add knowledge item |
| `DELETE` | `/api/knowledge/{id}` | Delete item |
| `GET` | `/api/knowledge/search` | Semantic search |
| `GET` | `/api/knowledge/favorites` | Get favorite teams |
| `GET` | `/api/knowledge/history` | Get search history |

### Utility Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tools` | Available tools info |
| `GET` | `/api/health` | Health check |
| `GET` | `/docs` | Swagger API docs |
| `GET` | `/redoc` | ReDoc API docs |

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run with verbose output
pytest -v --tb=short
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Containers
```bash
# Build backend
docker build -t football-agent-api -f backend/Dockerfile .

# Build frontend
docker build -t football-agent-frontend -f frontend/Dockerfile frontend/

# Run backend (with Groq)
docker run -p 8000:8000 -e GROQ_API_KEY=your_key football-agent-api

# Or with OpenAI
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key football-agent-api

# Run frontend
docker run -p 3000:3000 football-agent-frontend
```

## 🔧 Tech Stack

### Backend
- **Python 3.12** - Runtime
- **FastAPI** - REST API framework
- **LangGraph** - Agent workflow orchestration
- **LangChain** - Tool definitions & LLM integration
- **LangChain-Groq** - Groq LLM provider
- **LangChain-OpenAI** - OpenAI LLM provider
- **ChromaDB** - Vector database
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **HTML5/CSS3/JavaScript** - Core web technologies
- **ReactJs** - Modern UI aesthetics

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Service orchestration

## ⚖️ Tradeoffs & Design Decisions

### Why Microservices?
- **Independent Scaling**: Scale backend and frontend separately
- **Technology Flexibility**: Swap frontend framework without touching backend
- **Development Workflow**: Teams can work independently
- **Deployment Options**: Deploy to different services/hosts

### Why LangGraph + Groq/OpenAI?
- **Groq**: fast inference for LLMs (recommended) and Free but limited tokens/uses.
- **OpenAI**: GPT-4o for high quality responses but paid.
- **LangGraph**: Stateful agent workflows with proper tool handling

---

Built with ❤️ for Sportradar
