"""
LangChain Tools for Football Agent.
Wraps the ESPN-powered data service as LangChain tools.
Supports: NFL, College Football, CFL, XFL, USFL.
"""

import logging
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .football_data import football_service
from .vector_store import vector_store

# Configure logging
logger = logging.getLogger('🏈 FootballTools')


# ============ Tool Input Schemas ============

class FetchMatchesInput(BaseModel):
    """Input for fetching football games."""
    league: Optional[str] = Field("nfl", description="Football league: 'nfl', 'college-football', 'cfl', 'xfl', 'usfl'")
    team: Optional[str] = Field(None, description="Filter by team name (e.g., 'Chiefs', 'Cowboys', 'Alabama')")
    status: Optional[str] = Field(None, description="Filter by game status: 'scheduled', 'live', or 'finished'")
    date: Optional[str] = Field(None, description="Filter by date: 'today', 'tomorrow', 'yesterday', or 'YYYY-MM-DD'")
    week: Optional[int] = Field(None, description="NFL/College football week number (1-18 for NFL regular season)")


class TeamStatsInput(BaseModel):
    """Input for getting team stats."""
    team_name: str = Field(..., description="The name of the football team (e.g., 'Kansas City Chiefs', 'Alabama')")
    league: Optional[str] = Field("nfl", description="League: 'nfl', 'college-football', 'cfl'")


class LeagueStandingsInput(BaseModel):
    """Input for getting league standings."""
    league: str = Field("nfl", description="Football league: 'nfl', 'college-football', 'cfl'")
    conference: Optional[str] = Field(None, description="Conference filter: 'AFC', 'NFC', 'SEC', 'Big Ten', etc.")


class SearchPlayersInput(BaseModel):
    """Input for searching football players."""
    name: Optional[str] = Field(None, description="Player name to search for")
    team: Optional[str] = Field(None, description="Filter by team name")
    position: Optional[str] = Field(None, description="Filter by position: QB, RB, WR, TE, OL, DL, LB, DB, K, P")
    league: Optional[str] = Field("nfl", description="League: 'nfl', 'college-football'")


class SaveFavoriteInput(BaseModel):
    """Input for saving a favorite team."""
    team_name: str = Field(..., description="The name of the team to save as favorite")


class SearchKnowledgeInput(BaseModel):
    """Input for searching knowledge base."""
    query: str = Field(..., description="The search query")


class GetFootballNewsInput(BaseModel):
    """Input for getting football news."""
    league: Optional[str] = Field("nfl", description="League: 'nfl', 'college-football', 'cfl'")
    limit: Optional[int] = Field(5, description="Maximum number of articles to return")


class GetTeamsInput(BaseModel):
    """Input for getting all teams in a league."""
    league: str = Field("nfl", description="Football league: 'nfl', 'college-football', 'cfl'")


class GetLeadersInput(BaseModel):
    """Input for getting statistical leaders."""
    league: str = Field("nfl", description="League: 'nfl', 'college-football'")
    category: Optional[str] = Field(None, description="Stat category: 'passing', 'rushing', 'receiving', 'defense'")


class GetRankingsInput(BaseModel):
    """Input for getting college football rankings."""
    year: Optional[int] = Field(None, description="Season year")


class GetInjuriesInput(BaseModel):
    """Input for getting injury reports."""
    league: str = Field("nfl", description="League: 'nfl', 'college-football'")
    team: Optional[str] = Field(None, description="Optional team name for team-specific injuries")


class AddToCalendarInput(BaseModel):
    """Input for adding a game to the user's personal calendar."""
    home_team: str = Field(..., description="Name of the home team")
    away_team: str = Field(..., description="Name of the away team")
    date: str = Field("TBD", description="Game date in YYYY-MM-DD format or 'TBD' if unknown")
    time: str = Field("TBD", description="Game time (e.g., '20:00') or 'TBD' if unknown")
    league: str = Field("NFL", description="League name")
    venue: str = Field("TBD", description="Stadium/venue name or 'TBD' if unknown")


class RemoveFromCalendarInput(BaseModel):
    """Input for removing a game from the user's personal calendar."""
    home_team: str = Field(..., description="Name of the home team")
    away_team: str = Field(..., description="Name of the away team")


class GetCalendarInput(BaseModel):
    """Input for getting user's calendar games."""
    pass


