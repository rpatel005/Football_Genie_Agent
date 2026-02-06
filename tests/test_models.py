"""
Tests for Data Models.
Tests Pydantic models and enums for the football agent application.
"""

import pytest
from datetime import datetime
from typing import Optional

import sys
sys.path.insert(0, str(pytest.importorskip("pathlib").Path(__file__).parent.parent))

from backend.models import (
    # Enums
    ActionStatus,
    ToolType,
    ClientActionType,
    FootballLeague,
    FootballConference,
    # Models
    Match,
    FootballTeamInfo,
    Venue,
    GameOdds,
    FootballGame,
    TeamStats,
    LeagueStanding,
    Player,
    FootballPlayer,
    PlayerStats,
    AgentAction,
    AgentPlan,
    ClientAction,
    KnowledgeItem,
    UserGoalRequest,
    AgentResponse,
    ApprovalRequest,
)


class TestActionStatusEnum:
    """Test suite for ActionStatus enum."""
    
    def test_pending_status(self):
        """Test PENDING status."""
        assert ActionStatus.PENDING == "pending"
    
    def test_running_status(self):
        """Test RUNNING status."""
        assert ActionStatus.RUNNING == "running"
    
    def test_completed_status(self):
        """Test COMPLETED status."""
        assert ActionStatus.COMPLETED == "completed"
    
    def test_failed_status(self):
        """Test FAILED status."""
        assert ActionStatus.FAILED == "failed"
    
    def test_awaiting_approval_status(self):
        """Test AWAITING_APPROVAL status."""
        assert ActionStatus.AWAITING_APPROVAL == "awaiting_approval"
    
    def test_approved_status(self):
        """Test APPROVED status."""
        assert ActionStatus.APPROVED == "approved"
    
    def test_rejected_status(self):
        """Test REJECTED status."""
        assert ActionStatus.REJECTED == "rejected"


class TestToolTypeEnum:
    """Test suite for ToolType enum."""
    
    def test_fetch_matches(self):
        """Test FETCH_MATCHES tool type."""
        assert ToolType.FETCH_MATCHES == "fetch_matches"
    
    def test_get_team_stats(self):
        """Test GET_TEAM_STATS tool type."""
        assert ToolType.GET_TEAM_STATS == "get_team_stats"
    
    def test_get_league_standings(self):
        """Test GET_LEAGUE_STANDINGS tool type."""
        assert ToolType.GET_LEAGUE_STANDINGS == "get_league_standings"
    
    def test_save_to_favorites(self):
        """Test SAVE_TO_FAVORITES tool type."""
        assert ToolType.SAVE_TO_FAVORITES == "save_to_favorites"
    
    def test_search_players(self):
        """Test SEARCH_PLAYERS tool type."""
        assert ToolType.SEARCH_PLAYERS == "search_players"


class TestClientActionTypeEnum:
    """Test suite for ClientActionType enum."""
    
    def test_filter_results(self):
        """Test FILTER_RESULTS action type."""
        assert ClientActionType.FILTER_RESULTS == "filter_results"
    
    def test_sort_results(self):
        """Test SORT_RESULTS action type."""
        assert ClientActionType.SORT_RESULTS == "sort_results"
    
    def test_export_data(self):
        """Test EXPORT_DATA action type."""
        assert ClientActionType.EXPORT_DATA == "export_data"
    
    def test_add_to_watchlist(self):
        """Test ADD_TO_WATCHLIST action type."""
        assert ClientActionType.ADD_TO_WATCHLIST == "add_to_watchlist"
    
    def test_update_chart(self):
        """Test UPDATE_CHART action type."""
        assert ClientActionType.UPDATE_CHART == "update_chart"


class TestFootballLeagueEnum:
    """Test suite for FootballLeague enum."""
    
    def test_nfl(self):
        """Test NFL league."""
        assert FootballLeague.NFL == "nfl"
    
    def test_college_football(self):
        """Test college football league."""
        assert FootballLeague.COLLEGE_FOOTBALL == "college-football"
    
    def test_cfl(self):
        """Test CFL league."""
        assert FootballLeague.CFL == "cfl"
    
    def test_xfl(self):
        """Test XFL league."""
        assert FootballLeague.XFL == "xfl"
    
    def test_usfl(self):
        """Test USFL league."""
        assert FootballLeague.USFL == "usfl"


