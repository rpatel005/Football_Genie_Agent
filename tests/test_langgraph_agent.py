"""
Tests for LangGraph Agent.
Tests the football analytics AI agent workflow.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

import sys
sys.path.insert(0, str(pytest.importorskip("pathlib").Path(__file__).parent.parent))

from backend.langgraph_agent import FootballAgentGraph, AgentState, SYSTEM_PROMPT


def run_async(coro):
    """Helper to run async code in sync tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


class TestFootballAgentGraphInit:
    """Test suite for FootballAgentGraph initialization."""
    
    def test_agent_creation(self):
        """Test that agent can be created."""
        agent = FootballAgentGraph()
        assert agent is not None
    
    def test_agent_has_model_name(self):
        """Test that agent has a model name."""
        agent = FootballAgentGraph()
        assert agent.model_name is not None
    
    def test_agent_has_sessions_dict(self):
        """Test that agent has a sessions dictionary."""
        agent = FootballAgentGraph()
        assert hasattr(agent, 'sessions')
        assert isinstance(agent.sessions, dict)
    
    def test_agent_has_memory(self):
        """Test that agent has memory (checkpointer)."""
        agent = FootballAgentGraph()
        assert hasattr(agent, 'memory')
    
    def test_agent_use_llm_flag(self):
        """Test that agent has use_llm flag."""
        agent = FootballAgentGraph()
        assert hasattr(agent, 'use_llm')
        assert isinstance(agent.use_llm, bool)


class TestAgentStateDefinition:
    """Test suite for AgentState TypedDict."""
    
    def test_agent_state_structure(self):
        """Test that AgentState has correct structure."""
        # AgentState is a TypedDict, check its keys
        expected_keys = [
            'messages',
            'session_id',
            'pending_approval',
            'plan',
            'current_step',
            'knowledge_context',
            'client_actions',
            'activity_steps'
        ]
        
        # Check TypedDict annotations
        assert hasattr(AgentState, '__annotations__')
        for key in expected_keys:
            assert key in AgentState.__annotations__


class TestSystemPrompt:
    """Test suite for system prompt."""
    
    def test_system_prompt_exists(self):
        """Test that system prompt exists."""
        assert SYSTEM_PROMPT is not None
        assert len(SYSTEM_PROMPT) > 0
    
    def test_system_prompt_has_placeholders(self):
        """Test that system prompt has required placeholders."""
        assert '{knowledge_context}' in SYSTEM_PROMPT
        assert '{current_date}' in SYSTEM_PROMPT
    
    def test_system_prompt_mentions_football(self):
        """Test that system prompt mentions football."""
        assert 'football' in SYSTEM_PROMPT.lower() or 'nfl' in SYSTEM_PROMPT.lower()
    
    def test_system_prompt_has_guidelines(self):
        """Test that system prompt has action guidelines."""
        assert 'calendar' in SYSTEM_PROMPT.lower()
        assert 'favorites' in SYSTEM_PROMPT.lower()