class NavigateToPageInput(BaseModel):
    """Input for navigating to a page."""
    page: str = Field(..., description="Page to navigate to: 'schedule', 'standings', 'news', 'highlights', 'odds', 'fantasy', 'profiles', 'home'")


class SetLeagueFilterInput(BaseModel):
    """Input for setting the league filter on a page."""
    league: str = Field(..., description="League to filter by: 'nfl', 'college-football', 'cfl'")


class AddFavoriteTeamInput(BaseModel):
    """Input for adding a team to favorites."""
    name: str = Field(..., description="Name of the team (e.g., 'Kansas City Chiefs', 'Dallas Cowboys')")
    league: str = Field("NFL", description="League the team belongs to")


class RemoveFavoriteTeamInput(BaseModel):
    """Input for removing a team from favorites."""
    name: str = Field(..., description="Name of the team to remove")


class AddFavoritePlayerInput(BaseModel):
    """Input for adding a player to favorites."""
    name: str = Field(..., description="Name of the player (e.g., 'Patrick Mahomes', 'Travis Kelce')")
    team: str = Field("", description="Team the player belongs to")
    position: str = Field("", description="Player position (QB, RB, WR, etc.)")


class RemoveFavoritePlayerInput(BaseModel):
    """Input for removing a player from favorites."""
    name: str = Field(..., description="Name of the player to remove")


# ============ LangChain Tools ============

@tool(args_schema=FetchMatchesInput)
def fetch_matches(
    league: Optional[str] = "nfl",
    team: Optional[str] = None,
    status: Optional[str] = None,
    date: Optional[str] = None,
    week: Optional[int] = None
) -> str:
    """
    Fetch football games from ESPN with optional filters.
    Supports: NFL, College Football, CFL, XFL, USFL.
    Use this to get information about upcoming, live, or past games.
    """
    matches = football_service.get_matches(
        league=league or "nfl",
        team=team,
        status=status,
        date=date,
        week=week
    )
    
    if not matches:
        return f"No games found for {league or 'NFL'} with the given filters."
    
    result_lines = [f"Found {len(matches)} games:"]
    for match in matches[:10]:  # Limit to 10 games
        score = ""
        if match.home_score is not None:
            score = f" {match.home_score}-{match.away_score}"
        
        result_lines.append(
            f"- {match.home_team} vs {match.away_team}{score} "
            f"({match.status}) - {match.league} - {match.kickoff_time.strftime('%Y-%m-%d %H:%M')}"
        )
    
    return "\n".join(result_lines)


@tool(args_schema=TeamStatsInput)
def get_team_stats(team_name: str, league: Optional[str] = "nfl") -> str:
    """
    Get detailed statistics for a specific football team.
    Use this when the user asks about a team's record, wins, losses, points, etc.
    """
    stats = football_service.get_team_stats(team_name, league=league)
    
    if not stats:
        return f"Team '{team_name}' not found in {league or 'NFL'}. Try a different team name."
    
    # Check if it's a favorite team
    favorites = vector_store.get_favorite_teams()
    is_favorite = any(team_name.lower() in fav.lower() for fav in favorites)
    favorite_note = " ⭐ (Your favorite team!)" if is_favorite else ""
    
    return f"""
**{stats.team_name}**{favorite_note}

🏈 Season Record:
- Wins: {stats.wins} | Losses: {stats.losses} | Ties: {stats.draws}
- Games Played: {stats.played}
- Points For: {stats.goals_for} | Points Against: {stats.goals_against}
- Point Differential: {'+' if stats.goal_difference >= 0 else ''}{stats.goal_difference}
"""


@tool(args_schema=LeagueStandingsInput)
def get_league_standings(league: str = "nfl", conference: Optional[str] = None) -> str:
    """
    Get the current league standings from ESPN.
    Shows team records, points for/against, and conference standings.
    Supports: NFL, College Football, CFL.
    """
    standings = football_service.get_league_standings(league, conference=conference)
    
    if not standings:
        return f"Could not find standings for '{league}'."
    
    league_display = league.upper() if league == "nfl" else league.title()
    conf_text = f" - {conference}" if conference else ""
    
    result_lines = [f"**{league_display} Standings{conf_text}**\n"]
    result_lines.append("Pos | Team | W | L | T | PF | PA | Diff")
    result_lines.append("-" * 55)
    
    for s in standings[:16]:  # Top 16
        diff = f"+{s.goal_difference}" if s.goal_difference >= 0 else str(s.goal_difference)
        result_lines.append(
            f"{s.position:2} | {s.team[:22]:22} | {s.won:2} | {s.lost:2} | {s.drawn:1} | {s.goals_for:3} | {s.goals_against:3} | {diff:4}"
        )
    
    return "\n".join(result_lines)


