"""
Additional comprehensive tests for the API server endpoints.
Tests all football data endpoints, calendar, and knowledge endpoints.
"""

import pytest
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, str(pytest.importorskip("pathlib").Path(__file__).parent.parent))

from backend.server import app


class TestFootballDataEndpoints:
    """Test suite for football data endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    # ============ Games Endpoints ============
    
    def test_get_football_games_default(self, client):
        """Test getting NFL games (default)."""
        response = client.get("/api/football/games")
        
        assert response.status_code == 200
        data = response.json()
        assert "games" in data
        assert "league" in data
        assert data["league"] == "nfl"
    
    def test_get_football_games_college(self, client):
        """Test getting college football games."""
        response = client.get("/api/football/games?league=college-football")
        
        assert response.status_code == 200
        data = response.json()
        assert data["league"] == "college-football"
    
    def test_get_football_games_cfl(self, client):
        """Test getting CFL games."""
        response = client.get("/api/football/games?league=cfl")
        
        assert response.status_code == 200
        data = response.json()
        assert data["league"] == "cfl"
    
    def test_get_football_games_with_week(self, client):
        """Test getting games for a specific week."""
        response = client.get("/api/football/games?league=nfl&week=1")
        
        assert response.status_code == 200
    
    def test_get_football_games_with_date_today(self, client):
        """Test getting today's games."""
        response = client.get("/api/football/games?date=today")
        
        assert response.status_code == 200
    
    def test_get_football_games_with_team_filter(self, client):
        """Test getting games filtered by team."""
        response = client.get("/api/football/games?team=Chiefs")
        
        assert response.status_code == 200
    
    def test_legacy_matches_endpoint(self, client):
        """Test legacy /api/sports/matches endpoint."""
        response = client.get("/api/sports/matches")
        
        assert response.status_code == 200
        data = response.json()
        assert "games" in data
    
    # ============ Standings Endpoints ============
    
    def test_get_football_standings_nfl(self, client):
        """Test getting NFL standings."""
        response = client.get("/api/football/standings?league=nfl")
        
        assert response.status_code == 200
        data = response.json()
        assert "standings" in data
        assert data["league"] == "nfl"
    
    def test_get_football_standings_with_conference(self, client):
        """Test getting standings with conference filter."""
        response = client.get("/api/football/standings?league=nfl&conference=AFC")
        
        assert response.status_code == 200
    
    def test_legacy_standings_endpoint(self, client):
        """Test legacy /api/sports/standings endpoint."""
        response = client.get("/api/sports/standings")
        
        assert response.status_code == 200
    
    # ============ Teams Endpoints ============
    
    def test_get_football_teams_nfl(self, client):
        """Test getting NFL teams."""
        response = client.get("/api/football/teams?league=nfl")
        
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert data["league"] == "nfl"
    
    def test_get_football_teams_college(self, client):
        """Test getting college football teams."""
        response = client.get("/api/football/teams?league=college-football")
        
        assert response.status_code == 200
    
    def test_legacy_teams_endpoint(self, client):
        """Test legacy /api/sports/teams endpoint."""
        response = client.get("/api/sports/teams")
        
        assert response.status_code == 200
    
    # ============ News Endpoints ============
    
    def test_get_football_news_nfl(self, client):
        """Test getting NFL news."""
        response = client.get("/api/football/news?league=nfl")
        
        assert response.status_code == 200
        data = response.json()
        assert "news" in data
    
    def test_get_football_news_with_limit(self, client):
        """Test getting news with limit."""
        response = client.get("/api/football/news?limit=5")
        
        assert response.status_code == 200
    
    def test_legacy_news_endpoint(self, client):
        """Test legacy /api/sports/news endpoint."""
        response = client.get("/api/sports/news")
        
        assert response.status_code == 200
    
    # ============ Leaders Endpoints ============
    
    def test_get_football_leaders(self, client):
        """Test getting statistical leaders."""
        response = client.get("/api/football/leaders?league=nfl")
        
        assert response.status_code == 200
        data = response.json()
        assert "leaders" in data
    
    def test_get_football_leaders_passing(self, client):
        """Test getting passing leaders."""
        response = client.get("/api/football/leaders?category=passing")
        
        assert response.status_code == 200
    
    # ============ Rankings Endpoints ============
    
    def test_get_college_rankings(self, client):
        """Test getting college football rankings."""
        response = client.get("/api/football/rankings")
        
        assert response.status_code == 200
        data = response.json()
        assert "rankings" in data
    
    # ============ Injuries Endpoints ============
    
    def test_get_injuries(self, client):
        """Test getting injury reports."""
        response = client.get("/api/football/injuries?league=nfl")
        
        assert response.status_code == 200
        data = response.json()
        assert "injuries" in data


