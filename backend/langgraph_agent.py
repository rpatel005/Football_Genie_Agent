"""
LangGraph Agent for Football Analytics.
Uses LangGraph for stateful, multi-step agent workflows.
"""

import os
import re
import uuid
import logging
from datetime import datetime
from typing import Annotated, Sequence, TypedDict, Literal, Optional, List, Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('🏈 FootballAgent')

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from .langchain_tools import FOOTBALL_TOOLS, APPROVAL_REQUIRED_TOOLS
from .vector_store import vector_store

# Load environment variables
load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "TestProject"
os.environ["LANGSMITH_ENDPOINT"] = "https://eu.api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")


# ============ State Definition ============

class AgentState(TypedDict):
    """State for the football agent graph."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    session_id: str
    pending_approval: Optional[Dict[str, Any]]
    plan: List[str]
    current_step: int
    knowledge_context: str
    client_actions: List[Dict[str, Any]]
    activity_steps: List[Dict[str, Any]]  # Track agent activity


# ============ Agent Configuration ============

SYSTEM_PROMPT = """You are an expert American Football Analytics Agent. You help users get information about NFL, College Football, CFL, XFL, and USFL games, team statistics, league standings, and player data. You can also PERFORM ACTIONS on the user interface.
Analyze the user's request and determine if you need to call any tools to fetch data. If you call a tool that requires user approval (like adding to calendar or favorites), you MUST wait for the user's confirmation before executing it.
## UI Action Guidelines:
### Calendar Actions:
- When users ask to ADD a game to their calendar, use the add_match_to_calendar tool (this shows a confirmation first)
- When users CONFIRM/SAY YES to adding a game, use confirm_add_to_calendar tool with the same game details
- When users DECLINE/SAY NO to adding a game, acknowledge and don't add it
- When users ask to REMOVE a game from calendar, use remove_match_from_calendar tool (this shows a confirmation first)
- When users CONFIRM/SAY YES to removing a game, use confirm_remove_from_calendar tool with the same game details
- When users DECLINE/SAY NO to removing, acknowledge and don't remove it
- When users ask what's in their calendar, use get_calendar_matches tool

### Favorites Actions:
- When users ask to ADD a team to favorites, use add_team_to_favorites tool (this shows a confirmation first)
- When users CONFIRM/SAY YES to adding a team, use confirm_add_favorite_team tool with the same team name
- When users ask to REMOVE a team from favorites, use remove_team_from_favorites tool (this shows a confirmation first)  
- When users CONFIRM/SAY YES to removing a team, use confirm_remove_favorite_team tool with the same team name
- When users ask to ADD a player to favorites, use add_player_to_favorites tool (this shows a confirmation first)
- When users CONFIRM/SAY YES to adding a player, use confirm_add_favorite_player tool with the same player details
- When users ask to REMOVE a player from favorites, use remove_player_from_favorites tool (this shows a confirmation first)
- When users CONFIRM/SAY YES to removing a player, use confirm_remove_favorite_player tool with the same player name
- When users ask what teams/players are in their favorites, use get_favorite_teams or get_favorite_players tools

### Navigation Actions:
- When users ask to GO TO or SHOW a page, use navigate_to_page tool
- When users ask to FILTER by league, use set_league_filter tool
## Knowledge Context:
{knowledge_context}

