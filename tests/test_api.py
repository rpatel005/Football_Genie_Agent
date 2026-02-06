"""
Integration tests for the API endpoints.
Tests the LangGraph-based agent endpoints.
"""

import pytest
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, str(pytest.importorskip("pathlib").Path(__file__).parent.parent))

from backend.server import app


class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    # ============ Health Check Tests ============
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "2.0.0"
        assert data["agent"] == "LangGraph"
        assert data["vector_store"] == "ChromaDB"
    
    # ============ Agent Info Tests ============
    
    def test_agent_info(self, client):
        """Test agent info endpoint."""
        response = client.get("/api/agent/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "LangGraph + LangChain"
        assert data["vector_store"] == "ChromaDB"
        assert "features" in data
    
    # ============ Chat Endpoint Tests ============
    
    def test_chat_endpoint(self, client):
        """Test the chat endpoint."""
        response = client.post(
            "/api/agent/chat",
            json={"message": "Hello"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "response" in data
        assert "tool_results" in data
        assert "client_actions" in data
        assert "knowledge_used" in data
    
    def test_chat_with_session(self, client):
        """Test chat with existing session."""
        # First request
        response1 = client.post(
            "/api/agent/chat",
            json={"message": "Hello"}
        )
        assert response1.status_code == 200
        session_id = response1.json()["session_id"]
        
        # Second request with same session
        response2 = client.post(
            "/api/agent/chat",
            json={"message": "How are you?", "session_id": session_id}
        )
        
        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id
    
    # ============ Legacy Goal Endpoint Tests ============
    
    def test_goal_endpoint(self, client):
        """Test the legacy goal endpoint redirects to chat."""
        response = client.post(
            "/api/agent/goal",
            json={"message": "Show matches"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "response" in data
    
    # ============ Session Endpoints ============
    
    def test_get_session_not_found(self, client):
        """Test getting non-existent session."""
        response = client.get("/api/agent/session/nonexistent-session-id")
        
        assert response.status_code == 404
    
    # ============ Knowledge Endpoints ============
    
    def test_get_knowledge(self, client):
        """Test getting knowledge items."""
        response = client.get("/api/knowledge")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "count" in data
    
    def test_search_knowledge(self, client):
        """Test semantic search in knowledge base."""
        response = client.get("/api/knowledge/search?query=Premier League")
        
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert "count" in data
    
    def test_add_knowledge(self, client):
        """Test adding knowledge item."""
        response = client.post(
            "/api/knowledge",
            json={
                "type": "note",
                "content": {"text": "Test note for API"},
                "tags": ["test", "api"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["type"] == "note"
        assert data["message"] == "Knowledge item added"
    
    def test_get_favorites(self, client):
        """Test getting favorite teams."""
        response = client.get("/api/knowledge/favorites")
        
        assert response.status_code == 200
        data = response.json()
        assert "favorite_teams" in data
    
    def test_get_search_history(self, client):
        """Test getting search history."""
        response = client.get("/api/knowledge/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
    
    def test_delete_knowledge_not_found(self, client):
        """Test deleting non-existent knowledge item."""
        response = client.delete("/api/knowledge/nonexistent-id")
        
        # ChromaDB may not fail on non-existent delete, just succeed silently
        assert response.status_code in [200, 404]
    
    # ============ Tools Endpoint Tests ============
    
    def test_get_tools(self, client):
        """Test getting available tools."""
        response = client.get("/api/tools")
        
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert "count" in data
        assert data["agent_type"] == "LangGraph"
        assert data["count"] >= 5  # Should have at least 5 tools


class TestVectorStore:
    """Test suite for vector store operations."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_knowledge_with_query(self, client):
        """Test knowledge retrieval with semantic query."""
        response = client.get("/api/knowledge?query=Manchester")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "search_query" in data
        assert data["search_query"] == "Manchester"