@tool(args_schema=SearchPlayersInput)
def search_players(
    name: Optional[str] = None,
    team: Optional[str] = None,
    position: Optional[str] = None,
    league: Optional[str] = "nfl"
) -> str:
    """
    Search for football players by name, team, or position.
    Use this when the user asks about specific players.
    Position codes: QB, RB, WR, TE, OL, DL, LB, DB, K, P
    """
    players = football_service.search_players(
        name=name, 
        team=team, 
        position=position,
        league=league or "nfl"
    )
    
    if not players:
        return "No players found with the given criteria."
    
    result_lines = [f"Found {len(players)} players:"]
    for player in players[:10]:
        result_lines.append(
            f"- {player.name} ({player.team}) - {player.position}"
        )
    
    return "\n".join(result_lines)


@tool(args_schema=SaveFavoriteInput)
def save_favorite_team(team_name: str) -> str:
    """
    Save a team to the user's favorites (legacy - stores in vector store).
    Use add_team_to_favorites instead for UI integration.
    """
    # Check if team exists
    stats = football_service.get_team_stats(team_name)
    if not stats:
        return f"Team '{team_name}' not found. Cannot add to favorites."
    
    # Check if already a favorite
    favorites = vector_store.get_favorite_teams()
    if any(team_name.lower() in fav.lower() for fav in favorites):
        return f"{stats.team_name} is already in your favorites!"
    
    # Add to favorites
    vector_store.add_favorite_team(stats.team_name)
    
    return f"✅ {stats.team_name} has been added to your favorites!"


# In-memory favorites store (synced with frontend)
_favorite_teams: List[Dict[str, Any]] = []
_favorite_players: List[Dict[str, Any]] = []


@tool(args_schema=AddFavoriteTeamInput)
def add_team_to_favorites(name: str, league: str = "NFL") -> str:
    """
    Add a football team to the user's favorites.
    Use this when the user wants to favorite or follow a team.
    This will show a confirmation prompt first.
    """
    global _favorite_teams
    
    # Check if already in favorites
    for team in _favorite_teams:
        if team["name"].lower() == name.lower():
            return f"⚠️ {name} is already in your favorites!"
    
    # Generate a unique ID
    team_id = abs(hash(name.lower())) % 10000
    
    return f"""⭐ **Add Team to Favorites**

I'd like to add the following team to your favorites:

🏈 **{name}**
🏆 League: {league}

**Would you like me to add this team to your favorites?**

[ACTION:PENDING_FAVORITE_TEAM]
{{"action_type": "ADD_FAVORITE_TEAM", "id": {team_id}, "name": "{name}", "league": "{league}"}}
[/ACTION]"""


@tool(args_schema=AddFavoriteTeamInput)
def confirm_add_favorite_team(name: str, league: str = "NFL") -> str:
    """
    Confirm and add a team to favorites after user approval.
    Use this ONLY when the user has explicitly confirmed (said yes/confirm/ok) to add a team.
    """
    global _favorite_teams
    
    # Check if already in favorites
    for team in _favorite_teams:
        if team["name"].lower() == name.lower():
            return f"⚠️ {name} is already in your favorites!"
    
    # Generate a unique ID
    team_id = abs(hash(name.lower())) % 10000
    
    team_entry = {
        "id": team_id,
        "name": name,
        "league": league
    }
    
    _favorite_teams.append(team_entry)
    
    return f"""✅ **Team added to favorites!**

⭐ **{name}** is now in your favorites!
🏆 League: {league}

You now have {len(_favorite_teams)} favorite team(s).

[ACTION:ADD_FAVORITE_TEAM]
{{"id": {team_id}, "name": "{name}", "league": "{league}"}}
[/ACTION]"""


