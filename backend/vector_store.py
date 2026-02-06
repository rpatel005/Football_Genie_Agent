"""
Vector-based Knowledge Store using ChromaDB.
Provides semantic search capabilities for the football agent.
"""

import os
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

import chromadb
from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    """A document in the knowledge store."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str  # favorite_team, note, search_history, match_insight, player_fact
    content: str  # The main text content for embedding
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class VectorKnowledgeStore:
    """
    ChromaDB-powered knowledge store with semantic search.
    Stores user preferences, notes, and insights that the agent can retrieve.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector knowledge store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client with persistence (new API)
        # Use PersistentClient for persistence or EphemeralClient for in-memory
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
        except Exception:
            # Fallback to ephemeral client if persistence fails
            self.client = chromadb.EphemeralClient()
        
        # Create or get the main collection
        self.collection = self.client.get_or_create_collection(
            name="football_knowledge",
            metadata={"description": "Football agent knowledge base"}
        )
        
        # Clear any existing mock/fact data on startup
        self._clear_mock_data()
    
    def _clear_mock_data(self) -> None:
        """Clear any old mock/fact data from the collection."""
        try:
            # Get all documents with type 'fact' (old mock data)
            results = self.collection.get(where={"type": "fact"})
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Cleared {len(results['ids'])} old mock data entries from knowledge base")
        except Exception:
            pass  # Ignore errors when clearing
    
    def clear_all(self) -> None:
        """Clear all documents from the knowledge store."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection("football_knowledge")
            self.collection = self.client.create_collection(
                name="football_knowledge",
                metadata={"description": "Football agent knowledge base"}
            )
            print("Knowledge base cleared")
        except Exception as e:
            print(f"Error clearing knowledge base: {e}")
    
    def add(self, document: KnowledgeDocument) -> str:
        """
        Add a document to the knowledge store.
        
        Args:
            document: The document to add
            
        Returns:
            The document ID
        """
        # Prepare metadata - ChromaDB only accepts primitive types (str, int, float, bool)
        # Convert lists and dicts to JSON strings, filter out None values
        processed_metadata = {
            "type": document.type,
            "created_at": document.created_at,
        }
        for key, value in document.metadata.items():
            if value is None:
                continue  # Skip None values - ChromaDB doesn't support them
            elif isinstance(value, (list, dict)):
                processed_metadata[key] = json.dumps(value)
            else:
                processed_metadata[key] = value
        
        self.collection.add(
            ids=[document.id],
            documents=[document.content],
            metadatas=[processed_metadata]
        )
        return document.id
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant knowledge.
        
        Args:
            query: The search query
            n_results: Maximum number of results
            type_filter: Optional filter by document type
            
        Returns:
            List of matching documents with scores
        """
        where_filter = None
        if type_filter:
            where_filter = {"type": type_filter}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        documents = []
        if results and results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                doc = {
                    "id": doc_id,
                    "content": results['documents'][0][i] if results['documents'] else "",
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results.get('distances') else 0
                }
                documents.append(doc)
        
        return documents
    
    def get_by_type(self, doc_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get documents by type.
        
        Args:
            doc_type: The document type to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        results = self.collection.get(
            where={"type": doc_type},
            limit=limit
        )
        
        documents = []
        if results and results['ids']:
            for i, doc_id in enumerate(results['ids']):
                doc = {
                    "id": doc_id,
                    "content": results['documents'][i] if results['documents'] else "",
                    "metadata": results['metadatas'][i] if results['metadatas'] else {}
                }
                documents.append(doc)
        
        return documents
    
    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all documents."""
        results = self.collection.get(limit=limit)
        
        documents = []
        if results and results['ids']:
            for i, doc_id in enumerate(results['ids']):
                doc = {
                    "id": doc_id,
                    "content": results['documents'][i] if results['documents'] else "",
                    "metadata": results['metadatas'][i] if results['metadatas'] else {}
                }
                documents.append(doc)
        
        return documents
    
    def delete(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False
    
    def add_favorite_team(self, team_name: str) -> str:
        """Add a favorite team to knowledge."""
        doc = KnowledgeDocument(
            type="favorite_team",
            content=f"{team_name} is one of my favorite teams.",
            metadata={"team_name": team_name}
        )
        return self.add(doc)
    
    def add_note(self, note_text: str, tags: List[str] = None) -> str:
        """Add a user note."""
        doc = KnowledgeDocument(
            type="note",
            content=note_text,
            metadata={"tags": tags or []}
        )
        return self.add(doc)
    
    def add_search_history(self, query: str) -> str:
        """Add a search to history."""
        doc = KnowledgeDocument(
            type="search_history",
            content=f"User searched for: {query}",
            metadata={"query": query}
        )
        return self.add(doc)
    
    def get_favorite_teams(self) -> List[str]:
        """Get all favorite team names."""
        docs = self.get_by_type("favorite_team")
        return [doc["metadata"].get("team_name", "") for doc in docs if doc["metadata"].get("team_name")]
    
    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all documents from the collection.
        
        Args:
            limit: Maximum number of documents to return
            
        Returns:
            List of all documents
        """
        try:
            result = self.collection.get(limit=limit)
            
            if not result or not result['ids']:
                return []
            
            docs = []
            for i, doc_id in enumerate(result['ids']):
                docs.append({
                    "id": doc_id,
                    "content": result['documents'][i] if result['documents'] else "",
                    "metadata": result['metadatas'][i] if result['metadatas'] else {}
                })
            
            return docs
        except Exception:
            return []
    
    def get_search_history(self, limit: int = 10) -> List[str]:
        """
        Get recent search queries from history.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of search query strings
        """
        docs = self.get_by_type("search_history")
        queries = []
        for doc in docs[:limit]:
            query = doc.get("metadata", {}).get("query", "")
            if query:
                queries.append(query)
        return queries
    
    def get_relevant_context(self, query: str, n_results: int = 3) -> str:
        """
        Get relevant context for the LLM based on a query.
        
        Args:
            query: The user's query
            n_results: Number of results to include
            
        Returns:
            Formatted context string for the LLM
        """
        results = self.search(query, n_results=n_results)
        
        if not results:
            return "No relevant knowledge found in the database."
        
        context_parts = ["Relevant knowledge from the database:"]
        for i, doc in enumerate(results, 1):
            context_parts.append(f"{i}. {doc['content']}")
            if doc['metadata'].get('type') == 'favorite_team':
                context_parts.append(f"   (This is a user's favorite team)")
        
        return "\n".join(context_parts)

    # ============ Chat History Methods ============
    
    def add_chat_message(self, message: dict, session_id: str = None) -> str:
        """
        Add a chat message to history.
        
        Args:
            message: The chat message dict (id, type, content)
            session_id: Optional session ID
            
        Returns:
            The document ID
        """
        import json
        doc = KnowledgeDocument(
            id=f"chat-{message.get('id', datetime.now().timestamp())}",
            type="chat_message",
            content=message.get('content', ''),
            metadata={
                "message_id": message.get('id'),
                "message_type": message.get('type', 'user'),
                "session_id": session_id,
                "full_message": json.dumps(message)
            }
        )
        return self.add(doc)
    
    def get_chat_history(self, limit: int = 100) -> dict:
        """
        Get chat history messages.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            Dict with messages list and session_id
        """
        import json
        docs = self.get_by_type("chat_message", limit=limit)
        
        messages = []
        session_id = None
        
        # Sort by message_id to maintain order
        sorted_docs = sorted(docs, key=lambda x: x.get('metadata', {}).get('message_id', 0))
        
        for doc in sorted_docs:
            metadata = doc.get('metadata', {})
            try:
                full_message = json.loads(metadata.get('full_message', '{}'))
                if full_message:
                    messages.append(full_message)
                if metadata.get('session_id'):
                    session_id = metadata.get('session_id')
            except json.JSONDecodeError:
                # Fallback to reconstructing the message
                messages.append({
                    'id': metadata.get('message_id'),
                    'type': metadata.get('message_type', 'user'),
                    'content': doc.get('content', '')
                })
        
        return {
            "messages": messages,
            "session_id": session_id
        }
    
    def clear_chat_history(self) -> None:
        """Clear all chat history messages."""
        try:
            results = self.collection.get(where={"type": "chat_message"})
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Cleared {len(results['ids'])} chat messages")
        except Exception as e:
            print(f"Error clearing chat history: {e}")

    # ============ Chat Sessions Methods ============
    
    def save_chat_session(self, session: dict) -> str:
        """
        Save a chat session.
        
        Args:
            session: The session dict (id, title, preview, timestamp, messages)
            
        Returns:
            The document ID
        """
        import json
        session_id = session.get('id', str(uuid.uuid4())[:8])
        
        # Delete existing session with same ID (update)
        try:
            existing = self.collection.get(
                where={"$and": [{"type": "chat_session"}, {"session_id": session_id}]}
            )
            if existing and existing['ids']:
                self.collection.delete(ids=existing['ids'])
        except Exception:
            pass
        
        doc = KnowledgeDocument(
            id=f"session-{session_id}",
            type="chat_session",
            content=f"{session.get('title', '')} - {session.get('preview', '')}",
            metadata={
                "session_id": session_id,
                "title": session.get('title', ''),
                "preview": session.get('preview', ''),
                "timestamp": session.get('timestamp', datetime.now().strftime('%H:%M')),
                "messages_json": json.dumps(session.get('messages', []))
            }
        )
        return self.add(doc)
    
    def get_chat_sessions(self, limit: int = 10) -> List[dict]:
        """
        Get all chat sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session dicts
        """
        import json
        docs = self.get_by_type("chat_session", limit=limit)
        
        sessions = []
        for doc in docs:
            metadata = doc.get('metadata', {})
            try:
                messages = json.loads(metadata.get('messages_json', '[]'))
            except json.JSONDecodeError:
                messages = []
            
            sessions.append({
                'id': metadata.get('session_id', doc.get('id')),
                'title': metadata.get('title', 'Untitled'),
                'preview': metadata.get('preview', ''),
                'timestamp': metadata.get('timestamp', ''),
                'messages': messages
            })
        
        # Sort by timestamp (most recent first)
        sessions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return sessions
    
    def delete_chat_session(self, session_id: str) -> bool:
        """
        Delete a chat session.
        
        Args:
            session_id: The session ID to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            # Try to delete by session ID in metadata
            results = self.collection.get(
                where={"$and": [{"type": "chat_session"}, {"session_id": session_id}]}
            )
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Deleted session {session_id}")
                return True
            
            # Also try the document ID format
            doc_id = f"session-{session_id}"
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False


# Create singleton instance
vector_store = VectorKnowledgeStore()