class TestFootballConferenceEnum:
    """Test suite for FootballConference enum."""
    
    def test_afc(self):
        """Test AFC conference."""
        assert FootballConference.AFC == "afc"
    
    def test_nfc(self):
        """Test NFC conference."""
        assert FootballConference.NFC == "nfc"
    
    def test_sec(self):
        """Test SEC conference."""
        assert FootballConference.SEC == "sec"
    
    def test_big_ten(self):
        """Test Big Ten conference."""
        assert FootballConference.BIG_TEN == "big_ten"


class TestMatchModel:
    """Test suite for Match model."""
    
    def test_match_creation(self):
        """Test creating a Match."""
        match = Match(
            id="match-123",
            home_team="Kansas City Chiefs",
            away_team="Buffalo Bills",
            status="scheduled",
            kickoff_time=datetime.now(),
            league="NFL"
        )
        
        assert match.id == "match-123"
        assert match.home_team == "Kansas City Chiefs"
        assert match.away_team == "Buffalo Bills"
        assert match.status == "scheduled"
        assert match.league == "NFL"
    
    def test_match_with_scores(self):
        """Test Match with scores."""
        match = Match(
            id="match-456",
            home_team="Chiefs",
            away_team="Broncos",
            home_score=27,
            away_score=17,
            status="finished",
            kickoff_time=datetime.now(),
            league="NFL"
        )
        
        assert match.home_score == 27
        assert match.away_score == 17
    
    def test_match_with_venue(self):
        """Test Match with venue."""
        match = Match(
            id="match-789",
            home_team="Chiefs",
            away_team="Raiders",
            status="scheduled",
            kickoff_time=datetime.now(),
            league="NFL",
            venue="GEHA Field at Arrowhead Stadium"
        )
        
        assert match.venue == "GEHA Field at Arrowhead Stadium"


class TestFootballTeamInfoModel:
    """Test suite for FootballTeamInfo model."""
    
    def test_team_info_creation(self):
        """Test creating FootballTeamInfo."""
        team = FootballTeamInfo(
            id="team-1",
            name="Kansas City Chiefs",
            abbreviation="KC",
            logo="https://example.com/logo.png",
            color="#E31837"
        )
        
        assert team.id == "team-1"
        assert team.name == "Kansas City Chiefs"
        assert team.abbreviation == "KC"
    
    def test_team_info_defaults(self):
        """Test FootballTeamInfo default values."""
        team = FootballTeamInfo()
        
        assert team.id == ""
        assert team.name == ""
        assert team.score is None
        assert team.winner is False


class TestVenueModel:
    """Test suite for Venue model."""
    
    def test_venue_creation(self):
        """Test creating Venue."""
        venue = Venue(
            name="Arrowhead Stadium",
            city="Kansas City",
            state="Missouri"
        )
        
        assert venue.name == "Arrowhead Stadium"
        assert venue.city == "Kansas City"
        assert venue.state == "Missouri"
    
    def test_venue_defaults(self):
        """Test Venue default values."""
        venue = Venue()
        
        assert venue.name == ""
        assert venue.city == ""
        assert venue.state == ""


class TestGameOddsModel:
    """Test suite for GameOdds model."""
    
    def test_game_odds_creation(self):
        """Test creating GameOdds."""
        odds = GameOdds(
            spread="-3.5",
            over_under="44.5"
        )
        
        assert odds.spread == "-3.5"
        assert odds.over_under == "44.5"
    
    def test_game_odds_defaults(self):
        """Test GameOdds default values."""
        odds = GameOdds()
        
        assert odds.spread == ""
        assert odds.over_under == ""


