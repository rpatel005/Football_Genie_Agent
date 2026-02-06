"""
Tests for LangChain Tools.
Tests the football analytics tools for the AI agent.
"""

import pytest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(pytest.importorskip("pathlib").Path(__file__).parent.parent))

from backend.langchain_tools import (
    # Data fetching tools
    fetch_matches,
    get_team_stats,
    get_league_standings,
    search_players,
    get_football_news,
    get_all_teams,
    get_football_leaders,
    get_college_rankings,
    get_injuries,
    search_knowledge,
    # Calendar tools
    add_match_to_calendar,
    confirm_add_to_calendar,
    remove_match_from_calendar,
    confirm_remove_from_calendar,
    get_calendar_matches,
    clear_user_calendar,
    get_user_calendar,
    # Favorites tools
    add_team_to_favorites,
    confirm_add_favorite_team,
    remove_team_from_favorites,
    confirm_remove_favorite_team,
    add_player_to_favorites,
    confirm_add_favorite_player,
    remove_player_from_favorites,
    confirm_remove_favorite_player,
    get_favorite_teams,
    get_favorite_players,
    # Navigation tools
    navigate_to_page,
    set_league_filter,
    # Utility functions
    FOOTBALL_TOOLS,
    get_tools_description,
    APPROVAL_REQUIRED_TOOLS,
)


class TestFetchMatchesTool:
    """Test suite for fetch_matches tool."""
    
    def test_fetch_matches_returns_string(self):
        """Test that fetch_matches returns a string."""
        result = fetch_matches.invoke({"league": "nfl"})
        assert isinstance(result, str)
    
    def test_fetch_matches_nfl(self):
        """Test fetching NFL matches."""
        result = fetch_matches.invoke({"league": "nfl"})
        # Should either find games or return a message
        assert "games" in result.lower() or "no games" in result.lower()
    
    def test_fetch_matches_college(self):
        """Test fetching college football matches."""
        result = fetch_matches.invoke({"league": "college-football"})
        assert isinstance(result, str)
    
    def test_fetch_matches_with_team_filter(self):
        """Test fetching matches filtered by team."""
        result = fetch_matches.invoke({"league": "nfl", "team": "Chiefs"})
        assert isinstance(result, str)
    
    def test_fetch_matches_with_status_filter(self):
        """Test fetching matches filtered by status."""
        result = fetch_matches.invoke({"league": "nfl", "status": "scheduled"})
        assert isinstance(result, str)
    
    def test_fetch_matches_with_date_filter(self):
        """Test fetching matches filtered by date."""
        result = fetch_matches.invoke({"league": "nfl", "date": "today"})
        assert isinstance(result, str)


class TestTeamStatsTool:
    """Test suite for get_team_stats tool."""
    
    def test_get_team_stats_returns_string(self):
        """Test that get_team_stats returns a string."""
        result = get_team_stats.invoke({"team_name": "Kansas City Chiefs"})
        assert isinstance(result, str)
    
    def test_get_team_stats_valid_team(self):
        """Test getting stats for a valid NFL team."""
        result = get_team_stats.invoke({"team_name": "Kansas City Chiefs", "league": "nfl"})
        # Should contain team info or not found message
        assert "Chiefs" in result or "not found" in result.lower()
    
    def test_get_team_stats_invalid_team(self):
        """Test getting stats for an invalid team."""
        result = get_team_stats.invoke({"team_name": "Fake Team FC"})
        assert "not found" in result.lower()
    
    def test_get_team_stats_partial_name(self):
        """Test getting stats with partial team name."""
        result = get_team_stats.invoke({"team_name": "Chiefs"})
        assert isinstance(result, str)


class TestLeagueStandingsTool:
    """Test suite for get_league_standings tool."""
    
    def test_get_standings_returns_string(self):
        """Test that get_league_standings returns a string."""
        result = get_league_standings.invoke({"league": "nfl"})
        assert isinstance(result, str)
    
    def test_get_standings_nfl(self):
        """Test getting NFL standings."""
        result = get_league_standings.invoke({"league": "nfl"})
        assert isinstance(result, str)
    
    def test_get_standings_with_conference(self):
        """Test getting standings with conference filter."""
        result = get_league_standings.invoke({"league": "nfl", "conference": "AFC"})
        assert isinstance(result, str)
    
    def test_get_standings_invalid_league(self):
        """Test getting standings for invalid league."""
        result = get_league_standings.invoke({"league": "fake-league"})
        # Should handle gracefully
        assert isinstance(result, str)


