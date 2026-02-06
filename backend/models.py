"""
Data models for the Football Agent application.
Uses Pydantic for validation and serialization.
Focused on American Football (NFL, College, CFL, etc.)
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ActionStatus(str, Enum):
    """Status of an agent action."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class ToolType(str, Enum):
    """Types of server-side tools available."""
    FETCH_MATCHES = "fetch_matches"
    GET_TEAM_STATS = "get_team_stats"
    GET_LEAGUE_STANDINGS = "get_league_standings"
    SAVE_TO_FAVORITES = "save_to_favorites"
    SEARCH_PLAYERS = "search_players"
    GET_FOOTBALL_LEADERS = "get_football_leaders"
    GET_RANKINGS = "get_rankings"
    GET_INJURIES = "get_injuries"


class ClientActionType(str, Enum):
    """Types of client-side actions."""
    FILTER_RESULTS = "filter_results"
    SORT_RESULTS = "sort_results"
    EXPORT_DATA = "export_data"
    ADD_TO_WATCHLIST = "add_to_watchlist"
    UPDATE_CHART = "update_chart"


class FootballLeague(str, Enum):
    """Supported football leagues."""
    NFL = "nfl"
    COLLEGE_FOOTBALL = "college-football"
    CFL = "cfl"
    XFL = "xfl"
    USFL = "usfl"
    UFL = "ufl"


class FootballConference(str, Enum):
    """NFL and college football conferences."""
    # NFL
    AFC = "afc"
    NFC = "nfc"
    AFC_EAST = "afc_east"
    AFC_WEST = "afc_west"
    AFC_NORTH = "afc_north"
    AFC_SOUTH = "afc_south"
    NFC_EAST = "nfc_east"
    NFC_WEST = "nfc_west"
    NFC_NORTH = "nfc_north"
    NFC_SOUTH = "nfc_south"
    # College
    SEC = "sec"
    BIG_TEN = "big_ten"
    BIG_12 = "big_12"
    ACC = "acc"
    PAC_12 = "pac_12"


class Match(BaseModel):
    """Football game data model."""
    id: str
    home_team: str
    away_team: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str  # scheduled, live, finished
    kickoff_time: datetime
    league: str
    venue: Optional[str] = None


class FootballTeamInfo(BaseModel):
    """Detailed football team info in a game."""
    id: str = ""
    name: str = ""
    abbreviation: str = ""
    logo: str = ""
    color: str = ""
    score: Optional[int] = None
    record: str = ""
    rank: Optional[int] = None
    winner: bool = False


class Venue(BaseModel):
    """Venue/Stadium model."""
    name: str = ""
    city: str = ""
    state: str = ""


class GameOdds(BaseModel):
    """Game betting odds."""
    spread: str = ""
    over_under: str = ""


class FootballGame(BaseModel):
    """Detailed football game model with all stats."""
    id: str
    name: str = ""
    short_name: str = ""
    date: str = ""
    week: int = 0
    season_type: int = 2
    home_team: Dict[str, Any] = Field(default_factory=dict)
    away_team: Dict[str, Any] = Field(default_factory=dict)
    status: str = "scheduled"
    status_detail: str = ""
    period: int = 0
    clock: str = ""
    venue: Dict[str, Any] = Field(default_factory=dict)
    odds: Dict[str, Any] = Field(default_factory=dict)
    broadcasts: List[str] = Field(default_factory=list)
    attendance: int = 0
    neutral_site: bool = False
    conference_competition: bool = False


class TeamStats(BaseModel):
    """Team statistics model."""
    team_name: str
    played: int
    wins: int
    draws: int  # ties in football
    losses: int
    goals_for: int  # points_for in football
    goals_against: int  # points_against in football
    goal_difference: int  # point_differential in football
    points: int  # wins in football standings
    form: List[str] = Field(default_factory=list)  # W, L
    top_scorer: Optional[str] = None
    top_scorer_goals: Optional[int] = None


class LeagueStanding(BaseModel):
    """League standing entry."""
    position: int
    team: str
    played: int
    won: int
    drawn: int  # ties
    lost: int
    goals_for: int  # points_for
    goals_against: int  # points_against
    goal_difference: int  # point_differential
    points: int  # wins
    form: List[str] = Field(default_factory=list)


class Player(BaseModel):
    """Football player data model."""
    id: str
    name: str
    team: str
    position: str  # QB, RB, WR, TE, OL, DL, LB, DB, K, P
    nationality: str = ""
    age: int = 0
    goals: int = 0  # touchdowns
    assists: int = 0  # passing TDs for QB
    appearances: int = 0


class FootballPlayer(BaseModel):
    """Detailed football player model."""
    id: str
    name: str
    first_name: str = ""
    last_name: str = ""
    team: str = ""
    team_id: str = ""
    position: str = ""
    position_name: str = ""
    jersey: str = ""
    height: str = ""
    weight: str = ""
    age: int = 0
    experience: int = 0
    college: str = ""
    birthplace: str = ""
    headshot: str = ""
    status: str = "active"


class PlayerStats(BaseModel):
    """Football player statistics."""
    player_id: str
    player_name: str
    team: str
    position: str
    # Passing stats
    passing_yards: int = 0
    passing_tds: int = 0
    interceptions: int = 0
    completion_pct: float = 0.0
    passer_rating: float = 0.0
    # Rushing stats
    rushing_yards: int = 0
    rushing_tds: int = 0
    yards_per_carry: float = 0.0
    # Receiving stats
    receptions: int = 0
    receiving_yards: int = 0
    receiving_tds: int = 0
    # General
    games_played: int = 0


class AgentAction(BaseModel):
    """Represents a single action in the agent's plan."""
    id: str
    tool: str
    description: str
    status: ActionStatus = ActionStatus.PENDING
    requires_approval: bool = False
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AgentPlan(BaseModel):
    """The agent's execution plan."""
    goal: str
    steps: List[AgentAction]
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "created"  # created, executing, completed, failed


class ClientAction(BaseModel):
    """Client-side action to be executed in the browser."""
    type: ClientActionType
    target: str  # DOM element or component
    payload: Dict[str, Any]
    description: str


class KnowledgeItem(BaseModel):
    """Knowledge base item."""
    id: str
    type: str  # favorite_team, saved_game, note, search_history
    content: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)


class UserGoalRequest(BaseModel):
    """User's natural language goal request."""
    goal: str
    session_id: Optional[str] = None


class AgentResponse(BaseModel):
    """Response from the agent."""
    session_id: str
    plan: AgentPlan
    client_actions: List[ClientAction] = Field(default_factory=list)
    knowledge_used: List[KnowledgeItem] = Field(default_factory=list)
    message: str


class ApprovalRequest(BaseModel):
    """Request to approve/reject an action."""
    action_id: str
    approved: bool
    session_id: str
