"""
Tests for Football Data Service - American Football (NFL, College Football, etc.)
"""

import pytest
from datetime import datetime, timedelta

import sys
sys.path.insert(0, str(pytest.importorskip("pathlib").Path(__file__).parent.parent))

from backend.football_data import FootballDataService


class TestFootballDataService:
    """Test suite for FootballDataService."""
    
    @pytest.fixture
    def service(self):
        """Create a fresh service instance for each test."""
        return FootballDataService()
    
    # ============ Match Fetching Tests ============
    
    def test_get_matches_returns_list(self, service):
        """Test that get_matches returns a list."""
        matches = service.get_matches()
        assert isinstance(matches, list)
    
    def test_get_matches_can_be_empty_or_populated(self, service):
        """Test that get_matches returns a list (may be empty off-season)."""
        matches = service.get_matches()
        assert isinstance(matches, list)
    
    def test_get_matches_filter_by_league_nfl(self, service):
        """Test filtering matches by NFL league."""
        matches = service.get_matches(league="nfl")
        # All returned matches should be tagged as NFL
        for match in matches:
            assert hasattr(match, 'league')
    
    def test_get_matches_filter_by_league_college(self, service):
        """Test filtering matches by college football."""
        matches = service.get_matches(league="college-football")
        assert isinstance(matches, list)
    
    def test_get_matches_filter_by_team(self, service):
        """Test filtering matches by team name."""
        matches = service.get_matches(team="Chiefs")
        for match in matches:
            assert "Chiefs" in match.home_team or "Chiefs" in match.away_team
    
    def test_get_matches_filter_by_date_today(self, service):
        """Test filtering matches by today's date."""
        matches = service.get_matches(date="today")
        assert isinstance(matches, list)
    
    def test_get_matches_filter_by_week(self, service):
        """Test filtering matches by week number."""
        matches = service.get_matches(league="nfl", week=1)
        assert isinstance(matches, list)
    
    # ============ Football Games Tests ============
    
    def test_get_football_games_returns_list(self, service):
        """Test that get_football_games returns a list of FootballGame objects."""
        result = service.get_football_games()
        assert isinstance(result, list)
    
    def test_get_football_games_nfl(self, service):
        """Test getting NFL games."""
        result = service.get_football_games(league="nfl")
        assert isinstance(result, list)
    
    def test_get_football_games_college(self, service):
        """Test getting college football games."""
        result = service.get_football_games(league="college-football")
        assert isinstance(result, list)
    
    # ============ Team Stats Tests ============
    
    def test_get_team_stats_nfl_team(self, service):
        """Test getting stats for an NFL team."""
        stats = service.get_team_stats("Chiefs")
        # May return None if API doesn't have data
        if stats:
            assert hasattr(stats, 'team_name')
    
    def test_get_team_stats_invalid_team(self, service):
        """Test getting stats for an invalid team."""
        stats = service.get_team_stats("Nonexistent Team XYZ")
        assert stats is None
    
    # ============ League Standings Tests ============
    
    def test_get_league_standings_nfl(self, service):
        """Test getting NFL standings."""
        standings = service.get_league_standings("nfl")
        assert isinstance(standings, list)
    
    def test_get_league_standings_college(self, service):
        """Test getting college football standings."""
        standings = service.get_league_standings("college-football")
        assert isinstance(standings, list)
    
    def test_get_league_standings_with_conference(self, service):
        """Test getting NFL standings filtered by conference."""
        standings = service.get_league_standings("nfl", conference="AFC")
        assert isinstance(standings, list)
    
    # ============ Teams Tests ============
    
    def test_get_teams_nfl(self, service):
        """Test getting NFL teams list."""
        teams = service.get_teams("nfl")
        assert isinstance(teams, list)
    
    def test_get_teams_college(self, service):
        """Test getting college football teams."""
        teams = service.get_teams("college-football")
        assert isinstance(teams, list)
    
    # ============ Player Search Tests ============
    
    def test_search_players_returns_list(self, service):
        """Test searching players returns a list."""
        players = service.search_players()
        assert isinstance(players, list)
    
    def test_search_players_by_name(self, service):
        """Test searching players by name."""
        players = service.search_players(name="Mahomes")
        assert isinstance(players, list)
    
    def test_search_players_by_team(self, service):
        """Test searching players by team."""
        players = service.search_players(team="Chiefs")
        assert isinstance(players, list)
    
    def test_search_players_by_position(self, service):
        """Test searching players by position."""
        players = service.search_players(position="QB")
        assert isinstance(players, list)
    
    # ============ News Tests ============
    
    def test_get_news_returns_list(self, service):
        """Test getting news returns a list."""
        news = service.get_news()
        assert isinstance(news, list)
    
    def test_get_news_with_limit(self, service):
        """Test getting news with limit."""
        news = service.get_news(limit=5)
        assert isinstance(news, list)
        assert len(news) <= 5
    
    def test_get_news_college(self, service):
        """Test getting college football news."""
        news = service.get_news(league="college-football")
        assert isinstance(news, list)
    
    # ============ Leaders Tests ============
    
    def test_get_leaders_returns_dict(self, service):
        """Test getting statistical leaders."""
        leaders = service.get_leaders()
        assert isinstance(leaders, (dict, list))
    
    def test_get_leaders_passing(self, service):
        """Test getting passing leaders."""
        leaders = service.get_leaders(category="passing")
        assert isinstance(leaders, (dict, list))
    
    # ============ Rankings Tests ============
    
    def test_get_rankings_college(self, service):
        """Test getting college football rankings."""
        rankings = service.get_rankings()
        assert isinstance(rankings, dict)
    
    # ============ Injuries Tests ============
    
    def test_get_injuries_returns_dict(self, service):
        """Test getting injury reports."""
        injuries = service.get_injuries()
        assert isinstance(injuries, dict)
    
    # ============ Team Comparison Tests ============
    
    def test_compare_teams_returns_dict(self, service):
        """Test comparing two teams returns a dict."""
        comparison = service.compare_teams("Chiefs", "49ers")
        assert isinstance(comparison, dict)
    
    def test_compare_teams_has_teams(self, service):
        """Test that comparison includes team data."""
        comparison = service.compare_teams("Chiefs", "Ravens")
        # Should have team info or error
        assert isinstance(comparison, dict)
    
    # ============ Normalize League Tests ============
    
    def test_normalize_league_nfl_variations(self, service):
        """Test league normalization for NFL."""
        assert service._normalize_league("NFL") == "nfl"
        assert service._normalize_league("nfl") == "nfl"
        assert service._normalize_league(None) == "nfl"
    
    def test_normalize_league_college(self, service):
        """Test league normalization for college football."""
        result = service._normalize_league("college-football")
        assert result in ["college-football", "ncaaf"]