class TestFootballGameModel:
    """Test suite for FootballGame model."""
    
    def test_football_game_creation(self):
        """Test creating FootballGame."""
        game = FootballGame(
            id="game-123",
            name="Kansas City Chiefs at Buffalo Bills",
            short_name="KC @ BUF",
            date="2024-12-25"
        )
        
        assert game.id == "game-123"
        assert game.name == "Kansas City Chiefs at Buffalo Bills"
    
    def test_football_game_defaults(self):
        """Test FootballGame default values."""
        game = FootballGame(id="test-123")
        
        assert game.week == 0
        assert game.season_type == 2
        assert game.status == "scheduled"
        assert game.period == 0
        assert game.neutral_site is False


class TestTeamStatsModel:
    """Test suite for TeamStats model."""
    
    def test_team_stats_creation(self):
        """Test creating TeamStats."""
        stats = TeamStats(
            team_name="Kansas City Chiefs",
            played=16,
            wins=12,
            draws=0,
            losses=4,
            goals_for=350,
            goals_against=280,
            goal_difference=70,
            points=12
        )
        
        assert stats.team_name == "Kansas City Chiefs"
        assert stats.played == 16
        assert stats.wins == 12
        assert stats.losses == 4
    
    def test_team_stats_with_form(self):
        """Test TeamStats with form."""
        stats = TeamStats(
            team_name="Chiefs",
            played=5,
            wins=3,
            draws=0,
            losses=2,
            goals_for=100,
            goals_against=80,
            goal_difference=20,
            points=3,
            form=["W", "W", "L", "W", "L"]
        )
        
        assert len(stats.form) == 5
        assert stats.form[0] == "W"


class TestLeagueStandingModel:
    """Test suite for LeagueStanding model."""
    
    def test_standing_creation(self):
        """Test creating LeagueStanding."""
        standing = LeagueStanding(
            position=1,
            team="Kansas City Chiefs",
            played=16,
            won=12,
            drawn=0,
            lost=4,
            goals_for=350,
            goals_against=280,
            goal_difference=70,
            points=12
        )
        
        assert standing.position == 1
        assert standing.team == "Kansas City Chiefs"
        assert standing.won == 12


class TestPlayerModel:
    """Test suite for Player model."""
    
    def test_player_creation(self):
        """Test creating Player."""
        player = Player(
            id="player-1",
            name="Patrick Mahomes",
            team="Kansas City Chiefs",
            position="QB"
        )
        
        assert player.id == "player-1"
        assert player.name == "Patrick Mahomes"
        assert player.position == "QB"
    
    def test_player_with_stats(self):
        """Test Player with statistics."""
        player = Player(
            id="player-2",
            name="Travis Kelce",
            team="Chiefs",
            position="TE",
            goals=8,
            assists=0,
            appearances=16
        )
        
        assert player.goals == 8
        assert player.appearances == 16


class TestFootballPlayerModel:
    """Test suite for FootballPlayer model."""
    
    def test_football_player_creation(self):
        """Test creating FootballPlayer."""
        player = FootballPlayer(
            id="fp-123",
            name="Patrick Mahomes",
            first_name="Patrick",
            last_name="Mahomes",
            team="Kansas City Chiefs",
            position="QB",
            jersey="15"
        )
        
        assert player.id == "fp-123"
        assert player.name == "Patrick Mahomes"
        assert player.jersey == "15"
    
    def test_football_player_defaults(self):
        """Test FootballPlayer default values."""
        player = FootballPlayer(id="test", name="Test Player")
        
        assert player.team == ""
        assert player.age == 0
        assert player.status == "active"


class TestPlayerStatsModel:
    """Test suite for PlayerStats model."""
    
    def test_player_stats_creation(self):
        """Test creating PlayerStats."""
        stats = PlayerStats(
            player_id="ps-1",
            player_name="Patrick Mahomes",
            team="Chiefs",
            position="QB",
            passing_yards=4500,
            passing_tds=35,
            interceptions=10
        )
        
        assert stats.player_name == "Patrick Mahomes"
        assert stats.passing_yards == 4500
        assert stats.passing_tds == 35
    
    def test_player_stats_rushing(self):
        """Test PlayerStats with rushing stats."""
        stats = PlayerStats(
            player_id="ps-2",
            player_name="Isiah Pacheco",
            team="Chiefs",
            position="RB",
            rushing_yards=800,
            rushing_tds=8,
            yards_per_carry=4.5
        )
        
        assert stats.rushing_yards == 800
        assert stats.yards_per_carry == 4.5


