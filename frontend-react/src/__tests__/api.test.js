/**
 * Tests for API Service
 * Tests the API wrapper functions for the Football Genie app.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock the API functions
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Import after mocking
import { agentAPI, footballAPI, FOOTBALL_LEAGUES } from '../services/api';


describe('FOOTBALL_LEAGUES Constants', () => {
  it('should have NFL league', () => {
    expect(FOOTBALL_LEAGUES.NFL).toBe('nfl');
  });

  it('should have college football league', () => {
    expect(FOOTBALL_LEAGUES.COLLEGE_FOOTBALL).toBe('college-football');
  });

  it('should have CFL league', () => {
    expect(FOOTBALL_LEAGUES.CFL).toBe('cfl');
  });

  it('should have XFL league', () => {
    expect(FOOTBALL_LEAGUES.XFL).toBe('xfl');
  });

  it('should have USFL league', () => {
    expect(FOOTBALL_LEAGUES.USFL).toBe('usfl');
  });
});


describe('agentAPI', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe('chat', () => {
    it('should send message to chat endpoint', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ session_id: 'test-123', response: 'Hello!' }),
      });

      const result = await agentAPI.chat('Hello');

      expect(mockFetch).toHaveBeenCalledWith(
        '/api/agent/chat',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
      expect(result.session_id).toBe('test-123');
    });

    it('should include session_id when provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ session_id: 'existing-123', response: 'Hi!' }),
      });

      await agentAPI.chat('Hello', 'existing-123');

      const callBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(callBody.session_id).toBe('existing-123');
    });

    it('should throw error on failure', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false });

      await expect(agentAPI.chat('Hello')).rejects.toThrow('Failed to send message');
    });
  });

  describe('getTools', () => {
    it('should fetch available tools', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ tools: [], count: 0 }),
      });

      const result = await agentAPI.getTools();

      expect(mockFetch).toHaveBeenCalledWith('/api/tools');
      expect(result.tools).toBeDefined();
    });

    it('should throw error on failure', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false });

      await expect(agentAPI.getTools()).rejects.toThrow('Failed to get tools');
    });
  });

  describe('getHealth', () => {
    it('should check API health', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ status: 'healthy' }),
      });

      const result = await agentAPI.getHealth();

      expect(mockFetch).toHaveBeenCalledWith('/api/health');
      expect(result.status).toBe('healthy');
    });

    it('should throw error on failure', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false });

      await expect(agentAPI.getHealth()).rejects.toThrow('Health check failed');
    });
  });
});


describe('footballAPI', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe('getGames', () => {
    it('should fetch games with default parameters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ games: [] }),
      });

      await footballAPI.getGames();

      expect(mockFetch).toHaveBeenCalled();
      const url = mockFetch.mock.calls[0][0];
      expect(url).toContain('/api/football/games');
    });

    it('should include league parameter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ games: [] }),
      });

      await footballAPI.getGames('college-football');

      const url = mockFetch.mock.calls[0][0];
      expect(url).toContain('league=college-football');
    });

    it('should include date parameter when provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ games: [] }),
      });

      await footballAPI.getGames('nfl', '2024-12-25');

      const url = mockFetch.mock.calls[0][0];
      expect(url).toContain('date=2024-12-25');
    });

    it('should include week parameter when provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ games: [] }),
      });

      await footballAPI.getGames('nfl', null, 1);

      const url = mockFetch.mock.calls[0][0];
      expect(url).toContain('week=1');
    });

    it('should throw error on failure', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false });

      await expect(footballAPI.getGames()).rejects.toThrow('Failed to fetch games');
    });
  });

  describe('getStandings', () => {
    it('should fetch standings with league parameter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ standings: [] }),
      });

      await footballAPI.getStandings('nfl');

      const url = mockFetch.mock.calls[0][0];
      expect(url).toContain('/api/football/standings');
      expect(url).toContain('league=nfl');
    });

    it('should include conference parameter when provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ standings: [] }),
      });

      await footballAPI.getStandings('nfl', 'AFC');

      const url = mockFetch.mock.calls[0][0];
      expect(url).toContain('conference=AFC');
    });

    it('should throw error on failure', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false });

      await expect(footballAPI.getStandings()).rejects.toThrow('Failed to fetch standings');
    });
  });

  describe('getTeams', () => {
    it('should fetch teams with league parameter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ teams: [] }),
      });

      await footballAPI.getTeams('nfl');

      const url = mockFetch.mock.calls[0][0];
      expect(url).toContain('/api/football/teams');
      expect(url).toContain('league=nfl');
    });

    it('should throw error on failure', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false });

      await expect(footballAPI.getTeams()).rejects.toThrow('Failed to fetch teams');
    });
  });

  describe('getNews', () => {
    it('should fetch news with league parameter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ articles: [] }),
      });

      await footballAPI.getNews('nfl');

      const url = mockFetch.mock.calls[0][0];
      expect(url).toContain('/api/football/news');
      expect(url).toContain('league=nfl');
    });

    it('should include limit parameter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ articles: [] }),
      });

      await footballAPI.getNews('nfl', 5);

      const url = mockFetch.mock.calls[0][0];
      expect(url).toContain('limit=5');
    });

    it('should throw error on failure', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false });

      await expect(footballAPI.getNews()).rejects.toThrow('Failed to fetch news');
    });
  });

  describe('getLeaders', () => {
    it('should fetch statistical leaders', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ leaders: [] }),
      });

      await footballAPI.getLeaders('nfl', 'passing');

      const url = mockFetch.mock.calls[0][0];
      expect(url).toContain('/api/football/leaders');
      expect(url).toContain('category=passing');
    });

    it('should throw error on failure', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false });

      await expect(footballAPI.getLeaders()).rejects.toThrow('Failed to fetch leaders');
    });
  });

  describe('getGameDetails', () => {
    it('should fetch single game details', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ game: {} }),
      });

      await footballAPI.getGameDetails('game-123', 'nfl');

      const url = mockFetch.mock.calls[0][0];
      expect(url).toContain('/api/football/game/game-123');
    });

    it('should throw error on failure', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false });

      await expect(footballAPI.getGameDetails('123')).rejects.toThrow('Failed to fetch game details');
    });
  });
});