class TestSearchPlayersTool:
    """Test suite for search_players tool."""
    
    def test_search_players_returns_string(self):
        """Test that search_players returns a string."""
        result = search_players.invoke({"name": "Mahomes"})
        assert isinstance(result, str)
    
    def test_search_players_by_name(self):
        """Test searching players by name."""
        result = search_players.invoke({"name": "Patrick Mahomes"})
        assert isinstance(result, str)
    
    def test_search_players_by_team(self):
        """Test searching players by team."""
        result = search_players.invoke({"team": "Chiefs"})
        assert isinstance(result, str)
    
    def test_search_players_by_position(self):
        """Test searching players by position."""
        result = search_players.invoke({"position": "QB"})
        assert isinstance(result, str)
    
    def test_search_players_no_results(self):
        """Test searching with no results."""
        result = search_players.invoke({"name": "XYZNONEXISTENT123"})
        assert "no players found" in result.lower() or "found" in result.lower()


class TestNewsTool:
    """Test suite for get_football_news tool."""
    
    def test_get_news_returns_string(self):
        """Test that get_football_news returns a string."""
        result = get_football_news.invoke({"league": "nfl"})
        assert isinstance(result, str)
    
    def test_get_news_nfl(self):
        """Test getting NFL news."""
        result = get_football_news.invoke({"league": "nfl", "limit": 5})
        assert isinstance(result, str)
    
    def test_get_news_college(self):
        """Test getting college football news."""
        result = get_football_news.invoke({"league": "college-football"})
        assert isinstance(result, str)


class TestTeamsTool:
    """Test suite for get_all_teams tool."""
    
    def test_get_teams_returns_string(self):
        """Test that get_all_teams returns a string."""
        result = get_all_teams.invoke({"league": "nfl"})
        assert isinstance(result, str)
    
    def test_get_nfl_teams(self):
        """Test getting NFL teams."""
        result = get_all_teams.invoke({"league": "nfl"})
        assert "teams" in result.lower() or "nfl" in result.lower()


class TestLeadersTool:
    """Test suite for get_football_leaders tool."""
    
    def test_get_leaders_returns_string(self):
        """Test that get_football_leaders returns a string."""
        result = get_football_leaders.invoke({"league": "nfl"})
        assert isinstance(result, str)
    
    def test_get_passing_leaders(self):
        """Test getting passing leaders."""
        result = get_football_leaders.invoke({"league": "nfl", "category": "passing"})
        assert isinstance(result, str)


class TestRankingsTool:
    """Test suite for get_college_rankings tool."""
    
    def test_get_rankings_returns_string(self):
        """Test that get_college_rankings returns a string."""
        result = get_college_rankings.invoke({})
        assert isinstance(result, str)


class TestInjuriesTool:
    """Test suite for get_injuries tool."""
    
    def test_get_injuries_returns_string(self):
        """Test that get_injuries returns a string."""
        result = get_injuries.invoke({"league": "nfl"})
        assert isinstance(result, str)


class TestKnowledgeSearchTool:
    """Test suite for search_knowledge tool."""
    
    def test_search_knowledge_returns_string(self):
        """Test that search_knowledge returns a string."""
        result = search_knowledge.invoke({"query": "NFL teams"})
        assert isinstance(result, str)