class TestProcessMessageAsync:
    """Test suite for process_message async method."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent instance for testing."""
        return FootballAgentGraph()
    
    def test_process_message_returns_dict(self, agent):
        """Test that process_message returns a dictionary."""
        result = run_async(agent.process_message("Hello"))
        
        assert isinstance(result, dict)
    
    def test_process_message_has_session_id(self, agent):
        """Test that process_message result has session_id."""
        result = run_async(agent.process_message("Hello"))
        
        assert 'session_id' in result
        assert result['session_id'] is not None
    
    def test_process_message_has_response(self, agent):
        """Test that process_message result has response."""
        result = run_async(agent.process_message("Hello"))
        
        assert 'response' in result
    
    def test_process_message_has_tool_results(self, agent):
        """Test that process_message result has tool_results."""
        result = run_async(agent.process_message("Hello"))
        
        assert 'tool_results' in result
        assert isinstance(result['tool_results'], list)
    
    def test_process_message_has_client_actions(self, agent):
        """Test that process_message result has client_actions."""
        result = run_async(agent.process_message("Hello"))
        
        assert 'client_actions' in result
        assert isinstance(result['client_actions'], list)
    
    def test_process_message_has_knowledge_used(self, agent):
        """Test that process_message result has knowledge_used."""
        result = run_async(agent.process_message("Hello"))
        
        assert 'knowledge_used' in result
        assert isinstance(result['knowledge_used'], list)
    
    def test_process_message_with_session_id(self, agent):
        """Test that process_message uses provided session_id."""
        result = run_async(agent.process_message("Hello", session_id="test-session-123"))
        
        assert result['session_id'] == "test-session-123"
    
    def test_process_message_generates_session_id(self, agent):
        """Test that process_message generates session_id when not provided."""
        result = run_async(agent.process_message("Hello"))
        
        assert result['session_id'] is not None
        assert len(result['session_id']) > 0


class TestGetSessionState:
    """Test suite for get_session_state method."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent instance for testing."""
        return FootballAgentGraph()
    
    def test_get_session_state_nonexistent(self, agent):
        """Test getting state for non-existent session."""
        result = agent.get_session_state("nonexistent-session-xyz")
        
        # Should return None or empty dict based on LLM availability
        assert result is None or isinstance(result, dict)
    
    def test_get_session_state_after_message(self, agent):
        """Test getting state after processing a message."""
        # First process a message
        message_result = run_async(agent.process_message("Hello", session_id="test-session"))
        
        # Then get state
        if agent.use_llm:
            state = agent.get_session_state("test-session")
            if state:
                assert 'session_id' in state


class TestApproveActionAsync:
    """Test suite for approve_action async method."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent instance for testing."""
        return FootballAgentGraph()
    
    def test_approve_action_returns_dict(self, agent):
        """Test that approve_action returns a dictionary."""
        result = run_async(agent.approve_action(
            session_id="test-session",
            tool_call_id="test-tool-call",
            approved=True
        ))
        
        assert isinstance(result, dict)
    
    def test_approve_action_has_session_id(self, agent):
        """Test that approve_action result has session_id."""
        result = run_async(agent.approve_action(
            session_id="test-session",
            tool_call_id="test-call",
            approved=False
        ))
        
        assert 'session_id' in result
    
    def test_approve_action_rejected(self, agent):
        """Test rejecting an action."""
        result = run_async(agent.approve_action(
            session_id="test-session",
            tool_call_id="test-call",
            approved=False
        ))
        
        assert 'response' in result
        # When rejected, approved should be False
        if 'approved' in result:
            assert result['approved'] is False


class TestAgentGraphWorkflow:
    """Test suite for agent graph workflow components."""
    
    @pytest.fixture
    def agent_with_llm(self):
        """Create an agent that might have LLM available."""
        agent = FootballAgentGraph()
        return agent
    
    def test_agent_has_graph_if_llm(self, agent_with_llm):
        """Test that agent has compiled graph if LLM is available."""
        if agent_with_llm.use_llm:
            assert hasattr(agent_with_llm, 'graph')
            assert hasattr(agent_with_llm, 'compiled_graph')
    
    def test_agent_has_llm_if_api_key(self, agent_with_llm):
        """Test that agent has LLM if API key is set."""
        if agent_with_llm.use_llm:
            assert hasattr(agent_with_llm, 'llm')
            assert hasattr(agent_with_llm, 'llm_with_tools')


class TestAgentFallback:
    """Test suite for agent fallback behavior when no LLM."""
    
    def test_fallback_returns_response(self):
        """Test that fallback processing returns a response."""
        agent = FootballAgentGraph()
        
        # Test with a simple message
        result = run_async(agent.process_message("Show me NFL games"))
        
        assert 'response' in result
        assert result['response'] is not None