class TestAgentActionModel:
    """Test suite for AgentAction model."""
    
    def test_agent_action_creation(self):
        """Test creating AgentAction."""
        action = AgentAction(
            id="action-1",
            tool="fetch_matches",
            description="Fetch NFL games"
        )
        
        assert action.id == "action-1"
        assert action.tool == "fetch_matches"
        assert action.status == ActionStatus.PENDING
    
    def test_agent_action_with_approval(self):
        """Test AgentAction requiring approval."""
        action = AgentAction(
            id="action-2",
            tool="save_favorite_team",
            description="Save team to favorites",
            requires_approval=True
        )
        
        assert action.requires_approval is True


class TestAgentPlanModel:
    """Test suite for AgentPlan model."""
    
    def test_agent_plan_creation(self):
        """Test creating AgentPlan."""
        action = AgentAction(
            id="a1",
            tool="fetch_matches",
            description="Fetch games"
        )
        plan = AgentPlan(
            goal="Show NFL games",
            steps=[action]
        )
        
        assert plan.goal == "Show NFL games"
        assert len(plan.steps) == 1
        assert plan.status == "created"


class TestClientActionModel:
    """Test suite for ClientAction model."""
    
    def test_client_action_creation(self):
        """Test creating ClientAction."""
        action = ClientAction(
            type=ClientActionType.FILTER_RESULTS,
            target="results-container",
            payload={"filters": ["league", "team"]},
            description="Add filters to results"
        )
        
        assert action.type == ClientActionType.FILTER_RESULTS
        assert action.target == "results-container"
        assert "filters" in action.payload


class TestKnowledgeItemModel:
    """Test suite for KnowledgeItem model."""
    
    def test_knowledge_item_creation(self):
        """Test creating KnowledgeItem."""
        item = KnowledgeItem(
            id="ki-1",
            type="favorite_team",
            content={"team_name": "Chiefs"},
            tags=["favorites", "nfl"]
        )
        
        assert item.id == "ki-1"
        assert item.type == "favorite_team"
        assert len(item.tags) == 2


class TestUserGoalRequestModel:
    """Test suite for UserGoalRequest model."""
    
    def test_goal_request_creation(self):
        """Test creating UserGoalRequest."""
        request = UserGoalRequest(
            goal="Show me NFL games today"
        )
        
        assert request.goal == "Show me NFL games today"
        assert request.session_id is None
    
    def test_goal_request_with_session(self):
        """Test UserGoalRequest with session."""
        request = UserGoalRequest(
            goal="Show standings",
            session_id="session-123"
        )
        
        assert request.session_id == "session-123"


class TestAgentResponseModel:
    """Test suite for AgentResponse model."""
    
    def test_agent_response_creation(self):
        """Test creating AgentResponse."""
        action = AgentAction(
            id="a1",
            tool="test",
            description="Test"
        )
        plan = AgentPlan(goal="Test goal", steps=[action])
        
        response = AgentResponse(
            session_id="session-1",
            plan=plan,
            message="Here are the results"
        )
        
        assert response.session_id == "session-1"
        assert response.message == "Here are the results"


class TestApprovalRequestModel:
    """Test suite for ApprovalRequest model."""
    
    def test_approval_request_approved(self):
        """Test ApprovalRequest with approval."""
        request = ApprovalRequest(
            action_id="action-123",
            approved=True,
            session_id="session-1"
        )
        
        assert request.approved is True
        assert request.action_id == "action-123"
    
    def test_approval_request_rejected(self):
        """Test ApprovalRequest with rejection."""
        request = ApprovalRequest(
            action_id="action-456",
            approved=False,
            session_id="session-2"
        )
        
        assert request.approved is False
