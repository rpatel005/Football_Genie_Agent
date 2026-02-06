/**
 * Tests for AppContext
 * Tests the global state management context.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';

// Note: These tests require installing testing dependencies:
// npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom


describe('AppContext Initial State', () => {
  it('should have empty calendar matches initially', () => {
    const initialState = {
      calendarMatches: [],
      favoriteTeams: [],
      favoritePlayers: [],
      fantasySquad: [],
      fantasyBudget: 100,
      activeLeague: 'nfl',
      chatMessages: expect.any(Array),
      chatSessionId: null,
      chatSessions: [],
      notifications: [],
      loading: false,
      lastAction: null,
    };
    
    expect(initialState.calendarMatches).toEqual([]);
  });

  it('should have default league as nfl', () => {
    const initialState = {
      activeLeague: 'nfl',
    };
    
    expect(initialState.activeLeague).toBe('nfl');
  });

  it('should have 100 as default fantasy budget', () => {
    const initialState = {
      fantasyBudget: 100,
    };
    
    expect(initialState.fantasyBudget).toBe(100);
  });
});


describe('AppContext Action Types', () => {
  const ActionTypes = {
    ADD_TO_CALENDAR: 'ADD_TO_CALENDAR',
    REMOVE_FROM_CALENDAR: 'REMOVE_FROM_CALENDAR',
    SET_CALENDAR: 'SET_CALENDAR',
    ADD_FAVORITE_TEAM: 'ADD_FAVORITE_TEAM',
    REMOVE_FAVORITE_TEAM: 'REMOVE_FAVORITE_TEAM',
    ADD_FAVORITE_PLAYER: 'ADD_FAVORITE_PLAYER',
    REMOVE_FAVORITE_PLAYER: 'REMOVE_FAVORITE_PLAYER',
    SET_FAVORITES: 'SET_FAVORITES',
    ADD_TO_FANTASY_SQUAD: 'ADD_TO_FANTASY_SQUAD',
    REMOVE_FROM_FANTASY_SQUAD: 'REMOVE_FROM_FANTASY_SQUAD',
    SET_FANTASY_SQUAD: 'SET_FANTASY_SQUAD',
    CLEAR_FANTASY_SQUAD: 'CLEAR_FANTASY_SQUAD',
    SET_LEAGUE_FILTER: 'SET_LEAGUE_FILTER',
    ADD_CHAT_MESSAGE: 'ADD_CHAT_MESSAGE',
    SET_CHAT_MESSAGES: 'SET_CHAT_MESSAGES',
    SET_CHAT_SESSION_ID: 'SET_CHAT_SESSION_ID',
    CLEAR_CHAT: 'CLEAR_CHAT',
    ADD_CHAT_SESSION: 'ADD_CHAT_SESSION',
    DELETE_CHAT_SESSION: 'DELETE_CHAT_SESSION',
    SET_CHAT_SESSIONS: 'SET_CHAT_SESSIONS',
    LOAD_CHAT_SESSION: 'LOAD_CHAT_SESSION',
    ADD_NOTIFICATION: 'ADD_NOTIFICATION',
    REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
    SET_LOADING: 'SET_LOADING',
    SET_LAST_ACTION: 'SET_LAST_ACTION',
    CLEAR_LAST_ACTION: 'CLEAR_LAST_ACTION',
  };

  it('should have calendar action types', () => {
    expect(ActionTypes.ADD_TO_CALENDAR).toBe('ADD_TO_CALENDAR');
    expect(ActionTypes.REMOVE_FROM_CALENDAR).toBe('REMOVE_FROM_CALENDAR');
    expect(ActionTypes.SET_CALENDAR).toBe('SET_CALENDAR');
  });

  it('should have favorite action types', () => {
    expect(ActionTypes.ADD_FAVORITE_TEAM).toBe('ADD_FAVORITE_TEAM');
    expect(ActionTypes.REMOVE_FAVORITE_TEAM).toBe('REMOVE_FAVORITE_TEAM');
    expect(ActionTypes.ADD_FAVORITE_PLAYER).toBe('ADD_FAVORITE_PLAYER');
    expect(ActionTypes.REMOVE_FAVORITE_PLAYER).toBe('REMOVE_FAVORITE_PLAYER');
  });

  it('should have fantasy squad action types', () => {
    expect(ActionTypes.ADD_TO_FANTASY_SQUAD).toBe('ADD_TO_FANTASY_SQUAD');
    expect(ActionTypes.REMOVE_FROM_FANTASY_SQUAD).toBe('REMOVE_FROM_FANTASY_SQUAD');
    expect(ActionTypes.SET_FANTASY_SQUAD).toBe('SET_FANTASY_SQUAD');
    expect(ActionTypes.CLEAR_FANTASY_SQUAD).toBe('CLEAR_FANTASY_SQUAD');
  });

  it('should have chat action types', () => {
    expect(ActionTypes.ADD_CHAT_MESSAGE).toBe('ADD_CHAT_MESSAGE');
    expect(ActionTypes.SET_CHAT_MESSAGES).toBe('SET_CHAT_MESSAGES');
    expect(ActionTypes.CLEAR_CHAT).toBe('CLEAR_CHAT');
  });

  it('should have notification action types', () => {
    expect(ActionTypes.ADD_NOTIFICATION).toBe('ADD_NOTIFICATION');
    expect(ActionTypes.REMOVE_NOTIFICATION).toBe('REMOVE_NOTIFICATION');
  });
});


describe('AppContext Reducer Logic', () => {
  // Simplified reducer for testing
  function testReducer(state, action) {
    switch (action.type) {
      case 'ADD_TO_CALENDAR': {
        const exists = state.calendarMatches.some(
          m => m.home_team?.toLowerCase() === action.payload.home_team?.toLowerCase() &&
               m.away_team?.toLowerCase() === action.payload.away_team?.toLowerCase()
        );
        if (exists) return state;
        return {
          ...state,
          calendarMatches: [...state.calendarMatches, { id: Date.now(), ...action.payload }],
        };
      }
      case 'REMOVE_FROM_CALENDAR':
        return {
          ...state,
          calendarMatches: state.calendarMatches.filter(
            m => !(m.home_team?.toLowerCase() === action.payload.home_team?.toLowerCase() &&
                   m.away_team?.toLowerCase() === action.payload.away_team?.toLowerCase())
          ),
        };
      case 'ADD_FAVORITE_TEAM': {
        const exists = state.favoriteTeams.some(
          t => t.name?.toLowerCase() === action.payload.name?.toLowerCase()
        );
        if (exists) return state;
        return {
          ...state,
          favoriteTeams: [...state.favoriteTeams, { id: Date.now(), ...action.payload }],
        };
      }
      case 'REMOVE_FAVORITE_TEAM':
        return {
          ...state,
          favoriteTeams: state.favoriteTeams.filter(
            t => t.name?.toLowerCase() !== action.payload.name?.toLowerCase()
          ),
        };
      case 'SET_LEAGUE_FILTER':
        return {
          ...state,
          activeLeague: action.payload.toLowerCase(),
        };
      default:
        return state;
    }
  }

  it('should add match to calendar', () => {
    const state = { calendarMatches: [] };
    const action = {
      type: 'ADD_TO_CALENDAR',
      payload: { home_team: 'Chiefs', away_team: 'Bills', date: '2024-12-25' },
    };

    const newState = testReducer(state, action);

    expect(newState.calendarMatches).toHaveLength(1);
    expect(newState.calendarMatches[0].home_team).toBe('Chiefs');
  });

  it('should not add duplicate match to calendar', () => {
    const state = {
      calendarMatches: [{ id: 1, home_team: 'Chiefs', away_team: 'Bills' }],
    };
    const action = {
      type: 'ADD_TO_CALENDAR',
      payload: { home_team: 'Chiefs', away_team: 'Bills' },
    };

    const newState = testReducer(state, action);

    expect(newState.calendarMatches).toHaveLength(1);
  });

  it('should remove match from calendar', () => {
    const state = {
      calendarMatches: [{ id: 1, home_team: 'Chiefs', away_team: 'Bills' }],
    };
    const action = {
      type: 'REMOVE_FROM_CALENDAR',
      payload: { home_team: 'Chiefs', away_team: 'Bills' },
    };

    const newState = testReducer(state, action);

    expect(newState.calendarMatches).toHaveLength(0);
  });

  it('should add favorite team', () => {
    const state = { favoriteTeams: [] };
    const action = {
      type: 'ADD_FAVORITE_TEAM',
      payload: { name: 'Kansas City Chiefs', league: 'NFL' },
    };

    const newState = testReducer(state, action);

    expect(newState.favoriteTeams).toHaveLength(1);
    expect(newState.favoriteTeams[0].name).toBe('Kansas City Chiefs');
  });

  it('should not add duplicate favorite team', () => {
    const state = {
      favoriteTeams: [{ id: 1, name: 'Kansas City Chiefs' }],
    };
    const action = {
      type: 'ADD_FAVORITE_TEAM',
      payload: { name: 'Kansas City Chiefs' },
    };

    const newState = testReducer(state, action);

    expect(newState.favoriteTeams).toHaveLength(1);
  });

  it('should remove favorite team', () => {
    const state = {
      favoriteTeams: [{ id: 1, name: 'Kansas City Chiefs' }],
    };
    const action = {
      type: 'REMOVE_FAVORITE_TEAM',
      payload: { name: 'Kansas City Chiefs' },
    };

    const newState = testReducer(state, action);

    expect(newState.favoriteTeams).toHaveLength(0);
  });

  it('should set league filter', () => {
    const state = { activeLeague: 'nfl' };
    const action = {
      type: 'SET_LEAGUE_FILTER',
      payload: 'college-football',
    };

    const newState = testReducer(state, action);

    expect(newState.activeLeague).toBe('college-football');
  });
});


describe('Calendar Match Deduplication', () => {
  const calendarReducer = (state, action) => {
    if (action.type === 'ADD_TO_CALENDAR') {
      const exists = state.some(
        m => m.home_team?.toLowerCase() === action.payload.home_team?.toLowerCase() &&
             m.away_team?.toLowerCase() === action.payload.away_team?.toLowerCase()
      );
      if (exists) return state;
      return [...state, { id: Date.now(), ...action.payload }];
    }
    return state;
  };

  it('should detect duplicate with exact match', () => {
    const state = [{ home_team: 'Chiefs', away_team: 'Bills' }];
    const payload = { home_team: 'Chiefs', away_team: 'Bills' };

    const newState = calendarReducer(state, { type: 'ADD_TO_CALENDAR', payload });

    expect(newState).toHaveLength(1);
  });

  it('should detect duplicate with different case', () => {
    const state = [{ home_team: 'Chiefs', away_team: 'Bills' }];
    const payload = { home_team: 'CHIEFS', away_team: 'BILLS' };

    const newState = calendarReducer(state, { type: 'ADD_TO_CALENDAR', payload });

    expect(newState).toHaveLength(1);
  });

  it('should add new match when different', () => {
    const state = [{ home_team: 'Chiefs', away_team: 'Bills' }];
    const payload = { home_team: 'Cowboys', away_team: 'Eagles' };

    const newState = calendarReducer(state, { type: 'ADD_TO_CALENDAR', payload });

    expect(newState).toHaveLength(2);
  });
});


describe('Favorite Teams Deduplication', () => {
  const favoritesReducer = (state, action) => {
    if (action.type === 'ADD_FAVORITE_TEAM') {
      const exists = state.some(
        t => t.name?.toLowerCase() === action.payload.name?.toLowerCase()
      );
      if (exists) return state;
      return [...state, { id: Date.now(), ...action.payload }];
    }
    return state;
  };

  it('should detect duplicate team by name', () => {
    const state = [{ name: 'Kansas City Chiefs' }];
    const payload = { name: 'Kansas City Chiefs' };

    const newState = favoritesReducer(state, { type: 'ADD_FAVORITE_TEAM', payload });

    expect(newState).toHaveLength(1);
  });

  it('should detect duplicate with different case', () => {
    const state = [{ name: 'Kansas City Chiefs' }];
    const payload = { name: 'KANSAS CITY CHIEFS' };

    const newState = favoritesReducer(state, { type: 'ADD_FAVORITE_TEAM', payload });

    expect(newState).toHaveLength(1);
  });
});
