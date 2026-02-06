"""
Tests for ESPN API Client.
Tests the ESPN API wrapper for fetching sports data.
"""

import pytest
from unittest.mock import patch, MagicMock
import asyncio

import sys
sys.path.insert(0, str(pytest.importorskip("pathlib").Path(__file__).parent.parent))

from backend.espn_api import (
    ESPNClient,
    ESPNConfig,
    Sport,
    FOOTBALL_LEAGUES,
    SOCCER_LEAGUES,
    COLLEGE_FOOTBALL_CONFERENCES,
    NFL_SEASON_TYPES,
    FOOTBALL_POSITIONS,
    BETTING_PROVIDERS,
)


class TestESPNConfig:
    """Test suite for ESPNConfig."""
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = ESPNConfig()
        
        assert config.base_url is not None
        assert config.core_url is not None
        assert config.web_url is not None
        assert config.cdn_url is not None
        assert config.fantasy_url is not None
        assert config.timeout == 30.0
    
    def test_config_custom_timeout(self):
        """Test custom timeout configuration."""
        config = ESPNConfig(timeout=60.0)
        
        assert config.timeout == 60.0
    
    def test_config_urls(self):
        """Test that config URLs are valid strings."""
        config = ESPNConfig()
        
        assert "espn.com" in config.base_url
        assert "espn.com" in config.core_url


class TestSportEnum:
    """Test suite for Sport enum."""
    
    def test_soccer(self):
        """Test soccer sport."""
        assert Sport.SOCCER.value == "soccer"
    
    def test_nfl(self):
        """Test NFL sport."""
        assert Sport.NFL.value == "football/nfl"
    
    def test_college_football(self):
        """Test college football sport."""
        assert Sport.COLLEGE_FOOTBALL.value == "football/college-football"
    
    def test_cfl(self):
        """Test CFL sport."""
        assert Sport.CFL.value == "football/cfl"
    
    def test_xfl(self):
        """Test XFL sport."""
        assert Sport.XFL.value == "football/xfl"
    
    def test_usfl(self):
        """Test USFL sport."""
        assert Sport.USFL.value == "football/usfl"


class TestFootballLeaguesMapping:
    """Test suite for FOOTBALL_LEAGUES mapping."""
    
    def test_nfl_mapping(self):
        """Test NFL league mapping."""
        assert FOOTBALL_LEAGUES["nfl"] == "nfl"
        assert FOOTBALL_LEAGUES["national football league"] == "nfl"
    
    def test_college_football_mapping(self):
        """Test college football league mapping."""
        assert FOOTBALL_LEAGUES["college football"] == "college-football"
        assert FOOTBALL_LEAGUES["college-football"] == "college-football"
        assert FOOTBALL_LEAGUES["ncaaf"] == "college-football"
        assert FOOTBALL_LEAGUES["cfb"] == "college-football"
    
    def test_cfl_mapping(self):
        """Test CFL league mapping."""
        assert FOOTBALL_LEAGUES["cfl"] == "cfl"
        assert FOOTBALL_LEAGUES["canadian football"] == "cfl"
    
    def test_xfl_mapping(self):
        """Test XFL league mapping."""
        assert FOOTBALL_LEAGUES["xfl"] == "xfl"
    
    def test_usfl_mapping(self):
        """Test USFL league mapping."""
        assert FOOTBALL_LEAGUES["usfl"] == "usfl"


class TestSoccerLeaguesMapping:
    """Test suite for SOCCER_LEAGUES mapping."""
    
    def test_premier_league_mapping(self):
        """Test Premier League mapping."""
        assert SOCCER_LEAGUES["premier league"] == "eng.1"
        assert SOCCER_LEAGUES["premier_league"] == "eng.1"
        assert SOCCER_LEAGUES["epl"] == "eng.1"
    
    def test_la_liga_mapping(self):
        """Test La Liga mapping."""
        assert SOCCER_LEAGUES["la liga"] == "esp.1"
        assert SOCCER_LEAGUES["la_liga"] == "esp.1"
    
    def test_bundesliga_mapping(self):
        """Test Bundesliga mapping."""
        assert SOCCER_LEAGUES["bundesliga"] == "ger.1"
    
    def test_champions_league_mapping(self):
        """Test Champions League mapping."""
        assert SOCCER_LEAGUES["champions league"] == "uefa.champions"
        assert SOCCER_LEAGUES["ucl"] == "uefa.champions"


class TestCollegeFootballConferences:
    """Test suite for COLLEGE_FOOTBALL_CONFERENCES mapping."""
    
    def test_sec(self):
        """Test SEC conference mapping."""
        assert COLLEGE_FOOTBALL_CONFERENCES["sec"] == "8"
    
    def test_big_ten(self):
        """Test Big Ten conference mapping."""
        assert COLLEGE_FOOTBALL_CONFERENCES["big ten"] == "5"
    
    def test_acc(self):
        """Test ACC conference mapping."""
        assert COLLEGE_FOOTBALL_CONFERENCES["acc"] == "1"
    
    def test_big12(self):
        """Test Big 12 conference mapping."""
        assert COLLEGE_FOOTBALL_CONFERENCES["big 12"] == "4"