class TestAgentWithVectorStore:
    """Test suite for agent integration with vector store."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent instance for testing."""
        return FootballAgentGraph()
    
    def test_message_stored_in_history(self, agent):
        """Test that messages are stored in search history."""
        # Process a unique message
        import uuid
        unique_query = f"Test query {uuid.uuid4()}"
        
        run_async(agent.process_message(unique_query))
        
        # Note: This tests that the call doesn't fail
        # Full verification would require checking the vector store


class TestAgentActivityTracking:
    """Test suite for agent activity step tracking."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent instance for testing."""
        return FootballAgentGraph()
    
    def test_activity_steps_in_response(self, agent):
        """Test that activity steps are returned in response."""
        result = run_async(agent.process_message("Hello"))
        
        # Activity steps should be present if LLM is available
        if agent.use_llm:
            assert 'activity_steps' in result


class TestAgentClientActions:
    """Test suite for client action generation."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent instance for testing."""
        return FootballAgentGraph()
    
    def test_generate_client_actions_method_exists(self, agent):
        """Test that _generate_client_actions method exists."""
        if agent.use_llm:
            assert hasattr(agent, '_generate_client_actions')


class TestAgentKnowledgeRetrieval:
    """Test suite for knowledge retrieval functionality."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent instance for testing."""
        return FootballAgentGraph()
    
    def test_retrieve_knowledge_method_exists(self, agent):
        """Test that _retrieve_knowledge method exists."""
        if agent.use_llm:
            assert hasattr(agent, '_retrieve_knowledge')


class TestAgentRoutingLogic:
    """Test suite for agent routing logic."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent instance for testing."""
        return FootballAgentGraph()
    
    def test_should_continue_method_exists(self, agent):
        """Test that _should_continue method exists."""
        if agent.use_llm:
            assert hasattr(agent, '_should_continue')
    
    def test_check_approval_method_exists(self, agent):
        """Test that _check_approval method exists."""
        if agent.use_llm:
            assert hasattr(agent, '_check_approval')


class TestAgentSingleton:
    """Test suite for agent singleton instance."""
    
    def test_singleton_instance_exists(self):
        """Test that singleton instance is created."""
        from backend.langgraph_agent import langgraph_agent
        
        assert langgraph_agent is not None
        assert isinstance(langgraph_agent, FootballAgentGraph)


class TestAgentMessageTypes:
    """Test suite for handling different message types."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent instance for testing."""
        return FootballAgentGraph()
    
    def test_greeting_message(self, agent):
        """Test handling greeting message."""
        result = run_async(agent.process_message("Hello!"))
        
        assert 'response' in result
        assert result['response'] is not None
    
    def test_football_query(self, agent):
        """Test handling football-related query."""
        result = run_async(agent.process_message("Show me NFL games today"))
        
        assert 'response' in result
        assert result['response'] is not None
    
    def test_team_stats_query(self, agent):
        """Test handling team stats query."""
        result = run_async(agent.process_message("What are the Chiefs' stats?"))
        
        assert 'response' in result
    
    def test_standings_query(self, agent):
        """Test handling standings query."""
        result = run_async(agent.process_message("Show me NFL standings"))
        
        assert 'response' in result


class TestAgentErrorHandling:
    """Test suite for agent error handling."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent instance for testing."""
        return FootballAgentGraph()
    
    def test_empty_message(self, agent):
        """Test handling empty message."""
        result = run_async(agent.process_message(""))
        
        assert 'response' in result
        # Should not crash
    
    def test_very_long_message(self, agent):
        """Test handling very long message."""
        long_message = "Tell me about NFL " * 100
        result = run_async(agent.process_message(long_message))
        
        assert 'response' in result
        # Should not crash
    
    def test_special_characters(self, agent):
        """Test handling message with special characters."""
        result = run_async(agent.process_message("What about @#$%^&* teams?"))
        
        assert 'response' in result
        # Should not crash
