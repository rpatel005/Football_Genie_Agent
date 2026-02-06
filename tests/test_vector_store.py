"""
Tests for Vector Store (ChromaDB) functionality.
"""

import pytest
import tempfile
import uuid
from datetime import datetime

import sys
sys.path.insert(0, str(pytest.importorskip("pathlib").Path(__file__).parent.parent))

from backend.vector_store import VectorKnowledgeStore, KnowledgeDocument


class TestKnowledgeDocument:
    """Test suite for KnowledgeDocument model."""
    
    def test_document_creation_with_defaults(self):
        """Test creating a document with default values."""
        doc = KnowledgeDocument(
            type="note",
            content="Test content"
        )
        
        assert doc.id is not None
        assert doc.type == "note"
        assert doc.content == "Test content"
        assert doc.metadata == {}
        assert doc.created_at is not None
    
    def test_document_creation_with_custom_values(self):
        """Test creating a document with custom values."""
        doc = KnowledgeDocument(
            id="custom-id",
            type="favorite_team",
            content="Manchester City is my favorite",
            metadata={"team_name": "Manchester City"},
            created_at="2024-01-01T00:00:00"
        )
        
        assert doc.id == "custom-id"
        assert doc.type == "favorite_team"
        assert doc.metadata["team_name"] == "Manchester City"
    
    def test_document_id_is_unique(self):
        """Test that document IDs are unique."""
        doc1 = KnowledgeDocument(type="note", content="Note 1")
        doc2 = KnowledgeDocument(type="note", content="Note 2")
        
        assert doc1.id != doc2.id


class TestVectorKnowledgeStore:
    """Test suite for VectorKnowledgeStore."""
    
    @pytest.fixture
    def store(self):
        """Create a temporary vector store for each test."""
        # Use ignore_cleanup_errors=True to handle Windows file locks from ChromaDB
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            store = VectorKnowledgeStore(persist_directory=tmpdir)
            yield store
    
    # ============ Add Document Tests ============
    
    def test_add_document(self, store):
        """Test adding a document to the store."""
        doc = KnowledgeDocument(
            type="note",
            content="This is a test note"
        )
        
        doc_id = store.add(doc)
        
        assert doc_id == doc.id
    
    def test_add_multiple_documents(self, store):
        """Test adding multiple documents."""
        doc1 = KnowledgeDocument(type="note", content="Note 1")
        doc2 = KnowledgeDocument(type="note", content="Note 2")
        doc3 = KnowledgeDocument(type="favorite_team", content="Team 1")
        
        id1 = store.add(doc1)
        id2 = store.add(doc2)
        id3 = store.add(doc3)
        
        assert id1 != id2 != id3
    
    # ============ Search Tests ============
    
    def test_search_documents(self, store):
        """Test searching documents."""
        doc1 = KnowledgeDocument(type="note", content="Football is great")
        doc2 = KnowledgeDocument(type="note", content="Basketball is fun")
        doc3 = KnowledgeDocument(type="note", content="NFL games are exciting")
        
        store.add(doc1)
        store.add(doc2)
        store.add(doc3)
        
        results = store.search("football NFL", n_results=2)
        
        assert len(results) <= 2
    
    def test_search_with_type_filter(self, store):
        """Test searching with type filter."""
        doc1 = KnowledgeDocument(type="note", content="Test note about sports")
        doc2 = KnowledgeDocument(type="favorite_team", content="Favorite sports team")
        
        store.add(doc1)
        store.add(doc2)
        
        results = store.search("sports", type_filter="note")
        
        for result in results:
            assert result["metadata"]["type"] == "note"
    
    def test_search_empty_store(self, store):
        """Test searching an empty store."""
        results = store.search("test query")
        
        assert results == []
    
    # ============ Get By Type Tests ============
    
    def test_get_by_type(self, store):
        """Test getting documents by type."""
        doc1 = KnowledgeDocument(type="note", content="Note 1")
        doc2 = KnowledgeDocument(type="favorite_team", content="Team 1")
        doc3 = KnowledgeDocument(type="note", content="Note 2")
        
        store.add(doc1)
        store.add(doc2)
        store.add(doc3)
        
        notes = store.get_by_type("note")
        
        assert len(notes) == 2
        for note in notes:
            assert note["metadata"]["type"] == "note"
    
    def test_get_by_type_empty(self, store):
        """Test getting documents by type when none exist."""
        results = store.get_by_type("nonexistent_type")
        
        assert results == []
    
    # ============ Get All Tests ============
    
    def test_get_all(self, store):
        """Test getting all documents."""
        doc1 = KnowledgeDocument(type="note", content="Note 1")
        doc2 = KnowledgeDocument(type="note", content="Note 2")
        
        store.add(doc1)
        store.add(doc2)
        
        all_docs = store.get_all()
        
        assert len(all_docs) == 2
    
    def test_get_all_with_limit(self, store):
        """Test getting all documents with a limit."""
        for i in range(10):
            doc = KnowledgeDocument(type="note", content=f"Note {i}")
            store.add(doc)
        
        limited = store.get_all(limit=5)
        
        assert len(limited) == 5
    
    # ============ Delete Tests ============
    
    def test_delete_document(self, store):
        """Test deleting a document."""
        doc = KnowledgeDocument(type="note", content="To be deleted")
        doc_id = store.add(doc)
        
        result = store.delete(doc_id)
        
        assert result is True
    
    def test_delete_nonexistent_document(self, store):
        """Test deleting a document that doesn't exist."""
        # ChromaDB may not fail on non-existent delete
        result = store.delete("nonexistent-id")
        # Just check it doesn't crash
        assert result in [True, False]
    
    # ============ Favorite Team Tests ============
    
    def test_add_favorite_team(self, store):
        """Test adding a favorite team."""
        team_id = store.add_favorite_team("Manchester City")
        
        assert team_id is not None
        
        favorites = store.get_favorite_teams()
        assert "Manchester City" in favorites
    
    def test_get_favorite_teams(self, store):
        """Test getting favorite teams."""
        store.add_favorite_team("Arsenal")
        store.add_favorite_team("Chelsea")
        
        favorites = store.get_favorite_teams()
        
        assert "Arsenal" in favorites
        assert "Chelsea" in favorites
    
    def test_get_favorite_teams_empty(self, store):
        """Test getting favorite teams when none exist."""
        favorites = store.get_favorite_teams()
        
        assert favorites == []
    
    # ============ Note Tests ============
    
    def test_add_note(self, store):
        """Test adding a note."""
        note_id = store.add_note("This is my note", tags=["sports", "nfl"])
        
        assert note_id is not None
        
        notes = store.get_by_type("note")
        assert len(notes) == 1
    
    def test_add_note_without_tags(self, store):
        """Test adding a note without tags."""
        note_id = store.add_note("Simple note")
        
        assert note_id is not None
    
    # ============ Search History Tests ============
    
    def test_add_search_history(self, store):
        """Test adding to search history."""
        store.add_search_history("NFL scores")
        store.add_search_history("Premier League standings")
        
        history = store.get_search_history()
        
        assert len(history) == 2
        assert "NFL scores" in history
        assert "Premier League standings" in history
    
    def test_get_search_history_limit(self, store):
        """Test getting search history with limit."""
        for i in range(15):
            store.add_search_history(f"Search {i}")
        
        history = store.get_search_history(limit=5)
        
        assert len(history) <= 5
    
    # ============ Relevant Context Tests ============
    
    def test_get_relevant_context(self, store):
        """Test getting relevant context for LLM."""
        store.add_favorite_team("Kansas City Chiefs")
        store.add_note("The Chiefs won the Super Bowl")
        
        context = store.get_relevant_context("Chiefs")
        
        assert "Kansas City Chiefs" in context or "Chiefs" in context
    
    def test_get_relevant_context_empty(self, store):
        """Test getting context when store is empty."""
        context = store.get_relevant_context("random query")
        
        assert "No relevant knowledge" in context
    
    # ============ Chat History Tests ============
    
    def test_add_chat_message(self, store):
        """Test adding a chat message."""
        message = {
            "id": "msg-1",
            "type": "user",
            "content": "What are today's NFL games?"
        }
        
        doc_id = store.add_chat_message(message, session_id="session-1")
        
        assert doc_id is not None
    
    def test_get_chat_history(self, store):
        """Test getting chat history."""
        message1 = {"id": "1", "type": "user", "content": "Hello"}
        message2 = {"id": "2", "type": "assistant", "content": "Hi there!"}
        
        store.add_chat_message(message1, session_id="session-1")
        store.add_chat_message(message2, session_id="session-1")
        
        history = store.get_chat_history()
        
        assert "messages" in history
        assert len(history["messages"]) >= 2
    
    def test_clear_chat_history(self, store):
        """Test clearing chat history."""
        # Use message dict with no None values
        message = {"id": "1", "type": "user", "content": "Test", "timestamp": "2024-01-01"}
        store.add_chat_message(message)
        
        store.clear_chat_history()
        
        history = store.get_chat_history()
        assert len(history["messages"]) == 0
    
    # ============ Clear All Tests ============
    
    def test_clear_all(self, store):
        """Test clearing all documents."""
        store.add_favorite_team("Team 1")
        store.add_note("Note 1")
        
        store.clear_all()
        
        all_docs = store.get_all()
        assert len(all_docs) == 0