class TestNFLSeasonTypes:
    """Test suite for NFL_SEASON_TYPES mapping."""
    
    def test_preseason(self):
        """Test preseason type."""
        assert NFL_SEASON_TYPES["preseason"] == 1
    
    def test_regular(self):
        """Test regular season type."""
        assert NFL_SEASON_TYPES["regular"] == 2
    
    def test_postseason(self):
        """Test postseason type."""
        assert NFL_SEASON_TYPES["postseason"] == 3
    
    def test_offseason(self):
        """Test offseason type."""
        assert NFL_SEASON_TYPES["offseason"] == 4


class TestFootballPositions:
    """Test suite for FOOTBALL_POSITIONS mapping."""
    
    def test_qb(self):
        """Test QB position."""
        assert FOOTBALL_POSITIONS["qb"] == "1"
    
    def test_rb(self):
        """Test RB position."""
        assert FOOTBALL_POSITIONS["rb"] == "2"
    
    def test_wr(self):
        """Test WR position."""
        assert FOOTBALL_POSITIONS["wr"] == "3"
    
    def test_te(self):
        """Test TE position."""
        assert FOOTBALL_POSITIONS["te"] == "4"
    
    def test_k(self):
        """Test K position."""
        assert FOOTBALL_POSITIONS["k"] == "9"


class TestBettingProviders:
    """Test suite for BETTING_PROVIDERS mapping."""
    
    def test_draftkings(self):
        """Test DraftKings provider."""
        assert BETTING_PROVIDERS["draftkings"] == 41
    
    def test_fanduel(self):
        """Test FanDuel provider."""
        assert BETTING_PROVIDERS["fanduel"] == 58
    
    def test_betmgm(self):
        """Test BetMGM provider."""
        assert BETTING_PROVIDERS["betmgm"] == 45


class TestESPNClientInit:
    """Test suite for ESPNClient initialization."""
    
    def test_client_creation(self):
        """Test creating ESPN client."""
        client = ESPNClient()
        
        assert client is not None
        assert client.config is not None
    
    def test_client_with_custom_config(self):
        """Test creating client with custom config."""
        config = ESPNConfig(timeout=60.0)
        client = ESPNClient(config=config)
        
        assert client.config.timeout == 60.0
    
    def test_client_has_config(self):
        """Test that client has config attribute."""
        client = ESPNClient()
        
        assert hasattr(client, 'config')
        assert isinstance(client.config, ESPNConfig)


class TestESPNClientFootballEndpoints:
    """Test suite for ESPN client football endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create ESPN client for testing."""
        return ESPNClient()
    
    def test_normalize_football_league_nfl(self, client):
        """Test normalizing NFL league."""
        result = client._normalize_football_league("nfl")
        assert result == "nfl"
    
    def test_normalize_football_league_college(self, client):
        """Test normalizing college football league."""
        result = client._normalize_football_league("college football")
        assert result == "college-football"
    
    def test_normalize_football_league_unknown(self, client):
        """Test normalizing unknown league returns input."""
        result = client._normalize_football_league("unknown-league")
        assert result == "unknown-league"
    
    def test_get_nfl_scoreboard_returns_dict(self, client):
        """Test that get_nfl_scoreboard returns a dict."""
        result = client.get_nfl_scoreboard()
        
        assert isinstance(result, dict)
    
    def test_get_nfl_teams_returns_dict(self, client):
        """Test that get_nfl_teams returns a dict."""
        result = client.get_nfl_teams()
        
        assert isinstance(result, dict)
    
    def test_get_nfl_standings_returns_dict(self, client):
        """Test that get_nfl_standings returns a dict."""
        result = client.get_nfl_standings()
        
        assert isinstance(result, dict)
    
    def test_get_football_scoreboard_returns_dict(self, client):
        """Test that get_football_scoreboard returns a dict."""
        result = client.get_football_scoreboard(league="nfl")
        
        assert isinstance(result, dict)
    
    def test_get_football_teams_returns_dict(self, client):
        """Test that get_football_teams returns a dict."""
        result = client.get_football_teams(league="nfl")
        
        assert isinstance(result, dict)
    
    def test_get_football_standings_returns_dict(self, client):
        """Test that get_football_standings returns a dict."""
        result = client.get_football_standings(league="nfl")
        
        assert isinstance(result, dict)
    
    def test_get_football_news_returns_dict(self, client):
        """Test that get_football_news returns a dict."""
        result = client.get_football_news(league="nfl")
        
        assert isinstance(result, dict)