@tool(args_schema=RemoveFavoriteTeamInput)
def remove_team_from_favorites(name: str) -> str:
    """
    Request to remove a team from the user's favorites.
    This will ask for confirmation before removing.
    """
    global _favorite_teams
    
    # Check if team exists in favorites
    found = False
    team_id = abs(hash(name.lower())) % 10000
    for team in _favorite_teams:
        if team["name"].lower() == name.lower():
            found = True
            team_id = team["id"]
            break
    
    return f"""🗑️ **Remove Team from Favorites**

Are you sure you want to remove this team from your favorites?

❌ **{name}**

**Do you want to proceed with removal?**

[ACTION:PENDING_REMOVE_FAVORITE_TEAM]
{{"action_type": "REMOVE_FAVORITE_TEAM", "id": {team_id}, "name": "{name}"}}
[/ACTION]"""


@tool(args_schema=RemoveFavoriteTeamInput)
def confirm_remove_favorite_team(name: str) -> str:
    """
    Confirm and remove a team from favorites after user approval.
    Use this ONLY when the user has explicitly confirmed (said yes/confirm/ok) to remove a team.
    """
    global _favorite_teams
    
    team_id = abs(hash(name.lower())) % 10000
    for i, team in enumerate(_favorite_teams):
        if team["name"].lower() == name.lower():
            team_id = team["id"]
            _favorite_teams.pop(i)
            break
    
    return f"""✅ **Team removed from favorites!**

🗑️ **{name}** has been removed from your favorites.

You now have {len(_favorite_teams)} favorite team(s).

[ACTION:REMOVE_FAVORITE_TEAM]
{{"id": {team_id}, "name": "{name}"}}
[/ACTION]"""


@tool(args_schema=AddFavoritePlayerInput)
def add_player_to_favorites(name: str, team: str = "", position: str = "") -> str:
    """
    Add a football player to the user's favorites.
    Use this when the user wants to favorite or follow a player.
    This will show a confirmation prompt first.
    """
    global _favorite_players
    
    # Check if already in favorites
    for player in _favorite_players:
        if player["name"].lower() == name.lower():
            return f"⚠️ {name} is already in your favorites!"
    
    # Generate a unique ID
    player_id = abs(hash(name.lower())) % 10000
    
    team_info = f"\n🏈 Team: {team}" if team else ""
    position_info = f"\n📍 Position: {position}" if position else ""
    
    return f"""⭐ **Add Player to Favorites**

I'd like to add the following player to your favorites:

👤 **{name}**{team_info}{position_info}

**Would you like me to add this player to your favorites?**

[ACTION:PENDING_FAVORITE_PLAYER]
{{"action_type": "ADD_FAVORITE_PLAYER", "id": {player_id}, "name": "{name}", "team": "{team}", "position": "{position}"}}
[/ACTION]"""


@tool(args_schema=AddFavoritePlayerInput)
def confirm_add_favorite_player(name: str, team: str = "", position: str = "") -> str:
    """
    Confirm and add a player to favorites after user approval.
    Use this ONLY when the user has explicitly confirmed (said yes/confirm/ok) to add a player.
    """
    global _favorite_players
    
    # Check if already in favorites
    for player in _favorite_players:
        if player["name"].lower() == name.lower():
            return f"⚠️ {name} is already in your favorites!"
    
    # Generate a unique ID
    player_id = abs(hash(name.lower())) % 10000
    
    player_entry = {
        "id": player_id,
        "name": name,
        "team": team,
        "position": position
    }
    
    _favorite_players.append(player_entry)
    
    team_info = f"\n🏈 Team: {team}" if team else ""
    position_info = f"\n📍 Position: {position}" if position else ""
    
    return f"""✅ **Player added to favorites!**

⭐ **{name}** is now in your favorites!{team_info}{position_info}

You now have {len(_favorite_players)} favorite player(s).

[ACTION:ADD_FAVORITE_PLAYER]
{{"id": {player_id}, "name": "{name}", "team": "{team}", "position": "{position}"}}
[/ACTION]"""


@tool(args_schema=RemoveFavoritePlayerInput)
def remove_player_from_favorites(name: str) -> str:
    """
    Request to remove a player from the user's favorites.
    This will ask for confirmation before removing.
    """
    global _favorite_players
    
    # Generate ID
    player_id = abs(hash(name.lower())) % 10000
    for player in _favorite_players:
        if player["name"].lower() == name.lower():
            player_id = player["id"]
            break
    
    return f"""🗑️ **Remove Player from Favorites**

Are you sure you want to remove this player from your favorites?

❌ **{name}**

**Do you want to proceed with removal?**

[ACTION:PENDING_REMOVE_FAVORITE_PLAYER]
{{"action_type": "REMOVE_FAVORITE_PLAYER", "id": {player_id}, "name": "{name}"}}
[/ACTION]"""