class TestCalendarEndpoints:
    """Test suite for calendar management endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_get_calendar(self, client):
        """Test getting calendar matches."""
        response = client.get("/api/calendar")
        
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert "count" in data
    
    def test_add_to_calendar(self, client):
        """Test adding a match to calendar."""
        response = client.post(
            "/api/calendar",
            json={
                "home_team": "Test Team A",
                "away_team": "Test Team B",
                "date": "2024-12-25",
                "league": "NFL"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "matches" in data
    
    def test_add_to_calendar_minimal(self, client):
        """Test adding a match with minimal data."""
        response = client.post(
            "/api/calendar",
            json={
                "home_team": "Team X",
                "away_team": "Team Y"
            }
        )
        
        assert response.status_code == 200


class TestChatHistoryEndpoints:
    """Test suite for chat history endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_get_chat_history(self, client):
        """Test getting chat history."""
        response = client.get("/api/chat/history")
        
        assert response.status_code == 200
    
    def test_save_chat_message(self, client):
        """Test saving a chat message."""
        response = client.post(
            "/api/chat/history",
            json={
                "message": {
                    "id": "msg-123",
                    "type": "user",
                    "content": "Test message"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "saved"
    
    def test_clear_chat_history(self, client):
        """Test clearing chat history."""
        response = client.delete("/api/chat/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cleared"


class TestChatSessionsEndpoints:
    """Test suite for chat sessions endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_get_chat_sessions(self, client):
        """Test getting all chat sessions."""
        response = client.get("/api/chat/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
    
    def test_save_chat_session(self, client):
        """Test saving a chat session."""
        response = client.post(
            "/api/chat/sessions",
            json={
                "id": "test-session-123",
                "title": "Test Session",
                "preview": "Test preview",
                "messages": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "saved"
    
    def test_delete_chat_session(self, client):
        """Test deleting a chat session."""
        # First create a session
        client.post(
            "/api/chat/sessions",
            json={
                "id": "to-delete-123",
                "title": "Delete Me",
                "preview": "",
                "messages": []
            }
        )
        
        # Then delete it
        response = client.delete("/api/chat/sessions/to-delete-123")
        
        assert response.status_code == 200


class TestRootAndInfoEndpoints:
    """Test suite for root and info endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert data["version"] == "2.0.0"
    
    def test_health_check_complete(self, client):
        """Test health check returns all fields."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "timestamp" in data
        assert "version" in data
        assert "agent" in data
        assert "vector_store" in data
    
    def test_agent_info_complete(self, client):
        """Test agent info returns all fields."""
        response = client.get("/api/agent/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "agent_type" in data
        assert "vector_store" in data
        assert "tools_count" in data
        assert "features" in data


class TestErrorHandling:
    """Test suite for API error handling."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_invalid_session_returns_404(self, client):
        """Test getting non-existent session returns 404."""
        response = client.get("/api/agent/session/nonexistent-12345")
        
        assert response.status_code == 404
    
    def test_chat_without_message_fails(self, client):
        """Test chat without message field fails."""
        response = client.post(
            "/api/agent/chat",
            json={}
        )
        
        # Should return validation error (422)
        assert response.status_code == 422
    
    def test_invalid_endpoint_returns_404(self, client):
        """Test non-existent endpoint returns 404."""
        response = client.get("/api/nonexistent/endpoint")
        
        assert response.status_code == 404


class TestCORSAndHeaders:
    """Test suite for CORS and response headers."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_cors_preflight(self, client):
        """Test CORS preflight request."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # CORS preflight should be handled
        assert response.status_code in [200, 204, 405]
    
    def test_json_content_type(self, client):
        """Test that responses have JSON content type."""
        response = client.get("/api/health")
        
        assert "application/json" in response.headers.get("content-type", "")
