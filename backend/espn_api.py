"""
ESPN API Client - Real-time sports data from ESPN's public API.
Supports multiple sports: Soccer, NFL, and more.
"""

import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import asyncio


class Sport(Enum):
    """Supported sports."""
    SOCCER = "soccer"
    NFL = "football/nfl"
    COLLEGE_FOOTBALL = "football/college-football"
    COLLEGE_BASKETBALL = "basketball/mens-college-basketball"
    UFC = "mma/ufc"
    CFL = "football/cfl"
    XFL = "football/xfl"
    USFL = "football/usfl"


# Football league codes for ESPN API
FOOTBALL_LEAGUES = {
    # NFL
    "nfl": "nfl",
    "national football league": "nfl",
    # College Football
    "ncaaf": "college-football",
    "college football": "college-football",
    "college-football": "college-football",
    "cfb": "college-football",
    "fbs": "college-football",
    # Canadian Football
    "cfl": "cfl",
    "canadian football": "cfl",
    # Other American Football Leagues
    "xfl": "xfl",
    "usfl": "usfl",
    "ufl": "ufl",
    "aaf": "aaf",
    # Arena Football
    "arena": "arena-football",
    "afl": "arena-football",
}

# College football conferences
COLLEGE_FOOTBALL_CONFERENCES = {
    "sec": "8",
    "southeastern": "8",
    "big ten": "5",
    "big 10": "5",
    "big12": "4",
    "big 12": "4",
    "acc": "1",
    "atlantic coast": "1",
    "pac12": "9",
    "pac 12": "9",
    "pac-12": "9",
    "big east": "2",
    "american": "151",
    "aac": "151",
    "mountain west": "17",
    "mwc": "17",
    "sun belt": "37",
    "mac": "15",
    "mid-american": "15",
    "conference usa": "12",
    "c-usa": "12",
    "independent": "18",
    "ivy league": "22",
    "ivy": "22",
}


# Soccer league codes for ESPN API
SOCCER_LEAGUES = {
    "premier_league": "eng.1",
    "premier league": "eng.1",
    "epl": "eng.1",
    "championship": "eng.2",
    "la_liga": "esp.1",
    "la liga": "esp.1",
    "bundesliga": "ger.1",
    "serie_a": "ita.1",
    "serie a": "ita.1",
    "ligue_1": "fra.1",
    "ligue 1": "fra.1",
    "mls": "usa.1",
    "champions_league": "uefa.champions",
    "champions league": "uefa.champions",
    "ucl": "uefa.champions",
    "europa_league": "uefa.europa",
    "europa league": "uefa.europa",
    "world_cup": "fifa.world",
    "world cup": "fifa.world",
    "liga_mx": "mex.1",
    "eredivisie": "ned.1",
    "scottish": "sco.1",
    "brasileirao": "bra.1",
}


@dataclass
class ESPNConfig:
    """ESPN API configuration."""
    base_url: str = "https://site.api.espn.com/apis/site/v2/sports" # Scores, news, teams, standings
    core_url: str = "https://sports.core.api.espn.com/v2/sports"    # Athletes, stats, odds, detailed data
    web_url: str = "https://site.web.api.espn.com/apis/common/v3"   # Search, athlete profiles
    cdn_url: str = "https://cdn.espn.com/core"                      # Fast/live data (scoreboard, boxscore) 
    fantasy_url: str = "https://fantasy.espn.com/apis/v3/games"     # Fantasy sports leagues
    timeout: float = 30.0


# Fantasy sport codes
FANTASY_SPORT_CODES = {
    "football": "ffl",
}

# Betting provider IDs
BETTING_PROVIDERS = {
    "caesars": 38,
    "bet365": 2000,
    "draftkings": 41,
    "fanduel": 58,
    "betmgm": 45,
    "pointsbet": 53,
    "barstool": 68,
}

# NFL season types
NFL_SEASON_TYPES = {
    "preseason": 1,
    "regular": 2,
    "postseason": 3,
    "offseason": 4,
}

# Football position codes
FOOTBALL_POSITIONS = {
    "qb": "1",
    "rb": "2",
    "wr": "3",
    "te": "4",
    "ol": "5",
    "dl": "6",
    "lb": "7",
    "db": "8",
    "k": "9",
    "p": "10",
    "ls": "11",
}
    