@tool(args_schema=RemoveFavoritePlayerInput)
def confirm_remove_favorite_player(name: str) -> str:
    """
    Confirm and remove a player from favorites after user approval.
    Use this ONLY when the user has explicitly confirmed (said yes/confirm/ok) to remove a player.
    """
    global _favorite_players
    
    player_id = abs(hash(name.lower())) % 10000
    for i, player in enumerate(_favorite_players):
        if player["name"].lower() == name.lower():
            player_id = player["id"]
            _favorite_players.pop(i)
            break
    
    return f"""✅ **Player removed from favorites!**

🗑️ **{name}** has been removed from your favorites.

You now have {len(_favorite_players)} favorite player(s).

[ACTION:REMOVE_FAVORITE_PLAYER]
{{"id": {player_id}, "name": "{name}"}}
[/ACTION]"""


@tool
def get_favorite_teams() -> str:
    """
    Get all teams in the user's favorites.
    Use this when the user wants to see their favorite teams.
    """
    global _favorite_teams
    
    if not _favorite_teams:
        return "⭐ You don't have any favorite teams yet. Ask me to add a team to your favorites!"
    
    result_lines = [f"⭐ **Your Favorite Teams** ({len(_favorite_teams)}):"]
    for team in _favorite_teams:
        result_lines.append(f"• **{team['name']}** - {team.get('league', 'NFL')}")
    
    return "\n".join(result_lines)


@tool
def get_favorite_players() -> str:
    """
    Get all players in the user's favorites.
    Use this when the user wants to see their favorite players.
    """
    global _favorite_players
    
    if not _favorite_players:
        return "⭐ You don't have any favorite players yet. Ask me to add a player to your favorites!"
    
    result_lines = [f"⭐ **Your Favorite Players** ({len(_favorite_players)}):"]
    for player in _favorite_players:
        team_info = f" ({player['team']})" if player.get('team') else ""
        position_info = f" - {player['position']}" if player.get('position') else ""
        result_lines.append(f"• **{player['name']}**{team_info}{position_info}")
    
    return "\n".join(result_lines)


@tool(args_schema=SearchKnowledgeInput)
def search_knowledge(query: str) -> str:
    """
    Search the knowledge base for relevant information.
    Use this to find stored notes, favorite teams, or facts about football.
    """
    results = vector_store.search(query, n_results=5)
    
    if not results:
        return "No relevant knowledge found."
    
    result_lines = ["Found relevant knowledge:"]
    for doc in results:
        doc_type = doc['metadata'].get('type', 'unknown')
        result_lines.append(f"- [{doc_type}] {doc['content']}")
    
    return "\n".join(result_lines)


@tool(args_schema=GetFootballNewsInput)
def get_football_news(
    league: Optional[str] = "nfl",
    limit: Optional[int] = 5
) -> str:
    """
    Get the latest football news from ESPN.
    Use this when users ask about recent news, updates, or headlines.
    Supports: NFL, College Football, CFL news.
    """
    articles = football_service.get_news(
        league=league or "nfl",
        limit=limit or 5
    )
    
    if not articles:
        return f"No news found for {league or 'NFL'}."
    
    league_display = (league or "NFL").upper() if league == "nfl" else (league or "NFL").title()
    result_lines = [f"📰 Latest {league_display} News:\n"]
    for article in articles:
        headline = article.get("headline", "No headline")
        description = article.get("description", "")[:100]
        result_lines.append(f"• **{headline}**")
        if description:
            result_lines.append(f"  {description}...")
        result_lines.append("")
    
    return "\n".join(result_lines)


@tool(args_schema=GetTeamsInput)
def get_all_teams(league: str = "nfl") -> str:
    """
    Get all teams in a football league from ESPN.
    Use this to list all teams in the NFL, college football, or CFL.
    """
    teams = football_service.get_teams(league=league)
    
    if not teams:
        return f"Could not find teams for '{league}'."
    
    league_display = league.upper() if league == "nfl" else league.title()
    result_lines = [f"**Teams in {league_display}** ({len(teams)} teams):\n"]
    for team in teams:
        name = team.get("name", "Unknown")
        abbr = team.get("abbr", "")
        result_lines.append(f"• {name} ({abbr})")
    
    return "\n".join(result_lines)