## Current Date: {current_date}
"""


class FootballAgentGraph:
    """
    LangGraph-based Football Agent.
    Implements a stateful, multi-step agent with tool execution.
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the agent graph.
        
        Args:
            model_name: Model to use (auto-detected from env if not provided)
        """
        self.sessions: Dict[str, Any] = {}
        self.memory = MemorySaver()
        
        # Determine LLM provider based on available API keys
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if self.groq_api_key:
            self.llm_provider = "groq"
            self.api_key = self.groq_api_key
            self.model_name = model_name or os.getenv("GROQ_MODEL", "qwen/qwen3-32b")
            print(f"✅ Using Groq LLM with model: {self.model_name}")
        elif self.openai_api_key:
            self.llm_provider = "openai"
            self.api_key = self.openai_api_key
            self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o")
            print(f"✅ Using OpenAI LLM with model: {self.model_name}")
        else:
            self.llm_provider = None
            self.api_key = None
            self.model_name = None
        
        self.use_llm = bool(self.api_key)
        
        if self.use_llm:
            self._setup_llm_agent()
        else:
            print("⚠️ No LLM API key found. Please set GROQ_API_KEY or OPENAI_API_KEY in your .env file.")
    
    def _setup_llm_agent(self):
        """Set up the LLM-based agent with LangGraph."""
        # Initialize LLM based on provider
        if self.llm_provider == "groq":
            self.llm = ChatGroq(
                model=self.model_name,
                temperature=0,
                groq_api_key=self.api_key
            )
        elif self.llm_provider == "openai":
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0,
                api_key=self.api_key
            )
        self.llm_with_tools = self.llm.bind_tools(FOOTBALL_TOOLS)
        
        # Build the graph
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile(checkpointer=self.memory)
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("retrieve_knowledge", self._retrieve_knowledge)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolNode(FOOTBALL_TOOLS))
        workflow.add_node("check_approval", self._check_approval)
        workflow.add_node("generate_client_actions", self._generate_client_actions)
        
        # Set entry point
        workflow.set_entry_point("retrieve_knowledge")
        
        # Add edges
        workflow.add_edge("retrieve_knowledge", "agent")
        
        # Conditional edge from agent
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",
                "check_approval": "check_approval",
                "end": "generate_client_actions"
            }
        )
        
        workflow.add_edge("tools", "agent")
        workflow.add_edge("check_approval", "agent")
        workflow.add_edge("generate_client_actions", END)
        
        return workflow
    
    def _retrieve_knowledge(self, state: AgentState) -> Dict:
        """Retrieve relevant knowledge for the conversation."""
        messages = state.get("messages", [])
        
        # Get the latest user message
        user_message = ""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_message = msg.content
                break
        
        # Search for relevant knowledge
        knowledge_context = vector_store.get_relevant_context(user_message)
        
        # Also check for favorite teams
        favorites = vector_store.get_favorite_teams()
        if favorites:
            knowledge_context += f"\n\nUser's favorite teams: {', '.join(favorites)}"
        
        return {"knowledge_context": knowledge_context}
    
    def _agent_node(self, state: AgentState) -> Dict:
        """The main agent reasoning node."""
        messages = state.get("messages", [])
        knowledge_context = state.get("knowledge_context", "No relevant knowledge found.")
        
        # Create system message with context
        system_message = SystemMessage(content=SYSTEM_PROMPT.format(
            knowledge_context=knowledge_context,
            current_date=datetime.now().strftime("%Y-%m-%d")
        ))
        
        # Get response from LLM
        response = self.llm_with_tools.invoke([system_message] + list(messages))
        
        return {"messages": [response]}
    
    def _should_continue(self, state: AgentState) -> Literal["tools", "check_approval", "end"]:
        """Determine the next step based on agent output."""
        messages = state.get("messages", [])
        last_message = messages[-1]
        
        # Check if the agent wants to use tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            # Check if any tool requires approval
            for tool_call in last_message.tool_calls:
                if tool_call["name"] in APPROVAL_REQUIRED_TOOLS:
                    return "check_approval"
            return "tools"
        
        return "end"
    
    def _check_approval(self, state: AgentState) -> Dict:
        """Check if user approval is needed for a tool."""
        messages = state.get("messages", [])
        last_message = messages[-1]
        
        # Find the tool call that needs approval
        for tool_call in last_message.tool_calls:
            if tool_call["name"] in APPROVAL_REQUIRED_TOOLS:
                # Store pending approval info
                return {
                    "pending_approval": {
                        "tool_name": tool_call["name"],
                        "tool_args": tool_call["args"],
                        "tool_call_id": tool_call["id"]
                    }
                }
        
        return {}
    
    def _generate_client_actions(self, state: AgentState) -> Dict:
        """Generate client-side actions based on the conversation."""
        messages = state.get("messages", [])
        client_actions = []
        
        # Analyze what data was fetched to determine UI actions
        for msg in messages:
            if isinstance(msg, ToolMessage):
                if "matches" in msg.content.lower():
                    client_actions.append({
                        "type": "filter_results",
                        "target": "results-container",
                        "payload": {"filters": ["league", "team", "status"]}
                    })
                    client_actions.append({
                        "type": "add_to_watchlist",
                        "target": "match-cards",
                        "payload": {"enable": True}
                    })
                
                if "statistics" in msg.content.lower() or "stats" in msg.content.lower():
                    client_actions.append({
                        "type": "update_chart",
                        "target": "stats-chart",
                        "payload": {"chart_type": "bar"}
                    })
        
        # Always add export option if there are tool results
        tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
        if tool_messages:
            client_actions.append({
                "type": "export_data",
                "target": "export-button",
                "payload": {"formats": ["csv", "json"]}
            })
        
        return {"client_actions": client_actions}
    
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through the agent.
        
        Args:
            message: The user's message
            session_id: Optional session ID for conversation continuity
            
        Returns:
            Agent response with plan, results, and client actions
        """
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📨 NEW REQUEST | Session: {session_id}")
        logger.info(f"💬 User message: {message[:100]}{'...' if len(message) > 100 else ''}")
        
        # Store query in knowledge base
        vector_store.add_search_history(message)
        
        if self.use_llm:
            logger.info("🤖 Processing with LLM agent...")
            return await self._process_with_llm(message, session_id)
        else:
            logger.info("⚠️ Processing with fallback (no LLM)...")
            return await self._process_fallback(message, session_id)
    
    async def _process_with_llm(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process message using the LLM-based agent."""
        try:
            config = {"configurable": {"thread_id": session_id}}
            
            logger.info("🧠 Starting LLM processing pipeline...")
            
            # Track activity steps
            activity_steps = []
            
            # Initial state
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "session_id": session_id,
                "pending_approval": None,
                "plan": [],
                "current_step": 0,
                "knowledge_context": "",
                "client_actions": [],
                "activity_steps": []
            }
            
            # Add initial thinking step
            activity_steps.append({
                "step": "thinking",
                "status": "completed",
                "message": "🧠 Analyzing your request..."
            })
            
            # Add knowledge retrieval step
            activity_steps.append({
                "step": "knowledge",
                "status": "in_progress",
                "message": "📚 Searching knowledge base..."
            })
            
            # Run the graph
            result = await self.compiled_graph.ainvoke(initial_state, config)
            
            # Mark knowledge retrieval as completed
            for step in activity_steps:
                if step["step"] == "knowledge":
                    step["status"] = "completed"
                    step["message"] = "📚 Found relevant context"
            
            # Extract the response
            messages = result.get("messages", [])
            last_ai_message = None
            tool_results = []
            
            # Tool name to user-friendly description mapping
            tool_descriptions = {
                "get_matches": ("⚽ Fetching match data...", "⚽ Retrieved match information"),
                "fetch_matches": ("⚽ Fetching match data...", "⚽ Retrieved match information"),
                "get_team_stats": ("📊 Loading team statistics...", "📊 Got team stats"),
                "get_standings": ("🏆 Fetching league standings...", "🏆 Retrieved standings"),
                "get_league_standings": ("🏆 Fetching league standings...", "🏆 Retrieved standings"),
                "search_players": ("👤 Searching for players...", "👤 Found player info"),
                "search_knowledge": ("🔍 Searching knowledge base...", "🔍 Found relevant information"),
                "add_match_to_calendar": ("📅 Preparing calendar entry...", "📅 Ready to add to calendar"),
                "confirm_add_to_calendar": ("✅ Adding to calendar...", "✅ Added to calendar"),
                "remove_match_from_calendar": ("🗑️ Preparing to remove...", "🗑️ Ready to remove from calendar"),
                "confirm_remove_from_calendar": ("🗑️ Removing from calendar...", "🗑️ Removed from calendar"),
                "navigate_to_page": ("🧭 Navigating...", "🧭 Navigation ready"),
                "set_league_filter": ("🔧 Applying filter...", "🔧 Filter applied"),
                "get_calendar_matches": ("📆 Checking your calendar...", "📆 Retrieved calendar"),
                "save_favorite_team": ("⭐ Saving favorite...", "⭐ Team saved to favorites"),
                # Favorites tools
                "add_team_to_favorites": ("⭐ Preparing to favorite team...", "⭐ Ready to add team"),
                "confirm_add_favorite_team": ("✅ Adding team to favorites...", "✅ Team added to favorites"),
                "remove_team_from_favorites": ("🗑️ Preparing to remove team...", "🗑️ Ready to remove team"),
                "confirm_remove_favorite_team": ("🗑️ Removing team from favorites...", "🗑️ Team removed from favorites"),
                "add_player_to_favorites": ("⭐ Preparing to favorite player...", "⭐ Ready to add player"),
                "confirm_add_favorite_player": ("✅ Adding player to favorites...", "✅ Player added to favorites"),
                "remove_player_from_favorites": ("🗑️ Preparing to remove player...", "🗑️ Ready to remove player"),
                "confirm_remove_favorite_player": ("🗑️ Removing player from favorites...", "🗑️ Player removed from favorites"),
                "get_favorite_teams": ("⭐ Checking favorite teams...", "⭐ Retrieved favorite teams"),
                "get_favorite_players": ("⭐ Checking favorite players...", "⭐ Retrieved favorite players"),
            }
            
            for msg in messages:
                if isinstance(msg, AIMessage):
                    last_ai_message = msg
                    # Check if it called tools
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tool_name = tool_call['name']
                            logger.info(f"🔧 TOOL CALL: {tool_name}")
                            logger.info(f"   Args: {tool_call.get('args', {})}")
                            in_progress_msg, completed_msg = tool_descriptions.get(
                                tool_name, 
                                (f"🔄 Calling {tool_name.replace('_', ' ')}...", f"✓ Completed {tool_name.replace('_', ' ')}")
                            )
                            activity_steps.append({
                                "step": "tool_call",
                                "status": "in_progress",
                                "message": in_progress_msg,
                                "tool": tool_name
                            })
                elif isinstance(msg, ToolMessage):
                    logger.info(f"\u2705 TOOL RESULT: {msg.name}")
                    logger.info(f"   Output length: {len(msg.content)} chars")
                    tool_results.append({
                        "tool": msg.name,
                        "content": msg.content
                    })
                    # Update tool step to completed with better message
                    for step in activity_steps:
                        if step.get("tool") == msg.name and step["status"] == "in_progress":
                            step["status"] = "completed"
                            _, completed_msg = tool_descriptions.get(
                                msg.name,
                                (None, f"✓ {msg.name.replace('_', ' ')} completed")
                            )
                            step["message"] = completed_msg
            
            # Add final response generation step
            activity_steps.append({
                "step": "responding",
                "status": "completed",
                "message": "💬 Generating response..."
            })
            
            # Build response
            response_text = last_ai_message.content if last_ai_message else "I couldn't process that request."
            
            # Extract action markers from tool results and append to response
            # This ensures frontend can parse actions from tool outputs
            action_pattern = r'\[ACTION:\w+\][\s\S]*?\{[\s\S]*?\}[\s\S]*?\[/ACTION\]'
            for tr in tool_results:
                if tr.get("content"):
                    action_matches = re.findall(action_pattern, tr["content"])
                    for action in action_matches:
                        # Only append if not already in response
                        if action not in response_text:
                            response_text += "\n\n" + action
            
            # Get knowledge that was used
            knowledge_used = []
            knowledge_results = vector_store.search(message, n_results=2)
            for k in knowledge_results:
                knowledge_used.append({
                    "id": k["id"],
                    "type": k["metadata"].get("type", "unknown"),
                    "content": k["content"][:100]
                })
            
            return {
                "session_id": session_id,
                "response": response_text,
                "tool_results": tool_results,
                "pending_approval": result.get("pending_approval"),
                "client_actions": result.get("client_actions", []),
                "knowledge_used": knowledge_used,
                "activity_steps": activity_steps
            }
        except Exception as e:
            # If LLM fails (e.g., invalid API key), return error message
            logger.error(f"❌ LLM processing failed: {e}")
            return {
                "session_id": session_id,
                "response": f"I encountered an error processing your request. Please ensure your LLM API key is valid. Error: {str(e)[:100]}",
                "tool_results": [],
                "pending_approval": None,
                "client_actions": [],
                "knowledge_used": [],
                "activity_steps": [{"step": "error", "status": "failed", "message": "Request failed"}]
            }
    
    async def approve_action(
        self,
        session_id: str,
        tool_call_id: str,
        approved: bool
    ) -> Dict[str, Any]:
        """
        Handle approval/rejection of a pending action.
        
        Args:
            session_id: The session ID
            tool_call_id: The tool call ID to approve/reject
            approved: Whether the action is approved
            
        Returns:
            Updated response after executing or rejecting the action
        """
        if not self.use_llm:
            return {
                "session_id": session_id,
                "response": "Cannot approve actions without a valid LLM API key.",
                "approved": False,
                "tool_results": [],
                "pending_approval": None,
                "client_actions": [],
                "knowledge_used": []
            }
        
        config = {"configurable": {"thread_id": session_id}}
        
        if approved:
            # Execute the pending tool
            state = self.compiled_graph.get_state(config)
            pending = state.values.get("pending_approval")
            
            if pending:
                tool_name = pending["tool_name"]
                tool_args = pending["tool_args"]
                
                # Find and execute the tool
                for tool in FOOTBALL_TOOLS:
                    if tool.name == tool_name:
                        result = tool.invoke(tool_args)
                        
                        tool_message = ToolMessage(
                            content=result,
                            tool_call_id=pending["tool_call_id"],
                            name=tool_name
                        )
                        
                        updated_state = await self.compiled_graph.ainvoke(
                            {"messages": [tool_message], "pending_approval": None},
                            config
                        )
                        
                        # Extract action markers from tool result
                        response_text = updated_state["messages"][-1].content if updated_state["messages"] else "Action approved."
                        action_pattern = r'\[ACTION:\w+\][\s\S]*?\{[\s\S]*?\}[\s\S]*?\[/ACTION\]'
                        action_matches = re.findall(action_pattern, result)
                        for action in action_matches:
                            if action not in response_text:
                                response_text += "\n\n" + action
                        
                        return {
                            "session_id": session_id,
                            "response": response_text,
                            "approved": True,
                            "tool_results": [{"tool": tool_name, "content": result}],
                            "pending_approval": None,
                            "client_actions": [],
                            "knowledge_used": []
                        }
        
        return {
            "session_id": session_id,
            "response": "Action was rejected by user.",
            "approved": False,
            "tool_results": [],
            "pending_approval": None,
            "client_actions": [],
            "knowledge_used": []
        }
    
    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a session.
        
        Args:
            session_id: The session ID to look up
            
        Returns:
            Session state dict or None if not found
        """
        if not self.use_llm:
            return None
        
        try:
            config = {"configurable": {"thread_id": session_id}}
            state = self.compiled_graph.get_state(config)
            
            if state and state.values:
                messages = state.values.get("messages", [])
                return {
                    "session_id": session_id,
                    "message_count": len(messages),
                    "pending_approval": state.values.get("pending_approval"),
                    "knowledge_context": state.values.get("knowledge_context", ""),
                    "client_actions": state.values.get("client_actions", [])
                }
        except Exception:
            pass
        
        return None


# Create singleton instance
langgraph_agent = FootballAgentGraph()