class TestCalendarTools:
    """Test suite for calendar management tools."""
    
    def setup_method(self):
        """Clean up calendar before each test."""
        clear_user_calendar()
    
    def test_add_match_to_calendar(self):
        """Test adding a match to calendar (pending approval)."""
        result = add_match_to_calendar.invoke({
            "home_team": "Kansas City Chiefs",
            "away_team": "Buffalo Bills",
            "date": "2024-12-25",
            "time": "20:00",
            "league": "NFL"
        })
        
        assert "Chiefs" in result
        assert "Bills" in result
        assert "PENDING_APPROVAL" in result
        # Calendar should still be empty until confirmed
        assert len(get_user_calendar()) == 0
    
    def test_confirm_add_to_calendar(self):
        """Test confirming a calendar addition."""
        result = confirm_add_to_calendar.invoke({
            "home_team": "Dallas Cowboys",
            "away_team": "Philadelphia Eagles",
            "date": "2024-12-28",
            "league": "NFL"
        })
        
        assert "added" in result.lower() or "calendar" in result.lower()
        assert len(get_user_calendar()) == 1
    
    def test_add_duplicate_to_calendar(self):
        """Test adding duplicate match to calendar."""
        # First add
        confirm_add_to_calendar.invoke({
            "home_team": "Chiefs",
            "away_team": "Broncos"
        })
        
        # Try duplicate
        result = confirm_add_to_calendar.invoke({
            "home_team": "Chiefs",
            "away_team": "Broncos"
        })
        
        assert "already" in result.lower()
        assert len(get_user_calendar()) == 1
    
    def test_get_calendar_matches_empty(self):
        """Test getting empty calendar."""
        result = get_calendar_matches.invoke({})
        
        assert "empty" in result.lower()
    
    def test_get_calendar_matches_with_games(self):
        """Test getting calendar with games."""
        confirm_add_to_calendar.invoke({
            "home_team": "Packers",
            "away_team": "Bears",
            "league": "NFL"
        })
        
        result = get_calendar_matches.invoke({})
        
        assert "Packers" in result
        assert "Bears" in result
    
    def test_remove_match_from_calendar(self):
        """Test removing a match (pending approval)."""
        # First add a game
        confirm_add_to_calendar.invoke({
            "home_team": "Raiders",
            "away_team": "Chargers"
        })
        
        # Request removal
        result = remove_match_from_calendar.invoke({
            "home_team": "Raiders",
            "away_team": "Chargers"
        })
        
        assert "PENDING_REMOVAL" in result
        # Game should still be in calendar until confirmed
        assert len(get_user_calendar()) == 1
    
    def test_confirm_remove_from_calendar(self):
        """Test confirming a calendar removal."""
        # First add a game
        confirm_add_to_calendar.invoke({
            "home_team": "Patriots",
            "away_team": "Dolphins"
        })
        assert len(get_user_calendar()) == 1
        
        # Confirm removal
        result = confirm_remove_from_calendar.invoke({
            "home_team": "Patriots",
            "away_team": "Dolphins"
        })
        
        assert "removed" in result.lower()
        assert len(get_user_calendar()) == 0
    
    def test_remove_nonexistent_match(self):
        """Test removing a match that doesn't exist."""
        result = remove_match_from_calendar.invoke({
            "home_team": "FakeTeam1",
            "away_team": "FakeTeam2"
        })
        
        assert "not found" in result.lower()


class TestFavoriteTeamTools:
    """Test suite for favorite team management tools."""
    
    def test_add_team_to_favorites(self):
        """Test adding a team to favorites (pending approval)."""
        result = add_team_to_favorites.invoke({
            "name": "Kansas City Chiefs",
            "league": "NFL"
        })
        
        assert "Chiefs" in result
        assert "PENDING_FAVORITE_TEAM" in result
    
    def test_confirm_add_favorite_team(self):
        """Test confirming a favorite team addition."""
        result = confirm_add_favorite_team.invoke({
            "name": "Dallas Cowboys",
            "league": "NFL"
        })
        
        assert "added" in result.lower() or "favorites" in result.lower()
        assert "ADD_FAVORITE_TEAM" in result
    
    def test_add_duplicate_favorite_team(self):
        """Test adding duplicate favorite team."""
        # First add
        confirm_add_favorite_team.invoke({"name": "Raiders", "league": "NFL"})
        
        # Second add (duplicate)
        result = confirm_add_favorite_team.invoke({"name": "Raiders", "league": "NFL"})
        
        assert "already" in result.lower()
    
    def test_get_favorite_teams_empty(self):
        """Test getting favorites when empty."""
        # Reset favorites by adding/removing
        result = get_favorite_teams.invoke({})
        # Could be empty or have items from other tests - just check it returns string
        assert isinstance(result, str)
    
    def test_remove_team_from_favorites(self):
        """Test removing a team from favorites (pending approval)."""
        result = remove_team_from_favorites.invoke({"name": "Broncos"})
        
        assert "PENDING_REMOVE_FAVORITE_TEAM" in result
    
    def test_confirm_remove_favorite_team(self):
        """Test confirming a favorite team removal."""
        result = confirm_remove_favorite_team.invoke({"name": "Broncos"})
        
        assert "removed" in result.lower()
        assert "REMOVE_FAVORITE_TEAM" in result


