"""
FastAPI Backend Server for Football Agent.
Pure REST API microservice - no frontend serving.
Uses LangGraph for agentic AI workflows.
Focused on American Football: NFL, College Football, CFL, XFL, USFL.
"""

import os
import logging
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .langgraph_agent import langgraph_agent
from .vector_store import vector_store
from .langchain_tools import FOOTBALL_TOOLS, get_tools_description

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('🏈 FootballAPI')


# Configuration from environment
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", f"{FRONTEND_URL},http://localhost:3000,http://127.0.0.1:3000").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("=" * 50)
    print("🏈 Football Agent API Service")
    print("=" * 50)
    print(f"🌐 API running on port {os.getenv('PORT', 8000)}")
    print(f"🔗 Frontend expected at: {FRONTEND_URL}")
    print("🤖 Using LangGraph + LangChain for AI")
    print("📚 ChromaDB vector store initialized")
    print("🏈 Leagues: NFL, College Football, CFL, XFL, USFL")
    if langgraph_agent.use_llm:
        print(f"✅ LLM configured: {langgraph_agent.llm_provider.upper()} ({langgraph_agent.model_name})")
    else:
        print("⚠️ No LLM API key found - agent will provide helpful error messages")
    print("=" * 50)
    yield
    # Shutdown
    print("🏈 Football Agent API shutting down...")


app = FastAPI(
    title="Football Agent API",
    description="Microservice API for American Football data analysis. Supports NFL, College Football, CFL, XFL, USFL.",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware for frontend microservice
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Session-ID"],
)


# ============ Request/Response Models ============

class ChatRequest(BaseModel):
    """Request for chat/goal submission."""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from the agent."""
    session_id: str
    response: str
    tool_results: List[dict] = []
    pending_approval: Optional[dict] = None
    client_actions: List[dict] = []
    knowledge_used: List[dict] = []


class ApprovalRequest(BaseModel):
    """Request to approve/reject an action."""
    session_id: str
    tool_call_id: str
    approved: bool


class AddKnowledgeRequest(BaseModel):
    """Request body for adding knowledge."""
    type: str
    content: dict
    tags: Optional[List[str]] = None


# ============ Agent Endpoints ============

@app.post("/api/agent/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Send a message to the football agent.
    The agent will process the message, use tools as needed, and return a response.
    """
    logger.info(f"📨 /api/agent/chat | Session: {request.session_id or 'new'}")
    logger.info(f"   Message: {request.message[:80]}{'...' if len(request.message) > 80 else ''}")
    try:
        result = await langgraph_agent.process_message(
            message=request.message,
            session_id=request.session_id
        )
        logger.info(f"   ✅ Response generated successfully")
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"   ❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Legacy endpoint redirects to new chat endpoint
@app.post("/api/agent/goal")
async def submit_goal(request: ChatRequest):
    """
    Legacy endpoint - redirects to /api/agent/chat.
    """
    return await chat_with_agent(request)


@app.post("/api/agent/approve")
async def approve_action(request: ApprovalRequest):
    """
    Approve or reject an action that requires user approval.
    """
    try:
        result = await langgraph_agent.approve_action(
            session_id=request.session_id,
            tool_call_id=request.tool_call_id,
            approved=request.approved
        )
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agent/session/{session_id}")
async def get_session(session_id: str):
    """
    Get the current state of a session.
    """
    state = langgraph_agent.get_session_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "state": state}


# ============ Knowledge Endpoints ============

@app.get("/api/knowledge")
async def get_knowledge(query: Optional[str] = None, limit: int = 20):
    """
    Get knowledge items. Supports semantic search with ChromaDB.
    """
    if query:
        results = vector_store.search(query, n_results=limit)
        return {
            "items": results,
            "count": len(results),
            "search_query": query
        }
    
    # Return all knowledge items
    results = vector_store.get_all(limit=limit)
    return {
        "items": results,
        "count": len(results)
    }


@app.post("/api/knowledge")
async def add_knowledge(request: AddKnowledgeRequest):
    """
    Add a new knowledge item to the vector store.
    """
    from .vector_store import KnowledgeDocument
    
    content_text = str(request.content)
    if isinstance(request.content, dict):
        content_text = " ".join(str(v) for v in request.content.values())
    
    doc = KnowledgeDocument(
        type=request.type,
        content=content_text,
        metadata={
            "type": request.type,
            "tags": ",".join(request.tags or []),
            "source": "user_added",
            "content_json": str(request.content)
        }
    )
    doc_id = vector_store.add(doc)
    
    return {
        "id": doc_id,
        "type": request.type,
        "message": "Knowledge item added"
    }


@app.delete("/api/knowledge/{item_id}")
async def delete_knowledge(item_id: str):
    """
    Delete a knowledge item.
    """
    success = vector_store.delete(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted", "item_id": item_id}


@app.get("/api/knowledge/search")
async def search_knowledge(query: str, n_results: int = 5):
    """
    Semantic search in the knowledge base using ChromaDB.
    """
    results = vector_store.search(query, n_results=n_results)
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }


