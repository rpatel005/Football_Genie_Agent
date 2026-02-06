// API Service for Football Genie - American Football Only
const API_BASE = '/api';

// Football league constants
export const FOOTBALL_LEAGUES = {
  NFL: 'nfl',
  COLLEGE_FOOTBALL: 'college-football',
  CFL: 'cfl',
  XFL: 'xfl',
  USFL: 'usfl'
};

// ============ Agent API ============
export const agentAPI = {
  async chat(message, sessionId = null) {
    const response = await fetch(`${API_BASE}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    if (!response.ok) throw new Error('Failed to send message');
    return response.json();
  },

  async getTools() {
    const response = await fetch(`${API_BASE}/tools`);
    if (!response.ok) throw new Error('Failed to get tools');
    return response.json();
  },

  async getHealth() {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  }
};

// ============ Football Data API ============
export const footballAPI = {
  // Get football games
  async getGames(league = 'nfl', date = null, week = null, status = null) {
    const params = new URLSearchParams();
    if (league) params.append('league', league);
    if (date) params.append('date', date);
    if (week) params.append('week', week);
    if (status) params.append('status', status);
    
    const response = await fetch(`${API_BASE}/football/games?${params}`);
    if (!response.ok) throw new Error('Failed to fetch games');
    return response.json();
  },

  // Get single game details
  async getGameDetails(gameId, league = 'nfl') {
    const response = await fetch(`${API_BASE}/football/game/${gameId}?league=${league}`);
    if (!response.ok) throw new Error('Failed to fetch game details');
    return response.json();
  },

  // Get standings
  async getStandings(league = 'nfl', conference = null, group = null) {
    const params = new URLSearchParams();
    params.append('league', league);
    if (conference) params.append('conference', conference);
    if (group) params.append('group', group);
    
    const response = await fetch(`${API_BASE}/football/standings?${params}`);
    if (!response.ok) throw new Error('Failed to fetch standings');
    return response.json();
  },

  // Get teams
  async getTeams(league = 'nfl') {
    const response = await fetch(`${API_BASE}/football/teams?league=${league}`);
    if (!response.ok) throw new Error('Failed to fetch teams');
    return response.json();
  },

  // Get news
  async getNews(league = 'nfl', limit = 10) {
    const response = await fetch(`${API_BASE}/football/news?league=${league}&limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch news');
    return response.json();
  },

  // Get statistical leaders
  async getLeaders(league = 'nfl', category = 'passing', season = null) {
    const params = new URLSearchParams();
    params.append('league', league);
    params.append('category', category);
    if (season) params.append('season', season);
    
    const response = await fetch(`${API_BASE}/football/leaders?${params}`);
    if (!response.ok) throw new Error('Failed to fetch leaders');
    return response.json();
  },

  // Get college football rankings
  async getRankings(poll = 'ap') {
    const response = await fetch(`${API_BASE}/football/rankings?poll=${poll}`);
    if (!response.ok) throw new Error('Failed to fetch rankings');
    return response.json();
  },

  // Get injury reports
  async getInjuries(league = 'nfl', team = null) {
    const params = new URLSearchParams();
    params.append('league', league);
    if (team) params.append('team', team);
    
    const response = await fetch(`${API_BASE}/football/injuries?${params}`);
    if (!response.ok) throw new Error('Failed to fetch injuries');
    return response.json();
  },

  // Get betting odds for a game
  async getOdds(gameId, league = 'nfl') {
    const response = await fetch(`${API_BASE}/football/odds/${gameId}?league=${league}`);
    if (!response.ok) throw new Error('Failed to fetch odds');
    return response.json();
  }
};

// Backwards compatibility - alias sportsAPI to footballAPI
export const sportsAPI = {
  // Map old methods to new football methods
  async getMatches(sport = 'football', league = 'nfl', date = null) {
    return footballAPI.getGames(league, date);
  },
  async getStandings(sport = 'football', league = 'nfl') {
    return footballAPI.getStandings(league);
  },
  async getTeams(sport = 'football', league = 'nfl') {
    return footballAPI.getTeams(league);
  },
  async getNews(sport = 'football', league = 'nfl', limit = 10) {
    return footballAPI.getNews(league, limit);
  },
  async getOdds(eventId, competitionId) {
    return footballAPI.getOdds(eventId);
  }
};

// ============ Knowledge API ============
export const knowledgeAPI = {
  async search(query) {
    const response = await fetch(`${API_BASE}/knowledge/search?query=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('Failed to search knowledge');
    return response.json();
  },

  async getFavorites() {
    const response = await fetch(`${API_BASE}/knowledge/favorites`);
    if (!response.ok) throw new Error('Failed to get favorites');
    return response.json();
  }
};

export default { agentAPI, sportsAPI, knowledgeAPI };