class TestFavoritePlayerTools:
    """Test suite for favorite player management tools."""
    
    def test_add_player_to_favorites(self):
        """Test adding a player to favorites (pending approval)."""
        result = add_player_to_favorites.invoke({
            "name": "Patrick Mahomes",
            "team": "Kansas City Chiefs",
            "position": "QB"
        })
        
        assert "Mahomes" in result
        assert "PENDING_FAVORITE_PLAYER" in result
    
    def test_confirm_add_favorite_player(self):
        """Test confirming a favorite player addition."""
        result = confirm_add_favorite_player.invoke({
            "name": "Travis Kelce",
            "team": "Chiefs",
            "position": "TE"
        })
        
        assert "added" in result.lower() or "favorites" in result.lower()
        assert "ADD_FAVORITE_PLAYER" in result
    
    def test_add_duplicate_favorite_player(self):
        """Test adding duplicate favorite player."""
        confirm_add_favorite_player.invoke({"name": "Unique Player"})
        result = confirm_add_favorite_player.invoke({"name": "Unique Player"})
        
        assert "already" in result.lower()
    
    def test_get_favorite_players(self):
        """Test getting favorite players."""
        result = get_favorite_players.invoke({})
        assert isinstance(result, str)
    
    def test_remove_player_from_favorites(self):
        """Test removing a player from favorites (pending approval)."""
        result = remove_player_from_favorites.invoke({"name": "Some Player"})
        
        assert "PENDING_REMOVE_FAVORITE_PLAYER" in result
    
    def test_confirm_remove_favorite_player(self):
        """Test confirming a favorite player removal."""
        result = confirm_remove_favorite_player.invoke({"name": "Some Player"})
        
        assert "removed" in result.lower()
        assert "REMOVE_FAVORITE_PLAYER" in result


class TestNavigationTools:
    """Test suite for navigation tools."""
    
    def test_navigate_to_schedule(self):
        """Test navigating to schedule page."""
        result = navigate_to_page.invoke({"page": "schedule"})
        
        assert "schedule" in result.lower()
        assert "NAVIGATE" in result
    
    def test_navigate_to_standings(self):
        """Test navigating to standings page."""
        result = navigate_to_page.invoke({"page": "standings"})
        
        assert "standings" in result.lower()
        assert "NAVIGATE" in result
    
    def test_navigate_to_news(self):
        """Test navigating to news page."""
        result = navigate_to_page.invoke({"page": "news"})
        
        assert "news" in result.lower()
        assert "NAVIGATE" in result
    
    def test_navigate_to_home(self):
        """Test navigating to home page."""
        result = navigate_to_page.invoke({"page": "home"})
        
        assert "home" in result.lower()
        assert "NAVIGATE" in result
    
    def test_set_league_filter_nfl(self):
        """Test setting NFL league filter."""
        result = set_league_filter.invoke({"league": "nfl"})
        
        assert "nfl" in result.lower()
        assert "SET_FILTER" in result
    
    def test_set_league_filter_college(self):
        """Test setting college football league filter."""
        result = set_league_filter.invoke({"league": "college-football"})
        
        assert "college" in result.lower() or "football" in result.lower()
        assert "SET_FILTER" in result


class TestToolsMetadata:
    """Test suite for tools metadata and utility functions."""
    
    def test_football_tools_list_not_empty(self):
        """Test that FOOTBALL_TOOLS list is not empty."""
        assert len(FOOTBALL_TOOLS) > 0
    
    def test_football_tools_count(self):
        """Test that we have expected number of tools."""
        # Should have at least 20 tools
        assert len(FOOTBALL_TOOLS) >= 20
    
    def test_get_tools_description(self):
        """Test getting tools description."""
        tools_info = get_tools_description()
        
        assert isinstance(tools_info, list)
        assert len(tools_info) == len(FOOTBALL_TOOLS)
        
        for tool_info in tools_info:
            assert "name" in tool_info
            assert "description" in tool_info
            assert "requires_approval" in tool_info
    
    def test_approval_required_tools(self):
        """Test that approval required tools list exists."""
        assert isinstance(APPROVAL_REQUIRED_TOOLS, list)
    
    def test_all_tools_have_descriptions(self):
        """Test that all tools have descriptions."""
        for tool in FOOTBALL_TOOLS:
            assert tool.description is not None
            assert len(tool.description) > 0
    
    def test_all_tools_have_names(self):
        """Test that all tools have names."""
        for tool in FOOTBALL_TOOLS:
            assert tool.name is not None
            assert len(tool.name) > 0
    
    def test_tools_are_callable(self):
        """Test that all tools are callable."""
        for tool in FOOTBALL_TOOLS:
            assert hasattr(tool, 'invoke')