@tool(args_schema=GetLeadersInput)
def get_football_leaders(
    league: str = "nfl",
    category: Optional[str] = None
) -> str:
    """
    Get statistical leaders for a football league.
    Categories: passing, rushing, receiving, defense.
    Use this when users ask about top performers or league leaders.
    """
    leaders = football_service.get_leaders(league=league, category=category)
    
    if not leaders or not leaders.get("categories"):
        return f"No leaders data found for {league}."
    
    result_lines = [f"🏆 **{league.upper()} Statistical Leaders**\n"]
    
    for cat in leaders["categories"][:4]:  # Top 4 categories
        cat_name = cat.get("name", "Unknown")
        result_lines.append(f"**{cat_name}:**")
        for leader in cat.get("leaders", [])[:5]:  # Top 5 per category
            name = leader.get("player_name", "Unknown")
            value = leader.get("value", "N/A")
            team = leader.get("team", "")
            result_lines.append(f"  {leader.get('rank', '-')}. {name} ({team}) - {value}")
        result_lines.append("")
    
    return "\n".join(result_lines)


@tool(args_schema=GetRankingsInput)
def get_college_rankings(year: Optional[int] = None) -> str:
    """
    Get college football rankings (AP, Coaches, CFP).
    Use this when users ask about top 25 teams or college football rankings.
    """
    rankings = football_service.get_rankings(league="college-football", year=year)
    
    if not rankings:
        return "No college football rankings found."
    
    result_lines = ["🏈 **College Football Rankings**\n"]
    
    # Parse rankings data
    for poll in rankings.get("rankings", [])[:1]:  # AP Poll
        poll_name = poll.get("name", "Rankings")
        result_lines.append(f"**{poll_name}:**")
        for rank in poll.get("ranks", [])[:25]:
            team = rank.get("team", {})
            name = team.get("nickname", team.get("name", "Unknown"))
            record = rank.get("recordSummary", "")
            result_lines.append(f"  {rank.get('current', '-')}. {name} ({record})")
    
    return "\n".join(result_lines)


@tool(args_schema=GetInjuriesInput)
def get_injuries(league: str = "nfl", team: Optional[str] = None) -> str:
    """
    Get injury reports for a football league or specific team.
    Use this when users ask about injured players or injury updates.
    """
    injuries = football_service.get_injuries(league=league)
    
    if not injuries:
        return f"No injury reports found for {league}."
    
    result_lines = [f"🏥 **{league.upper()} Injury Report**\n"]
    
    # Parse injury data (format varies by ESPN response)
    items = injuries.get("items", injuries.get("injuries", []))
    for item in items[:20]:
        player = item.get("athlete", {}).get("displayName", "Unknown")
        status = item.get("status", "Unknown")
        detail = item.get("details", {}).get("detail", "")
        team_name = item.get("team", {}).get("displayName", "")
        result_lines.append(f"• {player} ({team_name}) - {status}: {detail}")
    
    if len(result_lines) == 1:
        return f"No detailed injury information available for {league}."
    
    return "\n".join(result_lines)


# ============ Calendar/UI Action Tools ============

# In-memory calendar store (in production, use a database)
_user_calendar: List[Dict[str, Any]] = []