class TestESPNClientSoccerEndpoints:
    """Test suite for ESPN client soccer endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create ESPN client for testing."""
        return ESPNClient()
    
    def test_get_soccer_scoreboard_returns_dict(self, client):
        """Test that get_soccer_scoreboard returns a dict."""
        result = client.get_soccer_scoreboard(league="eng.1")
        
        assert isinstance(result, dict)
    
    def test_get_soccer_teams_returns_dict(self, client):
        """Test that get_soccer_teams returns a dict."""
        result = client.get_soccer_teams(league="eng.1")
        
        assert isinstance(result, dict)
    
    def test_get_soccer_standings_returns_dict(self, client):
        """Test that get_soccer_standings returns a dict."""
        result = client.get_soccer_standings(league="eng.1")
        
        assert isinstance(result, dict)
    
    def test_get_soccer_news_returns_dict(self, client):
        """Test that get_soccer_news returns a dict."""
        result = client.get_soccer_news(league="eng.1")
        
        assert isinstance(result, dict)


class TestESPNClientNBAEndpoints:
    """Test suite for ESPN client NBA endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create ESPN client for testing."""
        return ESPNClient()
    
    def test_get_nba_scoreboard_returns_dict(self, client):
        """Test that get_nba_scoreboard returns a dict."""
        result = client.get_nba_scoreboard()
        
        assert isinstance(result, dict)
    
    def test_get_nba_teams_returns_dict(self, client):
        """Test that get_nba_teams returns a dict."""
        result = client.get_nba_teams()
        
        assert isinstance(result, dict)
    
    def test_get_nba_standings_returns_dict(self, client):
        """Test that get_nba_standings returns a dict."""
        result = client.get_nba_standings()
        
        assert isinstance(result, dict)


class TestESPNClientAsyncMethods:
    """Test suite for ESPN client async methods."""
    
    @pytest.fixture
    def client(self):
        """Create ESPN client for testing."""
        return ESPNClient()
    
    @pytest.mark.asyncio
    async def test_close_method(self, client):
        """Test that close method works."""
        await client.close()
        # Should not raise any errors
    
    @pytest.mark.asyncio
    async def test_get_client_method(self, client):
        """Test that _get_client method returns a client."""
        http_client = await client._get_client()
        
        assert http_client is not None
        
        # Clean up
        await client.close()


class TestESPNClientCollegeFootball:
    """Test suite for ESPN client college football endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create ESPN client for testing."""
        return ESPNClient()
    
    def test_get_college_football_scoreboard(self, client):
        """Test getting college football scoreboard."""
        result = client.get_football_scoreboard(league="college-football")
        
        assert isinstance(result, dict)
    
    def test_get_college_football_teams(self, client):
        """Test getting college football teams."""
        result = client.get_football_teams(league="college-football")
        
        assert isinstance(result, dict)
    
    def test_get_college_football_standings(self, client):
        """Test getting college football standings."""
        result = client.get_football_standings(league="college-football")
        
        assert isinstance(result, dict)


class TestESPNClientCFL:
    """Test suite for ESPN client CFL endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create ESPN client for testing."""
        return ESPNClient()
    
    def test_get_cfl_scoreboard(self, client):
        """Test getting CFL scoreboard."""
        result = client.get_football_scoreboard(league="cfl")
        
        assert isinstance(result, dict)
    
    def test_get_cfl_teams(self, client):
        """Test getting CFL teams."""
        result = client.get_football_teams(league="cfl")
        
        assert isinstance(result, dict)


class TestESPNClientErrorHandling:
    """Test suite for ESPN client error handling."""
    
    @pytest.fixture
    def client(self):
        """Create ESPN client for testing."""
        return ESPNClient()
    
    def test_sync_request_handles_errors(self, client):
        """Test that sync request handles errors gracefully."""
        # Request to invalid endpoint
        result = client._sync_request("https://invalid-url.espn.com/nonexistent")
        
        # Should return empty dict on error
        assert isinstance(result, dict)


class TestESPNClientWeekParameter:
    """Test suite for ESPN client with week parameter."""
    
    @pytest.fixture
    def client(self):
        """Create ESPN client for testing."""
        return ESPNClient()
    
    def test_get_nfl_scoreboard_with_week(self, client):
        """Test getting NFL scoreboard for specific week."""
        result = client.get_nfl_scoreboard(week=1)
        
        assert isinstance(result, dict)
    
    def test_get_football_scoreboard_with_week(self, client):
        """Test getting football scoreboard for specific week."""
        result = client.get_football_scoreboard(league="nfl", week=1)
        
        assert isinstance(result, dict)


class TestESPNClientSeasonType:
    """Test suite for ESPN client with season type parameter."""
    
    @pytest.fixture
    def client(self):
        """Create ESPN client for testing."""
        return ESPNClient()
    
    def test_get_nfl_scoreboard_preseason(self, client):
        """Test getting NFL preseason scoreboard."""
        result = client.get_nfl_scoreboard(season_type=1)
        
        assert isinstance(result, dict)
    
    def test_get_nfl_scoreboard_postseason(self, client):
        """Test getting NFL postseason scoreboard."""
        result = client.get_nfl_scoreboard(season_type=3)
        
        assert isinstance(result, dict)