class TestChatSessions:
    """Test suite for chat session functionality."""
    
    @pytest.fixture
    def store(self):
        """Create a temporary vector store for each test."""
        # Use ignore_cleanup_errors=True to handle Windows file locks from ChromaDB
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            store = VectorKnowledgeStore(persist_directory=tmpdir)
            yield store
    
    def test_save_chat_session(self, store):
        """Test saving a chat session."""
        session = {
            "id": "session-123",
            "title": "NFL Discussion",
            "preview": "Talking about games",
            "timestamp": datetime.now().isoformat(),
            "messages": [
                {"id": "1", "type": "user", "content": "Hello"}
            ]
        }
        
        session_id = store.save_chat_session(session)
        
        assert session_id is not None
    
    def test_get_chat_sessions(self, store):
        """Test getting all chat sessions."""
        session1 = {"id": "s1", "title": "Session 1", "preview": "Preview 1", "messages": []}
        session2 = {"id": "s2", "title": "Session 2", "preview": "Preview 2", "messages": []}
        
        store.save_chat_session(session1)
        store.save_chat_session(session2)
        
        sessions = store.get_chat_sessions()
        
        assert len(sessions) >= 2
    
    def test_delete_chat_session(self, store):
        """Test deleting a chat session."""
        session = {"id": "to-delete", "title": "Delete Me", "preview": "", "messages": []}
        store.save_chat_session(session)
        
        store.delete_chat_session("to-delete")
        
        sessions = store.get_chat_sessions()
        session_ids = [s.get("session_id") or s.get("id") for s in sessions]
        # Session should be deleted
        assert "to-delete" not in session_ids or len(sessions) == 0