class ESPNClient:
    """
    Async client for ESPN's public API.
    Provides access to scores, teams, standings, players, and more.
    """
    
    def __init__(self, config: Optional[ESPNConfig] = None):
        self.config = config or ESPNConfig()
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                }
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def _request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make an async HTTP request."""
        client = await self._get_client()
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"ESPN API error: {e}")
            return {}
    
    def _sync_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make a synchronous HTTP request (for non-async contexts)."""
        try:
            with httpx.Client(timeout=self.config.timeout) as client:
                response = client.get(
                    url, 
                    params=params,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept": "application/json",
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"ESPN API error: {e}")
            return {}
    
    # ============ Soccer Endpoints ============
    
    def get_soccer_scoreboard(
        self, 
        league: str = "eng.1",
        dates: Optional[str] = None
    ) -> Dict:
        """
        Get soccer scoreboard (matches).
        
        Args:
            league: League code (e.g., 'eng.1' for Premier League)
            dates: Date filter (YYYYMMDD or YYYYMMDD-YYYYMMDD)
        """
        # Normalize league name
        league_code = SOCCER_LEAGUES.get(league.lower(), league)
        url = f"{self.config.base_url}/soccer/{league_code}/scoreboard"
        params = {}
        if dates:
            params["dates"] = dates
        return self._sync_request(url, params)
    
    def get_soccer_teams(self, league: str = "eng.1") -> Dict:
        """Get all teams in a soccer league."""
        league_code = SOCCER_LEAGUES.get(league.lower(), league)
        url = f"{self.config.base_url}/soccer/{league_code}/teams"
        return self._sync_request(url)
    
    def get_soccer_team_detail(self, league: str, team_id: str) -> Dict:
        """Get detailed info for a specific team."""
        league_code = SOCCER_LEAGUES.get(league.lower(), league)
        url = f"{self.config.base_url}/soccer/{league_code}/teams/{team_id}"
        params = {"enable": "roster,stats"}
        return self._sync_request(url, params)
    
    def get_soccer_standings(self, league: str = "eng.1") -> Dict:
        """Get league standings/table."""
        league_code = SOCCER_LEAGUES.get(league.lower(), league)
        # Use v2 API for standings
        url = f"https://site.api.espn.com/apis/v2/sports/soccer/{league_code}/standings"
        return self._sync_request(url)
    
    def get_soccer_news(self, league: str = "eng.1", limit: int = 10) -> Dict:
        """Get latest news for a league."""
        league_code = SOCCER_LEAGUES.get(league.lower(), league)
        url = f"{self.config.base_url}/soccer/{league_code}/news"
        return self._sync_request(url, {"limit": limit})
    
    # ============ NFL Endpoints ============
    
    def get_nfl_scoreboard(self, week: Optional[int] = None, season_type: int = 2) -> Dict:
        """Get NFL scoreboard."""
        url = f"{self.config.base_url}/football/nfl/scoreboard"
        params = {"seasontype": season_type}
        if week:
            params["week"] = week
        return self._sync_request(url, params)
    
    def get_nfl_teams(self) -> Dict:
        """Get all NFL teams."""
        url = f"{self.config.base_url}/football/nfl/teams"
        return self._sync_request(url)
    
    def get_nfl_standings(self) -> Dict:
        """Get NFL standings."""
        url = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
        return self._sync_request(url)
    
    def get_nfl_team_detail(self, team_id: str) -> Dict:
        """Get NFL team detail with roster."""
        url = f"{self.config.base_url}/football/nfl/teams/{team_id}"
        return self._sync_request(url, {"enable": "roster,stats"})
    
    # ============ NBA Endpoints ============
    
    def get_nba_scoreboard(self, dates: Optional[str] = None) -> Dict:
        """Get NBA scoreboard."""
        url = f"{self.config.base_url}/basketball/nba/scoreboard"
        params = {}
        if dates:
            params["dates"] = dates
        return self._sync_request(url, params)
    
    def get_nba_teams(self) -> Dict:
        """Get all NBA teams."""
        url = f"{self.config.base_url}/basketball/nba/teams"
        return self._sync_request(url)
    
    def get_nba_standings(self) -> Dict:
        """Get NBA standings."""
        url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings"
        return self._sync_request(url)
    
    # ============ Football (All Leagues) Endpoints ============
    
    def _normalize_football_league(self, league: str) -> str:
        """Normalize football league name to ESPN code."""
        return FOOTBALL_LEAGUES.get(league.lower(), league)
    
    def get_football_scoreboard(
        self, 
        league: str = "nfl",
        week: Optional[int] = None,
        season_type: int = 2,
        dates: Optional[str] = None,
        year: Optional[int] = None,
        groups: Optional[str] = None
    ) -> Dict:
        """
        Get football scoreboard for any league.
        
        Args:
            league: League code (nfl, college-football, cfl, xfl, etc.)
            week: Week number (NFL/college)
            season_type: 1=preseason, 2=regular, 3=postseason
            dates: Date filter (YYYYMMDD)
            year: Season year
            groups: Conference/group filter for college (e.g., '80' for FBS)
        """
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/scoreboard"
        params = {"seasontype": season_type}
        if week:
            params["week"] = week
        if dates:
            params["dates"] = dates
        if year:
            params["year"] = year
        if groups:
            params["groups"] = groups
        return self._sync_request(url, params)
    
    def get_football_teams(self, league: str = "nfl", groups: Optional[str] = None) -> Dict:
        """
        Get all teams for a football league.
        
        Args:
            league: League code
            groups: Conference/group filter (e.g., '80' for FBS)
        """
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/teams"
        params = {}
        if groups:
            params["groups"] = groups
        return self._sync_request(url, params)
    
    def get_football_team_detail(self, league: str, team_id: str) -> Dict:
        """Get detailed team info with roster and stats."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/teams/{team_id}"
        return self._sync_request(url, {"enable": "roster,stats,schedule"})
    
    def get_football_team_roster(self, league: str, team_id: str) -> Dict:
        """Get team roster with player details."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/teams/{team_id}/roster"
        return self._sync_request(url)
    
    def get_football_team_schedule(self, league: str, team_id: str, year: Optional[int] = None) -> Dict:
        """Get team schedule."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/teams/{team_id}/schedule"
        params = {}
        if year:
            params["season"] = year
        return self._sync_request(url, params)
    
    def get_football_team_stats(self, league: str, team_id: str, year: Optional[int] = None) -> Dict:
        """Get team statistics."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.core_url}/football/leagues/{league_code}/seasons/{year or 2025}/types/2/teams/{team_id}/statistics"
        return self._sync_request(url)
    
    def get_football_team_depthchart(self, league: str, team_id: str) -> Dict:
        """Get team depth chart."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/teams/{team_id}/depthcharts"
        return self._sync_request(url)
    
    def get_football_team_injuries(self, league: str, team_id: str) -> Dict:
        """Get team injury report."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/teams/{team_id}/injuries"
        return self._sync_request(url)
    
    def get_football_standings(
        self, 
        league: str = "nfl",
        year: Optional[int] = None,
        season_type: int = 2
    ) -> Dict:
        """Get football standings for any league."""
        league_code = self._normalize_football_league(league)
        url = f"https://site.api.espn.com/apis/v2/sports/football/{league_code}/standings"
        params = {}
        if year:
            params["season"] = year
        if season_type:
            params["seasontype"] = season_type
        return self._sync_request(url, params)
    
    def get_football_news(self, league: str = "nfl", limit: int = 25) -> Dict:
        """Get latest football news."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/news"
        return self._sync_request(url, {"limit": limit})
    
    def get_football_schedule(
        self, 
        league: str = "nfl",
        year: Optional[int] = None,
        week: Optional[int] = None,
        season_type: int = 2
    ) -> Dict:
        """Get full schedule for a football league."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.cdn_url}/{league_code}/schedule"
        params = {"xhr": 1}
        if year:
            params["year"] = year
        if week:
            params["week"] = week
        if season_type:
            params["seasontype"] = season_type
        return self._sync_request(url, params)
    
    def get_football_game_summary(self, league: str, game_id: str) -> Dict:
        """Get detailed game summary including box score."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/summary"
        return self._sync_request(url, {"event": game_id})
    
    def get_football_game_boxscore(self, league: str, game_id: str) -> Dict:
        """Get game box score."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.cdn_url}/{league_code}/boxscore"
        return self._sync_request(url, {"xhr": 1, "gameId": game_id})
    
    def get_football_game_playbyplay(self, league: str, game_id: str) -> Dict:
        """Get play-by-play data for a game."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.cdn_url}/{league_code}/playbyplay"
        return self._sync_request(url, {"xhr": 1, "gameId": game_id})
    
    def get_football_game_drives(self, league: str, game_id: str) -> Dict:
        """Get drive data for a game."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.core_url}/football/leagues/{league_code}/events/{game_id}/competitions/{game_id}/drives"
        return self._sync_request(url)
    
    def get_football_player(self, league: str, player_id: str) -> Dict:
        """Get football player details."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/athletes/{player_id}"
        return self._sync_request(url)
    
    def get_football_player_stats(self, league: str, player_id: str) -> Dict:
        """Get player career/season statistics."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.web_url}/sports/football/{league_code}/athletes/{player_id}/stats"
        return self._sync_request(url)
    
    def get_football_player_gamelog(self, league: str, player_id: str, year: Optional[int] = None) -> Dict:
        """Get player game-by-game stats."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.web_url}/sports/football/{league_code}/athletes/{player_id}/gamelog"
        params = {}
        if year:
            params["season"] = year
        return self._sync_request(url, params)
    
    def get_football_player_splits(self, league: str, player_id: str) -> Dict:
        """Get player statistical splits."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.web_url}/sports/football/{league_code}/athletes/{player_id}/splits"
        return self._sync_request(url)
    
    def get_football_player_overview(self, league: str, player_id: str) -> Dict:
        """Get player overview including bio, stats summary, news."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.web_url}/sports/football/{league_code}/athletes/{player_id}/overview"
        return self._sync_request(url)
    
    def get_football_leaders(
        self, 
        league: str = "nfl",
        year: Optional[int] = None,
        season_type: int = 2,
        category: Optional[str] = None
    ) -> Dict:
        """
        Get statistical leaders.
        
        Args:
            league: League code
            year: Season year
            season_type: 1=preseason, 2=regular, 3=postseason
            category: Stat category (passing, rushing, receiving, defense, etc.)
        """
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/leaders"
        params = {}
        if year:
            params["season"] = year
        if season_type:
            params["seasontype"] = season_type
        if category:
            params["category"] = category
        return self._sync_request(url, params)
    
    def get_football_rankings(self, league: str = "college-football", year: Optional[int] = None) -> Dict:
        """Get college football rankings (AP, Coaches, CFP)."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/rankings"
        params = {}
        if year:
            params["season"] = year
        return self._sync_request(url, params)
    
    def get_football_recruiting(self, league: str = "college-football", year: Optional[int] = None) -> Dict:
        """Get college football recruiting rankings."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/recruiting/playerrankings"
        params = {}
        if year:
            params["year"] = year
        return self._sync_request(url, params)
    
    def get_football_draft(self, league: str = "nfl", year: int = 2025) -> Dict:
        """Get NFL draft information."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.core_url}/football/leagues/{league_code}/seasons/{year}/draft"
        return self._sync_request(url)
    
    def get_football_draft_picks(self, league: str = "nfl", year: int = 2025, round_num: Optional[int] = None) -> Dict:
        """Get draft picks."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.core_url}/football/leagues/{league_code}/seasons/{year}/draft/picks"
        params = {"limit": 500}
        if round_num:
            params["round"] = round_num
        return self._sync_request(url, params)
    
    def get_football_free_agents(self, league: str = "nfl", year: Optional[int] = None) -> Dict:
        """Get NFL free agents."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/freeagents"
        params = {}
        if year:
            params["season"] = year
        return self._sync_request(url, params)
    
    def get_football_injuries(self, league: str = "nfl") -> Dict:
        """Get league-wide injury report."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/injuries"
        return self._sync_request(url)
    
    def get_football_transactions(self, league: str = "nfl", limit: int = 50) -> Dict:
        """Get recent transactions (trades, signings, releases)."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/transactions"
        return self._sync_request(url, {"limit": limit})
    
    def get_football_qbr(self, league: str = "nfl", year: Optional[int] = None, season_type: int = 2) -> Dict:
        """Get QBR (Total Quarterback Rating) rankings."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/qbr"
        params = {"seasontype": season_type}
        if year:
            params["season"] = year
        return self._sync_request(url, params)
    
    def get_football_fpi(self, league: str = "nfl", year: Optional[int] = None) -> Dict:
        """Get Football Power Index (FPI) rankings."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/fpi"
        params = {}
        if year:
            params["season"] = year
        return self._sync_request(url, params)
    
    def get_football_game_odds(self, league: str, event_id: str) -> Dict:
        """Get betting odds for a football game."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.core_url}/football/leagues/{league_code}/events/{event_id}/competitions/{event_id}/odds"
        return self._sync_request(url)
    
    def get_football_game_predictions(self, league: str, event_id: str) -> Dict:
        """Get win probabilities for a football game."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.core_url}/football/leagues/{league_code}/events/{event_id}/competitions/{event_id}/probabilities"
        return self._sync_request(url)
    
    def get_football_pickcenter(self, league: str = "nfl") -> Dict:
        """Get ESPN expert picks for games."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.cdn_url}/{league_code}/pickcenter"
        return self._sync_request(url, {"xhr": 1})
    
    def get_football_powerindex(self, league: str = "nfl", year: Optional[int] = None) -> Dict:
        """Get team power index ratings."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/powerindex"
        params = {}
        if year:
            params["season"] = year
        return self._sync_request(url, params)
    
    def search_football_players(self, query: str, league: str = "nfl", limit: int = 25) -> Dict:
        """Search for football players by name."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/athletes"
        return self._sync_request(url, {"search": query, "limit": limit})
    
    def get_football_conferences(self, league: str = "college-football") -> Dict:
        """Get all conferences for college football."""
        league_code = self._normalize_football_league(league)
        url = f"{self.config.base_url}/football/{league_code}/groups"
        return self._sync_request(url)
    
    def get_football_superbowl_odds(self, year: int = 2025) -> Dict:
        """Get Super Bowl futures/odds."""
        url = f"{self.config.core_url}/football/leagues/nfl/seasons/{year}/futures"
        return self._sync_request(url)
    
    # ============ Generic Sport Endpoints ============
    
    def get_scoreboard(self, sport: str, league: str, dates: Optional[str] = None) -> Dict:
        """
        Get scoreboard for any sport.
        
        Args:
            sport: Sport type (e.g., 'football', 'basketball', 'soccer')
            league: League code (e.g., 'nfl', 'nba', 'eng.1')
            dates: Optional date filter
        """
        url = f"{self.config.base_url}/{sport}/{league}/scoreboard"
        params = {}
        if dates:
            params["dates"] = dates
        return self._sync_request(url, params)
    
    def get_teams(self, sport: str, league: str) -> Dict:
        """Get teams for any sport/league."""
        url = f"{self.config.base_url}/{sport}/{league}/teams"
        return self._sync_request(url)
    
    def get_standings(self, sport: str, league: str) -> Dict:
        """Get standings for any sport/league."""
        url = f"https://site.api.espn.com/apis/v2/sports/{sport}/{league}/standings"
        return self._sync_request(url)
    
    def get_news(self, sport: str, league: str, limit: int = 10) -> Dict:
        """Get news for any sport/league."""
        url = f"{self.config.base_url}/{sport}/{league}/news"
        return self._sync_request(url, {"limit": limit})

    # ============ Fantasy League Endpoints ============
    
    def get_fantasy_league(
        self, 
        sport: str = "football", 
        year: int = 2024, 
        league_id: str = None,
        views: List[str] = None
    ) -> Dict:
        """
        Get fantasy league data (public leagues only).
        
        Args:
            sport: Sport type (football, basketball, baseball, hockey)
            year: Season year
            league_id: The fantasy league ID
            views: List of views (mTeam, mRoster, mMatchup, mSettings, mDraftDetail)
        """
        sport_code = FANTASY_SPORT_CODES.get(sport.lower(), "ffl")
        url = f"{self.config.fantasy_url}/{sport_code}/seasons/{year}/segments/0/leagues/{league_id}"
        params = {}
        if views:
            params["view"] = views
        return self._sync_request(url, params)
    
    def get_fantasy_teams(self, sport: str = "football", year: int = 2024, league_id: str = None) -> Dict:
        """Get fantasy league teams."""
        return self.get_fantasy_league(sport, year, league_id, views=["mTeam"])
    
    def get_fantasy_rosters(self, sport: str = "football", year: int = 2024, league_id: str = None) -> Dict:
        """Get fantasy league rosters."""
        return self.get_fantasy_league(sport, year, league_id, views=["mRoster"])
    
    def get_fantasy_matchups(self, sport: str = "football", year: int = 2024, league_id: str = None) -> Dict:
        """Get fantasy league matchups."""
        return self.get_fantasy_league(sport, year, league_id, views=["mMatchup"])
    
    def get_fantasy_settings(self, sport: str = "football", year: int = 2024, league_id: str = None) -> Dict:
        """Get fantasy league settings."""
        return self.get_fantasy_league(sport, year, league_id, views=["mSettings"])
    
    def get_fantasy_draft(self, sport: str = "football", year: int = 2024, league_id: str = None) -> Dict:
        """Get fantasy league draft details."""
        return self.get_fantasy_league(sport, year, league_id, views=["mDraftDetail"])

    # ============ Athlete Endpoints ============
    
    def get_athlete_overview(self, sport: str, league: str, athlete_id: str) -> Dict:
        """
        Get athlete overview.
        URL: site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/overview
        """
        url = f"{self.config.web_url}/sports/{sport}/{league}/athletes/{athlete_id}/overview"
        return self._sync_request(url)
    
    def get_athlete_gamelog(self, sport: str, league: str, athlete_id: str) -> Dict:
        """
        Get athlete game log.
        URL: site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/gamelog
        """
        url = f"{self.config.web_url}/sports/{sport}/{league}/athletes/{athlete_id}/gamelog"
        return self._sync_request(url)
    
    def get_athlete_splits(self, sport: str, league: str, athlete_id: str) -> Dict:
        """
        Get athlete statistical splits.
        URL: site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/splits
        """
        url = f"{self.config.web_url}/sports/{sport}/{league}/athletes/{athlete_id}/splits"
        return self._sync_request(url)
    
    def get_athlete_stats(self, sport: str, league: str, athlete_id: str) -> Dict:
        """
        Get athlete statistics.
        URL: site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/stats
        """
        url = f"{self.config.web_url}/sports/{sport}/{league}/athletes/{athlete_id}/stats"
        return self._sync_request(url)

    # ============ Core API Endpoints (Detailed Data) ============
    
    def get_all_athletes(self, sport: str, league: str, limit: int = 1000) -> Dict:
        """
        Get all athletes for a sport/league.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/athletes
        """
        url = f"{self.config.core_url}/{sport}/leagues/{league}/athletes"
        return self._sync_request(url, {"limit": limit})
    
    def get_seasons(self, sport: str, league: str) -> Dict:
        """
        Get all seasons for a sport/league.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/seasons
        """
        url = f"{self.config.core_url}/{sport}/leagues/{league}/seasons"
        return self._sync_request(url)
    
    def get_season_teams(self, sport: str, league: str, year: int) -> Dict:
        """
        Get teams for a specific season.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/seasons/{year}/teams
        """
        url = f"{self.config.core_url}/{sport}/leagues/{league}/seasons/{year}/teams"
        return self._sync_request(url)
    
    def get_draft(self, sport: str, league: str, year: int) -> Dict:
        """
        Get draft data for a season.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/seasons/{year}/draft
        """
        url = f"{self.config.core_url}/{sport}/leagues/{league}/seasons/{year}/draft"
        return self._sync_request(url)
    
    def get_events(self, sport: str, league: str, dates: str = None) -> Dict:
        """
        Get events for a sport/league.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/events
        """
        url = f"{self.config.core_url}/{sport}/leagues/{league}/events"
        params = {}
        if dates:
            params["dates"] = dates
        return self._sync_request(url, params)
    
    def get_venues(self, sport: str, league: str, limit: int = 500) -> Dict:
        """
        Get all venues for a sport/league.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/venues
        """
        url = f"{self.config.core_url}/{sport}/leagues/{league}/venues"
        return self._sync_request(url, {"limit": limit})
    
    def get_franchises(self, sport: str, league: str) -> Dict:
        """
        Get all franchises for a sport/league.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/franchises
        """
        url = f"{self.config.core_url}/{sport}/leagues/{league}/franchises"
        return self._sync_request(url)
    
    def get_positions(self, sport: str, league: str) -> Dict:
        """
        Get all positions for a sport/league.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/positions
        """
        url = f"{self.config.core_url}/{sport}/leagues/{league}/positions"
        return self._sync_request(url)

    # ============ CDN Endpoints (Fast/Live Data) ============
    
    def get_cdn_scoreboard(self, league: str) -> Dict:
        """
        Get live scoreboard from CDN (fast).
        URL: cdn.espn.com/core/{league}/scoreboard?xhr=1
        """
        url = f"{self.config.cdn_url}/{league}/scoreboard"
        return self._sync_request(url, {"xhr": 1})
    
    def get_cdn_boxscore(self, league: str, game_id: str) -> Dict:
        """
        Get boxscore from CDN.
        URL: cdn.espn.com/core/{league}/boxscore?xhr=1&gameId={id}
        """
        url = f"{self.config.cdn_url}/{league}/boxscore"
        return self._sync_request(url, {"xhr": 1, "gameId": game_id})
    
    def get_cdn_playbyplay(self, league: str, game_id: str) -> Dict:
        """
        Get play-by-play from CDN.
        URL: cdn.espn.com/core/{league}/playbyplay?xhr=1&gameId={id}
        """
        url = f"{self.config.cdn_url}/{league}/playbyplay"
        return self._sync_request(url, {"xhr": 1, "gameId": game_id})
    
    def get_cdn_schedule(self, league: str) -> Dict:
        """
        Get schedule from CDN.
        URL: cdn.espn.com/core/{league}/schedule?xhr=1
        """
        url = f"{self.config.cdn_url}/{league}/schedule"
        return self._sync_request(url, {"xhr": 1})
    
    def get_cdn_standings(self, league: str) -> Dict:
        """
        Get standings from CDN.
        URL: cdn.espn.com/core/{league}/standings?xhr=1
        """
        url = f"{self.config.cdn_url}/{league}/standings"
        return self._sync_request(url, {"xhr": 1})

    # ============ Betting & Odds Endpoints ============
    
    def get_game_odds(self, sport: str, league: str, event_id: str, competition_id: str = None) -> Dict:
        """
        Get betting odds for a game.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/events/{id}/competitions/{id}/odds
        """
        comp_id = competition_id or event_id
        url = f"{self.config.core_url}/{sport}/leagues/{league}/events/{event_id}/competitions/{comp_id}/odds"
        return self._sync_request(url)
    
    def get_win_probabilities_sync(self, sport: str, league: str, event_id: str, competition_id: str = None) -> Dict:
        """
        Get win probabilities for a game.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/events/{id}/competitions/{id}/probabilities
        """
        comp_id = competition_id or event_id
        url = f"{self.config.core_url}/{sport}/leagues/{league}/events/{event_id}/competitions/{comp_id}/probabilities"
        return self._sync_request(url)
    
    def get_futures_sync(self, sport: str, league: str, year: int) -> Dict:
        """
        Get futures/season-long bets.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/seasons/{year}/futures
        """
        url = f"{self.config.core_url}/{sport}/leagues/{league}/seasons/{year}/futures"
        return self._sync_request(url)
    
    def get_ats_records(self, sport: str, league: str, year: int, season_type: int, team_id: str) -> Dict:
        """
        Get against-the-spread records for a team.
        URL: sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/seasons/{year}/types/{type}/teams/{id}/ats
        """
        url = f"{self.config.core_url}/{sport}/leagues/{league}/seasons/{year}/types/{season_type}/teams/{team_id}/ats"
        return self._sync_request(url)
    
    # ============ Search Endpoint ============
    
    def search(self, query: str, limit: int = 10) -> Dict:
        """
        Search ESPN for athletes, teams, etc.
        
        Args:
            query: Search term
            limit: Max results
        """
        url = f"{self.config.web_url}/search"
        return self._sync_request(url, {"query": query, "limit": limit})
    
    # ============ Helper Methods ============
    
    def parse_matches(self, scoreboard_data: Dict) -> List[Dict]:
        """
        Parse scoreboard data into a list of matches.
        
        Returns standardized match format.
        """
        matches = []
        events = scoreboard_data.get("events", [])
        
        for event in events:
            competitions = event.get("competitions", [])
            if not competitions:
                continue
            
            comp = competitions[0]
            competitors = comp.get("competitors", [])
            
            if len(competitors) < 2:
                continue
            
            # Get home and away teams
            home_team = None
            away_team = None
            for c in competitors:
                if c.get("homeAway") == "home":
                    home_team = c
                else:
                    away_team = c
            
            if not home_team or not away_team:
                home_team = competitors[0]
                away_team = competitors[1]
            
            # Parse status
            status_obj = comp.get("status", {})
            status_type = status_obj.get("type", {})
            status_name = status_type.get("name", "STATUS_SCHEDULED")
            
            if status_name == "STATUS_FINAL":
                status = "finished"
            elif status_name == "STATUS_IN_PROGRESS":
                status = "live"
            elif status_name in ["STATUS_HALFTIME", "STATUS_END_PERIOD"]:
                status = "live"
            else:
                status = "scheduled"
            
            # Parse scores
            home_score = home_team.get("score")
            away_score = away_team.get("score")
            
            if home_score:
                try:
                    home_score = int(home_score)
                except (ValueError, TypeError):
                    home_score = None
            
            if away_score:
                try:
                    away_score = int(away_score)
                except (ValueError, TypeError):
                    away_score = None
            
            # Get venue
            venue = comp.get("venue", {}).get("fullName", "Unknown Venue")
            
            # Get league info
            league_obj = event.get("league", scoreboard_data.get("leagues", [{}])[0] if scoreboard_data.get("leagues") else {})
            league_name = league_obj.get("name", "Unknown League")
            
            match = {
                "id": event.get("id", ""),
                "name": event.get("name", ""),
                "short_name": event.get("shortName", ""),
                "home_team": home_team.get("team", {}).get("displayName", home_team.get("team", {}).get("name", "Unknown")),
                "home_team_abbr": home_team.get("team", {}).get("abbreviation", ""),
                "home_team_logo": home_team.get("team", {}).get("logo", ""),
                "away_team": away_team.get("team", {}).get("displayName", away_team.get("team", {}).get("name", "Unknown")),
                "away_team_abbr": away_team.get("team", {}).get("abbreviation", ""),
                "away_team_logo": away_team.get("team", {}).get("logo", ""),
                "home_score": home_score,
                "away_score": away_score,
                "status": status,
                "status_detail": status_obj.get("type", {}).get("shortDetail", ""),
                "kickoff_time": event.get("date", ""),
                "venue": venue,
                "league": league_name,
                "broadcast": comp.get("broadcasts", [{}])[0].get("names", []) if comp.get("broadcasts") else [],
            }
            matches.append(match)
        
        return matches
    
    def parse_standings(self, standings_data: Dict) -> List[Dict]:
        """Parse standings data into a list of team standings."""
        standings = []
        
        children = standings_data.get("children", [])
        if not children:
            # Try direct standings format
            entries = standings_data.get("standings", {}).get("entries", [])
            for entry in entries:
                team = entry.get("team", {})
                stats = {s.get("name"): s.get("value") for s in entry.get("stats", [])}
                
                standings.append({
                    "position": int(stats.get("rank", 0)),
                    "team": team.get("displayName", team.get("name", "Unknown")),
                    "team_abbr": team.get("abbreviation", ""),
                    "team_logo": team.get("logos", [{}])[0].get("href", "") if team.get("logos") else "",
                    "played": int(stats.get("gamesPlayed", 0)),
                    "won": int(stats.get("wins", 0)),
                    "drawn": int(stats.get("ties", stats.get("draws", 0))),
                    "lost": int(stats.get("losses", 0)),
                    "goals_for": int(stats.get("pointsFor", 0)),
                    "goals_against": int(stats.get("pointsAgainst", 0)),
                    "goal_difference": int(stats.get("pointDifferential", 0)),
                    "points": int(stats.get("points", 0)),
                })
            return standings
        
        # Handle grouped standings (e.g., conferences)
        for group in children:
            group_name = group.get("name", "")
            entries = group.get("standings", {}).get("entries", [])
            
            for entry in entries:
                team = entry.get("team", {})
                stats = {s.get("name"): s.get("value") for s in entry.get("stats", [])}
                
                standings.append({
                    "position": int(stats.get("rank", len(standings) + 1)),
                    "team": team.get("displayName", team.get("name", "Unknown")),
                    "team_abbr": team.get("abbreviation", ""),
                    "team_logo": team.get("logos", [{}])[0].get("href", "") if team.get("logos") else "",
                    "group": group_name,
                    "played": int(stats.get("gamesPlayed", 0)),
                    "won": int(stats.get("wins", 0)),
                    "drawn": int(stats.get("ties", stats.get("draws", 0))),
                    "lost": int(stats.get("losses", 0)),
                    "goals_for": int(stats.get("pointsFor", 0)),
                    "goals_against": int(stats.get("pointsAgainst", 0)),
                    "goal_difference": int(stats.get("pointDifferential", 0)),
                    "points": int(stats.get("points", 0)),
                })
        
        return standings
    
    def parse_teams(self, teams_data: Dict) -> List[Dict]:
        """Parse teams data into a list of teams."""
        teams = []
        sports = teams_data.get("sports", [])
        
        for sport in sports:
            leagues = sport.get("leagues", [])
            for league in leagues:
                league_name = league.get("name", "")
                for team in league.get("teams", []):
                    team_info = team.get("team", {})
                    teams.append({
                        "id": team_info.get("id", ""),
                        "name": team_info.get("displayName", team_info.get("name", "")),
                        "abbr": team_info.get("abbreviation", ""),
                        "location": team_info.get("location", ""),
                        "nickname": team_info.get("nickname", ""),
                        "color": team_info.get("color", ""),
                        "logo": team_info.get("logos", [{}])[0].get("href", "") if team_info.get("logos") else "",
                        "league": league_name,
                    })
        
        return teams

    # ============ Football Parsing Helpers ============
    
    def parse_football_games(self, scoreboard_data: Dict) -> List[Dict]:
        """
        Parse football scoreboard data into a standardized list of games.
        Works for NFL, college football, CFL, etc.
        """
        games = []
        events = scoreboard_data.get("events", [])
        
        for event in events:
            competitions = event.get("competitions", [])
            if not competitions:
                continue
            
            comp = competitions[0]
            competitors = comp.get("competitors", [])
            
            if len(competitors) < 2:
                continue
            
            # Get home and away teams
            home_team = None
            away_team = None
            for c in competitors:
                if c.get("homeAway") == "home":
                    home_team = c
                else:
                    away_team = c
            
            if not home_team or not away_team:
                home_team = competitors[0]
                away_team = competitors[1]
            
            # Parse status
            status_obj = comp.get("status", {})
            status_type = status_obj.get("type", {})
            status_name = status_type.get("name", "STATUS_SCHEDULED")
            
            if status_name == "STATUS_FINAL":
                status = "final"
            elif status_name in ["STATUS_IN_PROGRESS", "STATUS_HALFTIME", "STATUS_END_PERIOD"]:
                status = "in_progress"
            elif status_name == "STATUS_POSTPONED":
                status = "postponed"
            elif status_name == "STATUS_CANCELED":
                status = "canceled"
            else:
                status = "scheduled"
            
            # Parse scores
            home_score = self._safe_int(home_team.get("score"))
            away_score = self._safe_int(away_team.get("score"))
            
            # Get quarter/period info
            period = status_obj.get("period", 0)
            clock = status_obj.get("displayClock", "")
            
            # Get odds if available
            odds_data = comp.get("odds", [{}])[0] if comp.get("odds") else {}
            spread = odds_data.get("details", "")
            over_under = odds_data.get("overUnder", "")
            
            # Get broadcast info
            broadcasts = []
            for b in comp.get("broadcasts", []):
                broadcasts.extend(b.get("names", []))
            
            # Get venue
            venue = comp.get("venue", {})
            
            # Get records
            home_record = self._get_team_record(home_team)
            away_record = self._get_team_record(away_team)
            
            # Get ranking for college football
            home_rank = home_team.get("curatedRank", {}).get("current", 0)
            away_rank = away_team.get("curatedRank", {}).get("current", 0)
            
            game = {
                "id": event.get("id", ""),
                "uid": event.get("uid", ""),
                "name": event.get("name", ""),
                "short_name": event.get("shortName", ""),
                "date": event.get("date", ""),
                "week": event.get("week", {}).get("number", 0),
                "season_type": event.get("season", {}).get("type", 2),
                "home_team": {
                    "id": home_team.get("team", {}).get("id", ""),
                    "name": home_team.get("team", {}).get("displayName", ""),
                    "abbreviation": home_team.get("team", {}).get("abbreviation", ""),
                    "logo": home_team.get("team", {}).get("logo", ""),
                    "color": home_team.get("team", {}).get("color", ""),
                    "score": home_score,
                    "record": home_record,
                    "rank": home_rank if home_rank > 0 else None,
                    "winner": home_team.get("winner", False),
                },
                "away_team": {
                    "id": away_team.get("team", {}).get("id", ""),
                    "name": away_team.get("team", {}).get("displayName", ""),
                    "abbreviation": away_team.get("team", {}).get("abbreviation", ""),
                    "logo": away_team.get("team", {}).get("logo", ""),
                    "color": away_team.get("team", {}).get("color", ""),
                    "score": away_score,
                    "record": away_record,
                    "rank": away_rank if away_rank > 0 else None,
                    "winner": away_team.get("winner", False),
                },
                "status": status,
                "status_detail": status_type.get("shortDetail", ""),
                "period": period,
                "clock": clock,
                "venue": {
                    "name": venue.get("fullName", ""),
                    "city": venue.get("address", {}).get("city", ""),
                    "state": venue.get("address", {}).get("state", ""),
                },
                "odds": {
                    "spread": spread,
                    "over_under": over_under,
                },
                "broadcasts": broadcasts,
                "attendance": comp.get("attendance", 0),
                "neutral_site": comp.get("neutralSite", False),
                "conference_competition": comp.get("conferenceCompetition", False),
            }
            games.append(game)
        
        return games
    
    def parse_football_standings(self, standings_data: Dict) -> List[Dict]:
        """Parse football standings into a standardized format."""
        standings = []
        
        children = standings_data.get("children", [])
        
        # Handle grouped standings (conferences/divisions)
        for group in children:
            group_name = group.get("name", "")
            subgroups = group.get("children", [])
            
            if subgroups:
                # Has divisions within conference
                for subgroup in subgroups:
                    division_name = subgroup.get("name", "")
                    entries = subgroup.get("standings", {}).get("entries", [])
                    for entry in entries:
                        standings.append(self._parse_football_standing_entry(entry, group_name, division_name))
            else:
                # Direct entries in conference
                entries = group.get("standings", {}).get("entries", [])
                for entry in entries:
                    standings.append(self._parse_football_standing_entry(entry, group_name, ""))
        
        # If no children, try direct standings format
        if not children:
            entries = standings_data.get("standings", {}).get("entries", [])
            for entry in entries:
                standings.append(self._parse_football_standing_entry(entry, "", ""))
        
        return standings
    
    def _parse_football_standing_entry(self, entry: Dict, conference: str, division: str) -> Dict:
        """Parse a single standing entry."""
        team = entry.get("team", {})
        stats = {s.get("name"): s.get("value") for s in entry.get("stats", [])}
        
        return {
            "team_id": team.get("id", ""),
            "team": team.get("displayName", team.get("name", "Unknown")),
            "abbreviation": team.get("abbreviation", ""),
            "logo": team.get("logos", [{}])[0].get("href", "") if team.get("logos") else "",
            "conference": conference,
            "division": division,
            "rank": self._safe_int(stats.get("rank", 0)) or self._safe_int(stats.get("playoffSeed", 0)),
            "wins": self._safe_int(stats.get("wins", 0)),
            "losses": self._safe_int(stats.get("losses", 0)),
            "ties": self._safe_int(stats.get("ties", 0)),
            "win_pct": float(stats.get("winPercent", 0)),
            "points_for": self._safe_int(stats.get("pointsFor", 0)),
            "points_against": self._safe_int(stats.get("pointsAgainst", 0)),
            "point_diff": self._safe_int(stats.get("pointDifferential", 0)),
            "conference_wins": self._safe_int(stats.get("vsConf_wins", 0)),
            "conference_losses": self._safe_int(stats.get("vsConf_losses", 0)),
            "division_wins": self._safe_int(stats.get("divisionWins", stats.get("vsDiv_wins", 0))),
            "division_losses": self._safe_int(stats.get("divisionLosses", stats.get("vsDiv_losses", 0))),
            "home_wins": self._safe_int(stats.get("homeWins", stats.get("Home_wins", 0))),
            "home_losses": self._safe_int(stats.get("homeLosses", stats.get("Home_losses", 0))),
            "away_wins": self._safe_int(stats.get("roadWins", stats.get("Road_wins", 0))),
            "away_losses": self._safe_int(stats.get("roadLosses", stats.get("Road_losses", 0))),
            "streak": stats.get("streak", ""),
            "clinched": entry.get("note", {}).get("description", "") if entry.get("note") else "",
        }
    
    def parse_football_roster(self, roster_data: Dict) -> List[Dict]:
        """Parse team roster data."""
        players = []
        
        athletes = roster_data.get("athletes", [])
        
        # Handle grouped format (by position)
        for group in athletes:
            position_name = group.get("position", "")
            for athlete in group.get("items", []):
                players.append(self._parse_player(athlete, position_name))
        
        # Handle flat format
        if not athletes:
            for athlete in roster_data.get("roster", []):
                players.append(self._parse_player(athlete, ""))
        
        return players
    
    def _parse_player(self, athlete: Dict, position_group: str) -> Dict:
        """Parse individual player data."""
        return {
            "id": athlete.get("id", ""),
            "uid": athlete.get("uid", ""),
            "name": athlete.get("displayName", athlete.get("fullName", "")),
            "first_name": athlete.get("firstName", ""),
            "last_name": athlete.get("lastName", ""),
            "jersey": athlete.get("jersey", ""),
            "position": athlete.get("position", {}).get("abbreviation", position_group),
            "position_name": athlete.get("position", {}).get("displayName", position_group),
            "height": athlete.get("displayHeight", ""),
            "weight": athlete.get("displayWeight", ""),
            "age": athlete.get("age", 0),
            "experience": athlete.get("experience", {}).get("years", 0),
            "college": athlete.get("college", {}).get("name", ""),
            "birthplace": athlete.get("birthPlace", {}).get("city", ""),
            "headshot": athlete.get("headshot", {}).get("href", ""),
            "status": athlete.get("status", {}).get("type", ""),
            "injuries": [
                {
                    "type": inj.get("type", ""),
                    "detail": inj.get("details", {}).get("detail", ""),
                    "status": inj.get("status", ""),
                }
                for inj in athlete.get("injuries", [])
            ],
        }
    
    def parse_football_player_stats(self, stats_data: Dict) -> Dict:
        """Parse player statistics data."""
        result = {
            "player": {},
            "seasons": [],
            "career": {},
        }
        
        athlete = stats_data.get("athlete", {})
        result["player"] = {
            "id": athlete.get("id", ""),
            "name": athlete.get("displayName", ""),
            "position": athlete.get("position", {}).get("abbreviation", ""),
            "team": athlete.get("team", {}).get("displayName", ""),
        }
        
        # Parse season stats
        for season in stats_data.get("seasons", []):
            season_data = {
                "year": season.get("displayName", ""),
                "type": season.get("type", ""),
                "categories": {},
            }
            
            for category in season.get("categories", []):
                cat_name = category.get("displayName", "")
                stats = {}
                for stat in category.get("stats", []):
                    stats[stat.get("abbreviation", "")] = stat.get("displayValue", "")
                season_data["categories"][cat_name] = stats
            
            result["seasons"].append(season_data)
        
        return result
    
    def parse_football_leaders(self, leaders_data: Dict) -> Dict:
        """Parse statistical leaders data."""
        result = {"categories": []}
        
        for category in leaders_data.get("leaders", []):
            cat_data = {
                "name": category.get("displayName", ""),
                "leaders": [],
            }
            
            for leader in category.get("leaders", [])[:10]:  # Top 10
                athlete = leader.get("athlete", {})
                cat_data["leaders"].append({
                    "rank": leader.get("rank", 0),
                    "value": leader.get("displayValue", ""),
                    "player_id": athlete.get("id", ""),
                    "player_name": athlete.get("displayName", ""),
                    "team": athlete.get("team", {}).get("displayName", ""),
                    "position": athlete.get("position", {}).get("abbreviation", ""),
                    "headshot": athlete.get("headshot", {}).get("href", ""),
                })
            
            result["categories"].append(cat_data)
        
        return result
    
    def parse_football_boxscore(self, boxscore_data: Dict) -> Dict:
        """Parse game box score data."""
        result = {
            "game": {},
            "teams": [],
            "players": [],
            "scoring": [],
            "drives": [],
        }
        
        # Get game info from content section
        content = boxscore_data.get("gamepackageJSON", boxscore_data.get("content", {}))
        
        # Parse team stats
        boxscore = content.get("boxscore", {})
        for team_data in boxscore.get("teams", []):
            team_stats = {
                "team": team_data.get("team", {}).get("displayName", ""),
                "statistics": [],
            }
            for stat in team_data.get("statistics", []):
                team_stats["statistics"].append({
                    "name": stat.get("displayValue", stat.get("name", "")),
                    "value": stat.get("displayValue", ""),
                })
            result["teams"].append(team_stats)
        
        # Parse player stats
        for player_section in boxscore.get("players", []):
            team_name = player_section.get("team", {}).get("displayName", "")
            for stat_category in player_section.get("statistics", []):
                cat_name = stat_category.get("name", "")
                labels = stat_category.get("labels", [])
                
                for athlete in stat_category.get("athletes", []):
                    player_stats = {
                        "team": team_name,
                        "category": cat_name,
                        "player_id": athlete.get("athlete", {}).get("id", ""),
                        "player_name": athlete.get("athlete", {}).get("displayName", ""),
                        "stats": dict(zip(labels, athlete.get("stats", []))),
                    }
                    result["players"].append(player_stats)
        
        # Parse scoring summary
        scoring = content.get("scoringPlays", [])
        for play in scoring:
            result["scoring"].append({
                "quarter": play.get("period", {}).get("number", 0),
                "clock": play.get("clock", {}).get("displayValue", ""),
                "team": play.get("team", {}).get("displayName", ""),
                "description": play.get("text", ""),
                "score": play.get("scoreValue", 0),
            })
        
        return result
    
    def _safe_int(self, value) -> int:
        """Safely convert value to int."""
        if value is None:
            return 0
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    def _get_team_record(self, team_data: Dict) -> str:
        """Extract team record string."""
        records = team_data.get("records", [])
        if records:
            return records[0].get("summary", "")
        return ""

    # ============ Betting & Odds Methods ============
    
    async def get_event_odds(self, event_id: str, competition_id: Optional[str] = None) -> Dict:
        """
        Get betting odds for a specific event.
        ESPN API: /events/{eventId}/competitions/{competitionId}/odds
        """
        # Build competition ID if not provided
        comp_id = competition_id or event_id
        
        # Try different URL patterns
        urls_to_try = [
            f"{self.config.base_url}/football/nfl/events/{event_id}/odds",
            f"{self.config.base_url}/soccer/eng.1/events/{event_id}/competitions/{comp_id}/odds",
            f"{self.config.core_url}/football/leagues/nfl/events/{event_id}/competitions/{comp_id}/odds",
        ]
        
        for url in urls_to_try:
            try:
                data = await self._request(url)
                if data:
                    return self._parse_odds(data)
            except Exception:
                continue
        
        return {"message": "Odds not available for this event", "odds": []}
    
    async def get_win_probabilities(self, event_id: str, competition_id: Optional[str] = None) -> Dict:
        """
        Get win probabilities for a specific event.
        ESPN API: /events/{eventId}/competitions/{competitionId}/probabilities
        """
        comp_id = competition_id or event_id
        
        urls_to_try = [
            f"{self.config.core_url}/football/leagues/nfl/events/{event_id}/competitions/{comp_id}/probabilities",
            f"{self.config.base_url}/football/nfl/events/{event_id}/probabilities",
        ]
        
        for url in urls_to_try:
            try:
                data = await self._request(url)
                if data:
                    return self._parse_probabilities(data)
            except Exception:
                continue
        
        return {"message": "Probabilities not available", "probabilities": []}
    
    async def get_futures(self, sport: str = "football/nfl", year: int = 2024) -> Dict:
        """
        Get futures/season-long bets.
        ESPN API: /seasons/{year}/futures
        """
        url = f"{self.config.core_url}/{sport}/seasons/{year}/futures"
        try:
            data = await self._request(url)
            return data
        except Exception:
            return {"message": "Futures not available", "futures": []}
    
    def _parse_odds(self, data: Dict) -> Dict:
        """Parse odds data."""
        odds_list = []
        
        items = data.get("items", data.get("odds", []))
        if isinstance(items, list):
            for item in items:
                odds_list.append({
                    "provider": item.get("provider", {}).get("name", "Unknown"),
                    "home_odds": item.get("homeTeamOdds", {}).get("moneyLine", "N/A"),
                    "away_odds": item.get("awayTeamOdds", {}).get("moneyLine", "N/A"),
                    "spread": item.get("spread", "N/A"),
                    "over_under": item.get("overUnder", "N/A"),
                    "details": item.get("details", ""),
                })
        
        return {"odds": odds_list}
    
    def _parse_probabilities(self, data: Dict) -> Dict:
        """Parse probabilities data."""
        probs = []
        
        items = data.get("items", [])
        for item in items:
            probs.append({
                "home_win": item.get("homeWinPercentage", 0),
                "away_win": item.get("awayWinPercentage", 0),
                "tie": item.get("tiePercentage", 0),
                "timestamp": item.get("timestamp", ""),
            })
        
        return {"probabilities": probs}


# Singleton instance
espn_client = ESPNClient()