@tool(args_schema=AddToCalendarInput)
def add_match_to_calendar(
    home_team: str,
    away_team: str,
    date: str = "TBD",
    time: str = "TBD",
    league: str = "NFL",
    venue: str = "TBD"
) -> str:
    """
    Add a football game to the user's personal calendar.
    Use this when the user wants to track or save a game to their calendar.
    This will show a confirmation prompt to the user before adding.
    """
    global _user_calendar
    
    logger.info(f"📅 ADD_MATCH_TO_CALENDAR called: {home_team} vs {away_team}")
    
    # Handle empty strings as defaults
    date = date if date else "TBD"
    time = time if time else "TBD"
    league = league if league else "NFL"
    venue = venue if venue else "TBD"
    
    # Check if already in calendar
    for match in _user_calendar:
        if match["home_team"].lower() == home_team.lower() and match["away_team"].lower() == away_team.lower():
            logger.info(f"   ⚠️ Already in calendar!")
            return f"⚠️ {home_team} vs {away_team} is already in your calendar!"
    
    logger.info(f"   → Requesting user confirmation...")
    
    # Return pending approval action - don't add yet
    return f"""📋 **Game Details for Calendar**

I'd like to add the following game to your calendar:

🏈 **{home_team} vs {away_team}**
🏆 League: {league}
📅 Date: {date}
⏰ Time: {time}
🏟️ Venue: {venue}

**Would you like me to add this game to your calendar?**

[ACTION:PENDING_APPROVAL]
{{"action_type": "ADD_TO_CALENDAR", "home_team": "{home_team}", "away_team": "{away_team}", "date": "{date}", "time": "{time}", "league": "{league}", "venue": "{venue}"}}
[/ACTION]"""


@tool(args_schema=AddToCalendarInput)
def confirm_add_to_calendar(
    home_team: str,
    away_team: str,
    date: str = "TBD",
    time: str = "TBD",
    league: str = "NFL",
    venue: str = "TBD"
) -> str:
    """
    Confirm and add a game to the calendar after user approval.
    Use this ONLY when the user has explicitly confirmed (said yes/confirm/ok) to add a game.
    """
    global _user_calendar
    
    logger.info(f"✅ CONFIRM_ADD_TO_CALENDAR called: {home_team} vs {away_team}")
    
    # Handle empty strings as defaults
    date = date if date else "TBD"
    time = time if time else "TBD"
    league = league if league else "NFL"
    venue = venue if venue else "TBD"
    
    # Check if already in calendar
    for match in _user_calendar:
        if match["home_team"].lower() == home_team.lower() and match["away_team"].lower() == away_team.lower():
            logger.info(f"   ⚠️ Already in calendar, skipping")
            return f"⚠️ {home_team} vs {away_team} is already in your calendar!"
    
    # Create game entry
    match_entry = {
        "id": len(_user_calendar) + 1,
        "home_team": home_team,
        "away_team": away_team,
        "date": date,
        "time": time,
        "league": league,
        "venue": venue
    }
    
    _user_calendar.append(match_entry)
    logger.info(f"   🎉 ADDED TO CALENDAR! Total games: {len(_user_calendar)}")
    logger.info(f"   → Emitting ADD_TO_CALENDAR action for frontend")
    
    return f"""✅ **Game added to your calendar!**

📅 **{home_team} vs {away_team}**
🏆 League: {league}
📆 Date: {date}
⏰ Time: {time}
🏟️ Venue: {venue}

You now have {len(_user_calendar)} game(s) in your calendar.

[ACTION:ADD_TO_CALENDAR]
{{"home_team": "{home_team}", "away_team": "{away_team}", "date": "{date}", "time": "{time}", "league": "{league}", "venue": "{venue}"}}
[/ACTION]"""


@tool(args_schema=RemoveFromCalendarInput)
def remove_match_from_calendar(home_team: str, away_team: str) -> str:
    """
    Request to remove a game from the user's personal calendar.
    Use this when the user wants to remove a game from their tracked games.
    This will ask for confirmation before removing.
    """
    global _user_calendar
    
    # Check if game exists
    found = False
    for match in _user_calendar:
        if match["home_team"].lower() == home_team.lower() and match["away_team"].lower() == away_team.lower():
            found = True
            break
    
    if not found:
        return f"⚠️ {home_team} vs {away_team} was not found in your calendar."
    
    # Return pending approval action
    return f"""🗑️ **Confirm Removal**

Are you sure you want to remove this game from your calendar?

❌ **{home_team} vs {away_team}**

**Do you want to proceed with removal?**

[ACTION:PENDING_REMOVAL]
{{"action_type": "REMOVE_FROM_CALENDAR", "home_team": "{home_team}", "away_team": "{away_team}"}}
[/ACTION]"""