@app.get("/api/knowledge/favorites")
async def get_favorites():
    """
    Get favorite teams.
    """
    teams = vector_store.get_favorite_teams()
    return {"favorite_teams": teams}


@app.get("/api/knowledge/history")
async def get_search_history(limit: int = 10):
    """
    Get recent search history.
    """
    history = vector_store.get_search_history(limit=limit)
    return {"history": history}


# ============ Chat History Endpoints ============

class ChatMessageRequest(BaseModel):
    """Request to save a chat message."""
    message: dict
    session_id: Optional[str] = None


class ChatSessionRequest(BaseModel):
    """Request to save a chat session."""
    id: str
    title: str
    preview: str
    timestamp: Optional[str] = None
    messages: List[dict] = []


@app.get("/api/chat/history")
async def get_chat_history():
    """
    Get chat history from ChromaDB.
    """
    chat_data = vector_store.get_chat_history()
    return chat_data


@app.post("/api/chat/history")
async def save_chat_message(request: ChatMessageRequest):
    """
    Save a chat message to history.
    """
    vector_store.add_chat_message(request.message, request.session_id)
    return {"status": "saved"}


@app.delete("/api/chat/history")
async def clear_chat_history():
    """
    Clear all chat history.
    """
    vector_store.clear_chat_history()
    return {"status": "cleared"}


@app.delete("/api/chat/history/{session_id}")
async def delete_chat_session_history(session_id: str):
    """
    Delete a specific chat session.
    """
    vector_store.delete_chat_session(session_id)
    return {"status": "deleted", "session_id": session_id}


# ============ Chat Sessions Endpoints ============

@app.get("/api/chat/sessions")
async def get_chat_sessions():
    """
    Get all chat sessions.
    """
    sessions = vector_store.get_chat_sessions()
    return {"sessions": sessions}


@app.post("/api/chat/sessions")
async def save_chat_session(request: ChatSessionRequest):
    """
    Save a chat session.
    """
    vector_store.save_chat_session({
        "id": request.id,
        "title": request.title,
        "preview": request.preview,
        "timestamp": request.timestamp,
        "messages": request.messages
    })
    return {"status": "saved", "session_id": request.id}


