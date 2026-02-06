"""
Football Data Service - Uses ESPN's public API for real-time football data.
Supports: NFL, College Football, CFL, XFL, USFL, and other American Football leagues.
All data is fetched from ESPN APIs - no mock data.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from .models import Match, TeamStats, LeagueStanding, Player, FootballGame
from .espn_api import espn_client, FOOTBALL_LEAGUES, COLLEGE_FOOTBALL_CONFERENCES

# Configure logging
logger = logging.getLogger('🏈 FootballData')


class FootballDataService:
    """
    Service for fetching American Football data from ESPN API.
    Supports NFL, College Football (NCAAF), CFL, XFL, USFL.
    """
    
    def __init__(self):
        self._cache: Dict = {}
    
    def _normalize_league(self, league: Optional[str]) -> str:
        """Normalize league name to ESPN code."""
        if not league:
            return "nfl"
        league_lower = league.lower().strip()
        return FOOTBALL_LEAGUES.get(league_lower, league_lower)
    
    def get_matches(
        self, 
        league: Optional[str] = None, 
        team: Optional[str] = None,
        status: Optional[str] = None,
        date: Optional[str] = None,
        week: Optional[int] = None,
        season_type: int = 2
    ) -> List[Match]:
        """
        Fetch football games from ESPN API.
        
        Args:
            league: League name (e.g., "NFL", "college-football", "CFL")
            team: Filter by team name
            status: Filter by match status (scheduled, live, finished)
            date: Filter by date (today, tomorrow, yesterday, or YYYY-MM-DD)
            week: NFL/College week number
            season_type: 1=preseason, 2=regular, 3=postseason
        
        Returns:
            List of Match objects
        """
        # Determine date parameter for ESPN API
        dates = None
        if date:
            if date == "today":
                dates = datetime.now().strftime("%Y%m%d")
            elif date == "tomorrow":
                dates = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
            elif date == "yesterday":
                dates = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            else:
                try:
                    parsed_date = datetime.strptime(date, "%Y-%m-%d")
                    dates = parsed_date.strftime("%Y%m%d")
                except ValueError:
                    pass
        
        try:
            league_code = self._normalize_league(league)
            logger.info(f"🔍 Fetching matches | League: {league_code}, Team: {team}, Date: {date}, Week: {week}")
            
            # Get scoreboard from ESPN
            scoreboard = espn_client.get_football_scoreboard(
                league=league_code,
                week=week,
                season_type=season_type,
                dates=dates
            )
            
            if not scoreboard or "events" not in scoreboard:
                logger.info(f"   ⚠️ No events found")
                return []
            
            # Parse ESPN response using football parser
            parsed_games = espn_client.parse_football_games(scoreboard)
            logger.info(f"   ✅ Found {len(parsed_games)} games from ESPN")
            
            # Convert to Match objects and filter
            matches = []
            for g in parsed_games:
                # Apply team filter
                if team:
                    team_lower = team.lower()
                    if team_lower not in g["home_team"]["name"].lower() and team_lower not in g["away_team"]["name"].lower():
                        continue
                
                # Map status
                game_status = g["status"]
                if status:
                    if status == "live" and game_status != "in_progress":
                        continue
                    if status == "finished" and game_status != "final":
                        continue
                    if status == "scheduled" and game_status != "scheduled":
                        continue
                
                # Map status to standard format
                status_map = {
                    "final": "finished",
                    "in_progress": "live",
                    "scheduled": "scheduled",
                    "postponed": "postponed",
                    "canceled": "canceled"
                }
                
                # Parse kickoff time
                kickoff = None
                if g["date"]:
                    try:
                        kickoff = datetime.fromisoformat(g["date"].replace("Z", "+00:00"))
                    except:
                        kickoff = datetime.now()
                
                # Get league name
                league_info = scoreboard.get("leagues", [{}])
                league_name = league_info[0].get("name", "NFL") if league_info else "NFL"
                
                match = Match(
                    id=g["id"],
                    home_team=g["home_team"]["name"],
                    away_team=g["away_team"]["name"],
                    home_score=g["home_team"]["score"],
                    away_score=g["away_team"]["score"],
                    status=status_map.get(game_status, game_status),
                    kickoff_time=kickoff or datetime.now(),
                    league=league_name,
                    venue=g["venue"]["name"]
                )
                matches.append(match)
            
            return matches
            
        except Exception as e:
            print(f"ESPN API error: {e}")
            return []
    
    def get_football_games(
        self,
        league: str = "nfl",
        week: Optional[int] = None,
        season_type: int = 2,
        year: Optional[int] = None
    ) -> List[FootballGame]:
        """
        Get detailed football games with full stats.
        
        Args:
            league: League code (nfl, college-football, cfl, etc.)
            week: Week number
            season_type: 1=preseason, 2=regular, 3=postseason
            year: Season year
            
        Returns:
            List of FootballGame objects with detailed info
        """
        try:
            league_code = self._normalize_league(league)
            scoreboard = espn_client.get_football_scoreboard(
                league=league_code,
                week=week,
                season_type=season_type,
                year=year
            )
            
            if not scoreboard or "events" not in scoreboard:
                return []
            
            parsed = espn_client.parse_football_games(scoreboard)
            
            games = []
            for g in parsed:
                game = FootballGame(
                    id=g["id"],
                    name=g["name"],
                    short_name=g["short_name"],
                    date=g["date"],
                    week=g["week"],
                    season_type=g["season_type"],
                    home_team=g["home_team"],
                    away_team=g["away_team"],
                    status=g["status"],
                    status_detail=g["status_detail"],
                    period=g["period"],
                    clock=g["clock"],
                    venue=g["venue"],
                    odds=g["odds"],
                    broadcasts=g["broadcasts"],
                    attendance=g["attendance"],
                    neutral_site=g["neutral_site"],
                    conference_competition=g["conference_competition"]
                )
                games.append(game)
            
            return games
            
        except Exception as e:
            print(f"ESPN API error for football games: {e}")
            return []
    
    def get_team_stats(self, team_name: str, league: Optional[str] = None) -> Optional[TeamStats]:
        """
        Get statistics for a specific football team.
        
        Args:
            team_name: Name of the team
            league: Optional league (nfl, college-football, etc.)
            
        Returns:
            TeamStats object or None if team not found
        """
        try:
            league_code = self._normalize_league(league) if league else "nfl"
            
            # Get standings to extract team stats
            standings_data = espn_client.get_football_standings(league=league_code)
            
            if standings_data:
                parsed = espn_client.parse_football_standings(standings_data)
                for standing in parsed:
                    if team_name.lower() in standing["team"].lower():
                        return TeamStats(
                            team_name=standing["team"],
                            played=standing["wins"] + standing["losses"] + standing["ties"],
                            wins=standing["wins"],
                            draws=standing["ties"],
                            losses=standing["losses"],
                            goals_for=standing["points_for"],
                            goals_against=standing["points_against"],
                            goal_difference=standing["point_diff"],
                            points=standing["wins"],  # In NFL, wins matter most
                            form=[],
                            top_scorer=None,
                            top_scorer_goals=None
                        )
            
            return None
            
        except Exception as e:
            print(f"ESPN API error for team stats: {e}")
            return None
    
    def get_league_standings(self, league: str = "NFL", conference: Optional[str] = None) -> List[LeagueStanding]:
        """
        Get league standings from ESPN.
        
        Args:
            league: League name (NFL, college-football, CFL, etc.)
            conference: Optional conference filter (AFC, NFC, SEC, Big Ten, etc.)
            
        Returns:
            List of LeagueStanding objects sorted by position
        """
        try:
            league_code = self._normalize_league(league)
            standings_data = espn_client.get_football_standings(league=league_code)
            
            if not standings_data:
                return []
            
            parsed = espn_client.parse_football_standings(standings_data)
            
            if not parsed:
                return []
            
            standings = []
            for i, s in enumerate(parsed):
                # Apply conference filter if specified
                if conference:
                    conf_lower = conference.lower()
                    standing_conf = s.get("conference", "").lower()
                    if conf_lower not in standing_conf:
                        continue
                
                standing = LeagueStanding(
                    position=s.get("rank", i + 1) or i + 1,
                    team=s["team"],
                    played=s["wins"] + s["losses"] + s["ties"],
                    won=s["wins"],
                    drawn=s["ties"],
                    lost=s["losses"],
                    goals_for=s["points_for"],
                    goals_against=s["points_against"],
                    goal_difference=s["point_diff"],
                    points=s["wins"],  # W-L record matters in NFL
                    form=[]
                )
                standings.append(standing)
            
            # Sort by wins, then by point differential
            standings.sort(key=lambda x: (-x.won, -x.goal_difference))
            
            # Update positions
            for i, standing in enumerate(standings):
                standing.position = i + 1
            
            return standings
            
        except Exception as e:
            print(f"ESPN API error for standings: {e}")
            return []
    
    def get_teams(self, league: str = "NFL") -> List[Dict]:
        """
        Get all teams in a football league.
        
        Args:
            league: League name (NFL, college-football, CFL, etc.)
            
        Returns:
            List of team dictionaries
        """
        try:
            league_code = self._normalize_league(league)
            teams_data = espn_client.get_football_teams(league=league_code)
            
            if not teams_data:
                return []
            
            return espn_client.parse_teams(teams_data)
            
        except Exception as e:
            print(f"ESPN API error for teams: {e}")
            return []
    
    def get_team_roster(self, team_id: str, league: str = "nfl") -> List[Dict]:
        """
        Get team roster.
        
        Args:
            team_id: ESPN team ID
            league: League code
            
        Returns:
            List of player dictionaries
        """
        try:
            league_code = self._normalize_league(league)
            roster_data = espn_client.get_football_team_roster(league_code, team_id)
            
            if not roster_data:
                return []
            
            return espn_client.parse_football_roster(roster_data)
            
        except Exception as e:
            print(f"ESPN API error for roster: {e}")
            return []
    
    def get_team_schedule(self, team_id: str, league: str = "nfl", year: Optional[int] = None) -> Dict:
        """
        Get team schedule.
        
        Args:
            team_id: ESPN team ID
            league: League code
            year: Season year
            
        Returns:
            Raw schedule data from ESPN
        """
        try:
            league_code = self._normalize_league(league)
            return espn_client.get_football_team_schedule(league_code, team_id, year)
        except Exception as e:
            print(f"ESPN API error for schedule: {e}")
            return {}
    
    def search_players(
        self, 
        name: Optional[str] = None,
        team: Optional[str] = None,
        position: Optional[str] = None,
        league: str = "nfl"
    ) -> List[Player]:
        """
        Search for football players.
        
        Args:
            name: Player name (partial match)
            team: Team name
            position: Position (QB, RB, WR, etc.)
            league: League code
            
        Returns:
            List of Player objects
        """
        try:
            if not name and not team:
                return []
            
            league_code = self._normalize_league(league)
            query = name or team or ""
            
            # Use ESPN search or player endpoint
            if name:
                search_result = espn_client.search_football_players(query, league_code)
                if not search_result:
                    # Fallback to general search
                    search_result = espn_client.search(query, limit=20)
            else:
                search_result = espn_client.search(query, limit=20)
            
            if not search_result:
                return []
            
            players = []
            results = search_result.get("results", search_result.get("athletes", []))
            
            # Handle different response formats
            if isinstance(results, list):
                for result in results:
                    if result.get("type") == "athlete" or "displayName" in result:
                        items = result.get("contents", [result])
                        for item in items:
                            player_name = item.get("title", item.get("displayName", ""))
                            player_team = item.get("description", item.get("team", {}).get("displayName", ""))
                            player_pos = item.get("position", {}).get("abbreviation", position or "Unknown")
                            
                            # Apply filters
                            if name and name.lower() not in player_name.lower():
                                continue
                            if team and team.lower() not in player_team.lower():
                                continue
                            if position and position.lower() != player_pos.lower():
                                continue
                            
                            player = Player(
                                id=item.get("uid", item.get("id", f"ESPN-{len(players)}")),
                                name=player_name,
                                team=player_team,
                                position=player_pos,
                                nationality="",
                                age=item.get("age", 0),
                                goals=0,
                                assists=0,
                                appearances=0
                            )
                            players.append(player)
            
            return players
            
        except Exception as e:
            print(f"ESPN API error for player search: {e}")
            return []
    
    def get_news(self, league: str = "NFL", limit: int = 10) -> List[Dict]:
        """
        Get latest football news.
        
        Args:
            league: League name
            limit: Max number of articles
            
        Returns:
            List of news articles
        """
        try:
            league_code = self._normalize_league(league)
            news = espn_client.get_football_news(league_code, limit)
            
            articles = []
            for article in news.get("articles", []):
                articles.append({
                    "headline": article.get("headline", ""),
                    "description": article.get("description", ""),
                    "link": article.get("links", {}).get("web", {}).get("href", ""),
                    "published": article.get("published", ""),
                    "images": [img.get("url") for img in article.get("images", [])]
                })
            
            return articles
            
        except Exception as e:
            print(f"ESPN API error for news: {e}")
            return []
    
    def get_leaders(
        self, 
        league: str = "nfl",
        category: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict:
        """
        Get statistical leaders.
        
        Args:
            league: League code
            category: Stat category (passing, rushing, receiving, defense)
            year: Season year
            
        Returns:
            Leaders data
        """
        try:
            league_code = self._normalize_league(league)
            leaders_data = espn_client.get_football_leaders(
                league=league_code,
                category=category,
                year=year
            )
            return espn_client.parse_football_leaders(leaders_data)
        except Exception as e:
            print(f"ESPN API error for leaders: {e}")
            return {"categories": []}
    
    def get_rankings(self, league: str = "college-football", year: Optional[int] = None) -> Dict:
        """
        Get college football rankings (AP, Coaches, CFP).
        
        Args:
            league: League code (college-football)
            year: Season year
            
        Returns:
            Rankings data
        """
        try:
            return espn_client.get_football_rankings(league, year)
        except Exception as e:
            print(f"ESPN API error for rankings: {e}")
            return {}
    
    def get_game_boxscore(self, game_id: str, league: str = "nfl") -> Dict:
        """
        Get detailed box score for a game.
        
        Args:
            game_id: ESPN game ID
            league: League code
            
        Returns:
            Box score data
        """
        try:
            league_code = self._normalize_league(league)
            boxscore_data = espn_client.get_football_game_boxscore(league_code, game_id)
            return espn_client.parse_football_boxscore(boxscore_data)
        except Exception as e:
            print(f"ESPN API error for boxscore: {e}")
            return {}
    
    def get_game_odds(self, game_id: str, league: str = "nfl") -> Dict:
        """
        Get betting odds for a game.
        
        Args:
            game_id: ESPN game ID
            league: League code
            
        Returns:
            Odds data
        """
        try:
            league_code = self._normalize_league(league)
            return espn_client.get_football_game_odds(league_code, game_id)
        except Exception as e:
            print(f"ESPN API error for odds: {e}")
            return {}
    
    def get_injuries(self, league: str = "nfl", team_id: Optional[str] = None) -> Dict:
        """
        Get injury reports.
        
        Args:
            league: League code
            team_id: Optional team ID for team-specific injuries
            
        Returns:
            Injury report data
        """
        try:
            league_code = self._normalize_league(league)
            if team_id:
                return espn_client.get_football_team_injuries(league_code, team_id)
            return espn_client.get_football_injuries(league_code)
        except Exception as e:
            print(f"ESPN API error for injuries: {e}")
            return {}
    
    def get_draft(self, league: str = "nfl", year: int = 2025) -> Dict:
        """
        Get NFL draft information.
        
        Args:
            league: League code
            year: Draft year
            
        Returns:
            Draft data
        """
        try:
            return espn_client.get_football_draft(league, year)
        except Exception as e:
            print(f"ESPN API error for draft: {e}")
            return {}
    
    def compare_teams(self, team1: str, team2: str, league: str = "nfl") -> Dict:
        """
        Compare two football teams head-to-head.
        
        Args:
            team1: First team name
            team2: Second team name
            league: League code
            
        Returns:
            Comparison data dictionary
        """
        stats1 = self.get_team_stats(team1, league=league)
        stats2 = self.get_team_stats(team2, league=league)
        
        if not stats1 or not stats2:
            return {"error": "One or both teams not found"}
        
        return {
            "team1": stats1.model_dump(),
            "team2": stats2.model_dump(),
            "comparison": {
                "wins_diff": stats1.wins - stats2.wins,
                "point_diff": stats1.goal_difference - stats2.goal_difference,
                "points_for_diff": stats1.goals_for - stats2.goals_for,
            }
        }


# Singleton instance
football_service = FootballDataService()