@tool(args_schema=RemoveFromCalendarInput)
def confirm_remove_from_calendar(home_team: str, away_team: str) -> str:
    """
    Confirm and remove a game from the calendar after user approval.
    Use this ONLY when the user has explicitly confirmed (said yes/confirm/ok) to remove a game.
    """
    global _user_calendar
    
    for i, match in enumerate(_user_calendar):
        if match["home_team"].lower() == home_team.lower() and match["away_team"].lower() == away_team.lower():
            _user_calendar.pop(i)
            return f"""✅ **Game removed from your calendar!**

🗑️ {home_team} vs {away_team} has been removed.

You now have {len(_user_calendar)} game(s) in your calendar.

[ACTION:REMOVE_FROM_CALENDAR]
{{"home_team": "{home_team}", "away_team": "{away_team}"}}
[/ACTION]"""
    
    return f"⚠️ {home_team} vs {away_team} was not found in your calendar."


@tool(args_schema=GetCalendarInput)
def get_calendar_matches() -> str:
    """
    Get all games in the user's personal calendar.
    Use this when the user wants to see their saved/tracked games.
    """
    global _user_calendar
    
    if not _user_calendar:
        return "📅 Your calendar is empty. Ask me to add games to track them!"
    
    result_lines = [f"📅 **Your Calendar** ({len(_user_calendar)} games):\n"]
    for match in _user_calendar:
        result_lines.append(
            f"• **{match['home_team']} vs {match['away_team']}**\n"
            f"  🏟️ {match['league']} | 📆 {match['date']} | ⏰ {match['time']}"
        )
    
    return "\n".join(result_lines)


@tool(args_schema=NavigateToPageInput)
def navigate_to_page(page: str) -> str:
    """
    Navigate to a specific page in the application.
    Use this when the user asks to go to a page or view specific content.
    Available pages: schedule, standings, news, highlights, odds, fantasy, profiles, home
    """
    page_map = {
        "schedule": "/schedule",
        "calendar": "/schedule",
        "standings": "/standings",
        "news": "/news",
        "highlights": "/highlights",
        "odds": "/odds",
        "betting": "/odds",
        "fantasy": "/fantasy",
        "profiles": "/profiles",
        "players": "/profiles",
        "teams": "/profiles",
        "home": "/"
    }
    
    route = page_map.get(page.lower(), "/")
    page_name = page.title()
    
    return f"""🔗 **Navigating to {page_name}**

I'll take you to the {page_name} page now.

[ACTION:NAVIGATE]
{{"route": "{route}", "page": "{page_name}"}}
[/ACTION]"""


@tool(args_schema=SetLeagueFilterInput)
def set_league_filter(league: str) -> str:
    """
    Set the league filter on the current page.
    Use this when the user wants to view data for a specific football league.
    """
    league_ids = {
        "nfl": "nfl",
        "college football": "college-football",
        "college-football": "college-football",
        "ncaaf": "college-football",
        "cfb": "college-football",
        "cfl": "cfl",
        "xfl": "xfl",
        "usfl": "usfl"
    }
    
    league_id = league_ids.get(league.lower(), "nfl")
    league_display = "NFL" if league_id == "nfl" else league.title()
    
    return f"""🏈 **Filter set to {league_display}**

Now showing data for {league_display}.

[ACTION:SET_FILTER]
{{"league": "{league_display}", "league_id": "{league_id}"}}
[/ACTION]"""


def get_user_calendar() -> List[Dict[str, Any]]:
    """Get the current user calendar (for API access)."""
    return _user_calendar.copy()


def clear_user_calendar():
    """Clear the user calendar (for testing)."""
    global _user_calendar
    _user_calendar = []


# List of all available tools
FOOTBALL_TOOLS = [
    fetch_matches,
    get_team_stats,
    get_league_standings,
    search_players,
    save_favorite_team,
    search_knowledge,
    get_football_news,
    get_all_teams,
    get_football_leaders,
    get_college_rankings,
    get_injuries,
    add_match_to_calendar,
    confirm_add_to_calendar,
    remove_match_from_calendar,
    confirm_remove_from_calendar,
    get_calendar_matches,
    navigate_to_page,
    set_league_filter,
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
]

# Tools that require user approval
APPROVAL_REQUIRED_TOOLS = ["save_favorite_team"]


def get_tools_description() -> List[Dict[str, Any]]:
    """Get a formatted description of all available tools."""
    tools_info = []
    for tool in FOOTBALL_TOOLS:
        requires_approval = tool.name in APPROVAL_REQUIRED_TOOLS
        tools_info.append({
            "name": tool.name,
            "description": tool.description,
            "requires_approval": requires_approval
        })
    return tools_info
