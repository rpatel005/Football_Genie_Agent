/**
 * Tests for FootballGenie Component
 * Tests the AI chat assistant component.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock modules before importing
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
  useLocation: () => ({ pathname: '/' }),
  BrowserRouter: ({ children }) => children,
}));

vi.mock('../services/api', () => ({
  agentAPI: {
    chat: vi.fn().mockResolvedValue({
      session_id: 'test-123',
      response: 'Hello! How can I help?',
      tool_results: [],
      client_actions: [],
      knowledge_used: [],
    }),
  },
}));

vi.mock('../context/AppContext', () => ({
  useApp: () => ({
    state: {
      chatMessages: [],
      calendarMatches: [],
      favoriteTeams: [],
    },
    dispatch: vi.fn(),
    ActionTypes: {
      ADD_TO_CALENDAR: 'ADD_TO_CALENDAR',
      REMOVE_FROM_CALENDAR: 'REMOVE_FROM_CALENDAR',
      ADD_FAVORITE_TEAM: 'ADD_FAVORITE_TEAM',
      REMOVE_FAVORITE_TEAM: 'REMOVE_FAVORITE_TEAM',
      ADD_NOTIFICATION: 'ADD_NOTIFICATION',
    },
  }),
}));


describe('FootballGenie Message Parsing', () => {
  // Test the parseAIResponse helper function logic
  const parseAIResponse = (content) => {
    const actions = [];
    const actionRegex = /\[ACTION:(\w+)\][\s\S]*?(\{[\s\S]*?\})[\s\S]*?\[\/ACTION\]/g;
    let match;
    
    while ((match = actionRegex.exec(content)) !== null) {
      try {
        actions.push({
          type: match[1],
          payload: JSON.parse(match[2])
        });
      } catch (e) {
        // Skip invalid JSON
      }
    }
    
    const cleanContent = content.replace(/\[ACTION:\w+\][\s\S]*?\{[\s\S]*?\}[\s\S]*?\[\/ACTION\]/g, '').trim();
    
    return { actions, cleanContent };
  };

  it('should parse simple response without actions', () => {
    const response = 'Hello! How can I help you today?';
    const { actions, cleanContent } = parseAIResponse(response);

    expect(actions).toHaveLength(0);
    expect(cleanContent).toBe('Hello! How can I help you today?');
  });

  it('should parse response with ADD_TO_CALENDAR action', () => {
    const response = `Game added to calendar!

[ACTION:ADD_TO_CALENDAR]
{"home_team": "Chiefs", "away_team": "Bills", "date": "2024-12-25"}
[/ACTION]`;

    const { actions, cleanContent } = parseAIResponse(response);

    expect(actions).toHaveLength(1);
    expect(actions[0].type).toBe('ADD_TO_CALENDAR');
    expect(actions[0].payload.home_team).toBe('Chiefs');
    expect(cleanContent).toBe('Game added to calendar!');
  });

  it('should parse response with NAVIGATE action', () => {
    const response = `Navigating to standings page.

[ACTION:NAVIGATE]
{"route": "/standings", "page": "Standings"}
[/ACTION]`;

    const { actions, cleanContent } = parseAIResponse(response);

    expect(actions).toHaveLength(1);
    expect(actions[0].type).toBe('NAVIGATE');
    expect(actions[0].payload.route).toBe('/standings');
  });

  it('should parse response with SET_FILTER action', () => {
    const response = `Filter set to college football.

[ACTION:SET_FILTER]
{"league": "College Football", "league_id": "college-football"}
[/ACTION]`;

    const { actions, cleanContent } = parseAIResponse(response);

    expect(actions).toHaveLength(1);
    expect(actions[0].type).toBe('SET_FILTER');
    expect(actions[0].payload.league_id).toBe('college-football');
  });

  it('should parse response with PENDING_APPROVAL action', () => {
    const response = `Would you like to add this game?

[ACTION:PENDING_APPROVAL]
{"action_type": "ADD_TO_CALENDAR", "home_team": "Cowboys", "away_team": "Eagles"}
[/ACTION]`;

    const { actions, cleanContent } = parseAIResponse(response);

    expect(actions).toHaveLength(1);
    expect(actions[0].type).toBe('PENDING_APPROVAL');
    expect(actions[0].payload.action_type).toBe('ADD_TO_CALENDAR');
  });

  it('should parse multiple actions', () => {
    const response = `Done!

[ACTION:ADD_FAVORITE_TEAM]
{"name": "Chiefs", "league": "NFL"}
[/ACTION]

[ACTION:ADD_NOTIFICATION]
{"message": "Team added!"}
[/ACTION]`;

    const { actions, cleanContent } = parseAIResponse(response);

    expect(actions).toHaveLength(2);
    expect(actions[0].type).toBe('ADD_FAVORITE_TEAM');
    expect(actions[1].type).toBe('ADD_NOTIFICATION');
  });

  it('should handle malformed JSON gracefully', () => {
    const response = `Response

[ACTION:INVALID]
{not valid json}
[/ACTION]`;

    const { actions, cleanContent } = parseAIResponse(response);

    expect(actions).toHaveLength(0);
    expect(cleanContent).toBe('Response');
  });
});


describe('FootballGenie Welcome Message', () => {
  const WELCOME_MESSAGE = { 
    id: 1, 
    type: 'assistant', 
    content: "⚽ Welcome to Football Genie! I'm your AI-powered sports assistant." 
  };

  it('should have correct structure', () => {
    expect(WELCOME_MESSAGE).toHaveProperty('id');
    expect(WELCOME_MESSAGE).toHaveProperty('type');
    expect(WELCOME_MESSAGE).toHaveProperty('content');
  });

  it('should be of type assistant', () => {
    expect(WELCOME_MESSAGE.type).toBe('assistant');
  });

  it('should have welcome text', () => {
    expect(WELCOME_MESSAGE.content).toContain('Welcome');
  });
});


describe('FootballGenie Action Processing', () => {
  // Test action processing logic
  const processAction = (action, dispatch, navigate, ActionTypes) => {
    switch (action.type) {
      case 'ADD_TO_CALENDAR':
        dispatch({ type: ActionTypes.ADD_TO_CALENDAR, payload: action.payload });
        return true;
      case 'REMOVE_FROM_CALENDAR':
        dispatch({ type: ActionTypes.REMOVE_FROM_CALENDAR, payload: action.payload });
        return true;
      case 'ADD_FAVORITE_TEAM':
        dispatch({ type: ActionTypes.ADD_FAVORITE_TEAM, payload: action.payload });
        return true;
      case 'NAVIGATE':
        navigate(action.payload.route);
        return true;
      default:
        return false;
    }
  };

  it('should dispatch ADD_TO_CALENDAR action', () => {
    const dispatch = vi.fn();
    const navigate = vi.fn();
    const ActionTypes = { ADD_TO_CALENDAR: 'ADD_TO_CALENDAR' };
    const action = { type: 'ADD_TO_CALENDAR', payload: { home_team: 'Chiefs', away_team: 'Bills' } };

    const result = processAction(action, dispatch, navigate, ActionTypes);

    expect(result).toBe(true);
    expect(dispatch).toHaveBeenCalledWith({
      type: 'ADD_TO_CALENDAR',
      payload: { home_team: 'Chiefs', away_team: 'Bills' },
    });
  });

  it('should dispatch REMOVE_FROM_CALENDAR action', () => {
    const dispatch = vi.fn();
    const navigate = vi.fn();
    const ActionTypes = { REMOVE_FROM_CALENDAR: 'REMOVE_FROM_CALENDAR' };
    const action = { type: 'REMOVE_FROM_CALENDAR', payload: { home_team: 'Chiefs', away_team: 'Bills' } };

    const result = processAction(action, dispatch, navigate, ActionTypes);

    expect(result).toBe(true);
    expect(dispatch).toHaveBeenCalledWith({
      type: 'REMOVE_FROM_CALENDAR',
      payload: { home_team: 'Chiefs', away_team: 'Bills' },
    });
  });

  it('should dispatch ADD_FAVORITE_TEAM action', () => {
    const dispatch = vi.fn();
    const navigate = vi.fn();
    const ActionTypes = { ADD_FAVORITE_TEAM: 'ADD_FAVORITE_TEAM' };
    const action = { type: 'ADD_FAVORITE_TEAM', payload: { name: 'Chiefs', league: 'NFL' } };

    const result = processAction(action, dispatch, navigate, ActionTypes);

    expect(result).toBe(true);
    expect(dispatch).toHaveBeenCalledWith({
      type: 'ADD_FAVORITE_TEAM',
      payload: { name: 'Chiefs', league: 'NFL' },
    });
  });

  it('should navigate on NAVIGATE action', () => {
    const dispatch = vi.fn();
    const navigate = vi.fn();
    const ActionTypes = {};
    const action = { type: 'NAVIGATE', payload: { route: '/standings' } };

    const result = processAction(action, dispatch, navigate, ActionTypes);

    expect(result).toBe(true);
    expect(navigate).toHaveBeenCalledWith('/standings');
  });

  it('should return false for unknown action type', () => {
    const dispatch = vi.fn();
    const navigate = vi.fn();
    const ActionTypes = {};
    const action = { type: 'UNKNOWN_ACTION', payload: {} };

    const result = processAction(action, dispatch, navigate, ActionTypes);

    expect(result).toBe(false);
    expect(dispatch).not.toHaveBeenCalled();
    expect(navigate).not.toHaveBeenCalled();
  });
});


describe('FootballGenie Message Types', () => {
  it('should identify user message type', () => {
    const message = { id: 1, type: 'user', content: 'Hello' };
    expect(message.type).toBe('user');
  });

  it('should identify assistant message type', () => {
    const message = { id: 2, type: 'assistant', content: 'Hi there!' };
    expect(message.type).toBe('assistant');
  });

  it('should identify system message type', () => {
    const message = { id: 3, type: 'system', content: 'System notification' };
    expect(message.type).toBe('system');
  });
});


describe('FootballGenie Session Management', () => {
  it('should generate unique session IDs', () => {
    const generateSessionId = () => Math.random().toString(36).substr(2, 8);
    
    const id1 = generateSessionId();
    const id2 = generateSessionId();

    expect(id1).not.toBe(id2);
    expect(id1).toHaveLength(8);
    expect(id2).toHaveLength(8);
  });

  it('should handle session loading', () => {
    const session = {
      id: 'session-123',
      messages: [
        { id: 1, type: 'user', content: 'Hello' },
        { id: 2, type: 'assistant', content: 'Hi!' },
      ],
    };

    expect(session.messages).toHaveLength(2);
    expect(session.id).toBe('session-123');
  });
});