@app.delete("/api/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """
    Delete a chat session.
    """
    vector_store.delete_chat_session(session_id)
    return {"status": "deleted", "session_id": session_id}


# ============ Calendar Endpoints ============

class CalendarMatchRequest(BaseModel):
    """Request to add a match to calendar."""
    home_team: str
    away_team: str
    date: Optional[str] = None
    time: Optional[str] = None
    league: Optional[str] = None
    venue: Optional[str] = None


class RemoveCalendarMatchRequest(BaseModel):
    """Request to remove a match from calendar."""
    home_team: str
    away_team: str


@app.get("/api/calendar")
async def get_calendar():
    """
    Get all matches in the user's personal calendar.
    """
    from .langchain_tools import get_user_calendar
    calendar = get_user_calendar()
    logger.info(f"📅 GET /api/calendar | Found {len(calendar)} matches")
    return {
        "matches": calendar,
        "count": len(calendar)
    }


@app.post("/api/calendar")
async def add_to_calendar(request: CalendarMatchRequest):
    """
    Add a match to the user's personal calendar.
    """
    logger.info(f"📅 POST /api/calendar | Adding: {request.home_team} vs {request.away_team}")
    from .langchain_tools import add_match_to_calendar
    
    result = add_match_to_calendar.invoke({
        "home_team": request.home_team,
        "away_team": request.away_team,
        "date": request.date or "TBD",
        "time": request.time or "TBD",
        "league": request.league or "NFL",
        "venue": request.venue or "TBD"
    })
    
    from .langchain_tools import get_user_calendar
    calendar = get_user_calendar()
    
    logger.info(f"   ✅ Calendar now has {len(calendar)} matches")
    return {
        "message": f"Added {request.home_team} vs {request.away_team} to calendar",
        "matches": calendar,
        "count": len(calendar)
    }


@app.delete("/api/calendar")
async def remove_from_calendar(request: RemoveCalendarMatchRequest):
    """
    Remove a match from the user's personal calendar.
    """
    logger.info(f"📅 DELETE /api/calendar | Removing: {request.home_team} vs {request.away_team}")
    from .langchain_tools import remove_match_from_calendar, get_user_calendar
    
    result = remove_match_from_calendar.invoke({
        "home_team": request.home_team,
        "away_team": request.away_team
    })
    
    calendar = get_user_calendar()
    
    logger.info(f"   ✅ Calendar now has {len(calendar)} matches")
    return {
        "message": f"Removed {request.home_team} vs {request.away_team} from calendar",
        "matches": calendar,
        "count": len(calendar)
    }


# ============ Tools Info Endpoint ============

@app.get("/api/tools")
async def get_available_tools():
    """
    Get information about available agent tools.
    """
    tools_info = get_tools_description()
    return {
        "tools": tools_info,
        "count": len(FOOTBALL_TOOLS),
        "agent_type": "LangGraph"
    }


# ============ Agent Info Endpoint ============

@app.get("/api/agent/info")
async def get_agent_info():
    """
    Get information about the current agent configuration.
    """
    return {
        "agent_type": "LangGraph + LangChain",
        "llm_enabled": langgraph_agent.use_llm,
        "vector_store": "ChromaDB",
        "tools_count": len(FOOTBALL_TOOLS),
        "features": [
            "Natural language understanding",
            "Semantic knowledge search",
            "Tool execution with approval flow",
            "Conversation memory",
            "Client-side action generation"
        ]
    }


# ============ Health Check ============

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "football-agent-api",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "agent": "LangGraph",
        "llm_enabled": langgraph_agent.use_llm,
        "vector_store": "ChromaDB"
    }


# ============ Football Data Endpoints ============

from .football_data import football_service

@app.get("/api/football/games")
async def get_football_games(
    league: str = "nfl",
    week: Optional[int] = None,
    date: Optional[str] = None,
    team: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get football games for a league.
    
    Args:
        league: Football league (nfl, college-football, cfl, xfl, usfl)
        week: Week number (NFL/college)
        date: Date filter (today, tomorrow, YYYY-MM-DD)
        team: Filter by team name
        status: Filter by status (scheduled, live, finished)
    """
    try:
        matches = football_service.get_matches(
            league=league,
            week=week,
            date=date,
            team=team,
            status=status
        )
        return {"games": [m.model_dump() for m in matches], "league": league}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Legacy endpoint for backwards compatibility
@app.get("/api/sports/matches")
async def get_matches(league: str = "nfl", date: Optional[str] = None):
    """Legacy endpoint - redirects to /api/football/games."""
    return await get_football_games(league=league, date=date)


@app.get("/api/football/standings")
async def get_football_standings(league: str = "nfl", conference: Optional[str] = None):
    """
    Get football league standings.
    
    Args:
        league: Football league (nfl, college-football, cfl)
        conference: Conference filter (AFC, NFC, SEC, Big Ten, etc.)
    """
    try:
        standings = football_service.get_league_standings(league=league, conference=conference)
        return {"standings": [s.model_dump() for s in standings], "league": league}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Legacy endpoint
@app.get("/api/sports/standings")
async def get_standings(league: str = "nfl"):
    """Legacy endpoint - redirects to /api/football/standings."""
    return await get_football_standings(league=league)


@app.get("/api/football/teams")
async def get_football_teams(league: str = "nfl"):
    """
    Get all teams in a football league.
    """
    try:
        teams = football_service.get_teams(league=league)
        return {"teams": teams, "league": league}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Legacy endpoint
@app.get("/api/sports/teams")
async def get_teams(league: str = "nfl"):
    """Legacy endpoint - redirects to /api/football/teams."""
    return await get_football_teams(league=league)


@app.get("/api/football/news")
async def get_football_news(league: str = "nfl", limit: int = 10):
    """
    Get football news.
    """
    try:
        news = football_service.get_news(league=league, limit=limit)
        return {"news": news, "league": league}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Legacy endpoint
@app.get("/api/sports/news")
async def get_news(league: str = "nfl", limit: int = 10):
    """Legacy endpoint - redirects to /api/football/news."""
    return await get_football_news(league=league, limit=limit)


@app.get("/api/football/leaders")
async def get_leaders(league: str = "nfl", category: Optional[str] = None):
    """
    Get statistical leaders.
    
    Args:
        league: Football league
        category: Stat category (passing, rushing, receiving, defense)
    """
    try:
        leaders = football_service.get_leaders(league=league, category=category)
        return {"leaders": leaders, "league": league}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/football/rankings")
async def get_rankings(year: Optional[int] = None):
    """
    Get college football rankings (AP, Coaches, CFP).
    """
    try:
        rankings = football_service.get_rankings(league="college-football", year=year)
        return {"rankings": rankings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/football/injuries")
async def get_injuries(league: str = "nfl", team: Optional[str] = None):
    """
    Get injury reports.
    """
    try:
        injuries = football_service.get_injuries(league=league)
        return {"injuries": injuries, "league": league}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/football/game/{game_id}")
async def get_game_detail(game_id: str, league: str = "nfl"):
    """
    Get detailed game info including boxscore.
    """
    try:
        boxscore = football_service.get_game_boxscore(game_id, league=league)
        return {"game_id": game_id, "boxscore": boxscore, "league": league}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/football/odds/{game_id}")
async def get_game_odds(game_id: str, league: str = "nfl"):
    """
    Get betting odds for a game.
    """
    try:
        odds = football_service.get_game_odds(game_id, league=league)
        return {"game_id": game_id, "odds": odds, "league": league}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sports/odds")
async def get_odds(event_id: str, competition_id: Optional[str] = None):
    """
    Legacy endpoint for betting odds.
    """
    try:
        odds = football_service.get_game_odds(event_id, league="nfl")
        return {"odds": odds, "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sports/probabilities")
async def get_probabilities(event_id: str, competition_id: Optional[str] = None):
    """
    Get win probabilities for a game.
    """
    try:
        from .espn_api import espn_client
        probs = espn_client.get_football_game_predictions("nfl", event_id)
        return {"probabilities": probs, "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Root Endpoint ============

@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "service": "Football Agent API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "frontend": FRONTEND_URL
    }
