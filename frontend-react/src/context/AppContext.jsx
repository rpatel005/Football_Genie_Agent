import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

// Initial state
const initialState = {
  // Calendar/Schedule
  calendarMatches: [],
  
  // Favorites
  favoriteTeams: [],
  favoritePlayers: [],
  
  // Fantasy Squad
  fantasySquad: [],
  fantasyBudget: 100,
  
  // Filters
  activeLeague: 'nfl',
  
  // Chat state
  chatMessages: [
    { 
      id: 1, 
      type: 'assistant', 
      content: "🏈 Welcome to Football Genie! I'm your AI-powered American Football assistant. Ask me about:\n\n• NFL, College Football, CFL, XFL, USFL games\n• Live scores & game updates\n• Team & conference standings\n• Player stats & injury reports\n• College football rankings\n• Betting odds & predictions\n\nHow can I help you today?" 
    }
  ],
  chatSessionId: null,
  chatSessions: [],
  
  // Notifications
  notifications: [],
  
  // Loading states
  loading: false,
  
  // Last action from AI
  lastAction: null,
};

// Action types
const ActionTypes = {
  // Calendar actions
  ADD_TO_CALENDAR: 'ADD_TO_CALENDAR',
  REMOVE_FROM_CALENDAR: 'REMOVE_FROM_CALENDAR',
  SET_CALENDAR: 'SET_CALENDAR',
  
  // Favorites actions
  ADD_FAVORITE_TEAM: 'ADD_FAVORITE_TEAM',
  REMOVE_FAVORITE_TEAM: 'REMOVE_FAVORITE_TEAM',
  ADD_FAVORITE_PLAYER: 'ADD_FAVORITE_PLAYER',
  REMOVE_FAVORITE_PLAYER: 'REMOVE_FAVORITE_PLAYER',
  SET_FAVORITES: 'SET_FAVORITES',
  
  // Fantasy Squad actions
  ADD_TO_FANTASY_SQUAD: 'ADD_TO_FANTASY_SQUAD',
  REMOVE_FROM_FANTASY_SQUAD: 'REMOVE_FROM_FANTASY_SQUAD',
  SET_FANTASY_SQUAD: 'SET_FANTASY_SQUAD',
  CLEAR_FANTASY_SQUAD: 'CLEAR_FANTASY_SQUAD',
  
  // Filter actions
  SET_LEAGUE_FILTER: 'SET_LEAGUE_FILTER',
  
  // Chat actions
  ADD_CHAT_MESSAGE: 'ADD_CHAT_MESSAGE',
  SET_CHAT_MESSAGES: 'SET_CHAT_MESSAGES',
  SET_CHAT_SESSION_ID: 'SET_CHAT_SESSION_ID',
  CLEAR_CHAT: 'CLEAR_CHAT',
  ADD_CHAT_SESSION: 'ADD_CHAT_SESSION',
  DELETE_CHAT_SESSION: 'DELETE_CHAT_SESSION',
  SET_CHAT_SESSIONS: 'SET_CHAT_SESSIONS',
  LOAD_CHAT_SESSION: 'LOAD_CHAT_SESSION',
  
  // Notification actions
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  
  // Loading
  SET_LOADING: 'SET_LOADING',
  
  // AI Action
  SET_LAST_ACTION: 'SET_LAST_ACTION',
  CLEAR_LAST_ACTION: 'CLEAR_LAST_ACTION',
};

// Reducer
function appReducer(state, action) {
  switch (action.type) {
    case ActionTypes.ADD_TO_CALENDAR: {
      const exists = state.calendarMatches.some(
        m => m.home_team?.toLowerCase() === action.payload.home_team?.toLowerCase() &&
             m.away_team?.toLowerCase() === action.payload.away_team?.toLowerCase()
      );
      if (exists) return state;
      
      return {
        ...state,
        calendarMatches: [...state.calendarMatches, {
          id: Date.now(),
          ...action.payload
        }],
        notifications: [...state.notifications, {
          id: Date.now(),
          type: 'success',
          message: `Added ${action.payload.home_team} vs ${action.payload.away_team} to calendar`,
        }]
      };
    }
    
    case ActionTypes.REMOVE_FROM_CALENDAR: {
      return {
        ...state,
        calendarMatches: state.calendarMatches.filter(
          m => !(m.home_team?.toLowerCase() === action.payload.home_team?.toLowerCase() &&
                 m.away_team?.toLowerCase() === action.payload.away_team?.toLowerCase())
        ),
        notifications: [...state.notifications, {
          id: Date.now(),
          type: 'info',
          message: `Removed ${action.payload.home_team} vs ${action.payload.away_team} from calendar`,
        }]
      };
    }
    
    case ActionTypes.SET_CALENDAR:
      return { ...state, calendarMatches: action.payload };
    
    case ActionTypes.ADD_FAVORITE_TEAM: {
      // Match by name (case-insensitive) for cross-source compatibility
      const exists = state.favoriteTeams.some(
        t => t.name?.toLowerCase() === action.payload.name?.toLowerCase()
      );
      if (exists) return state;
      return {
        ...state,
        favoriteTeams: [...state.favoriteTeams, action.payload],
        notifications: [...state.notifications, {
          id: Date.now(),
          type: 'success',
          message: `Added ${action.payload.name} to favorites`,
        }]
      };
    }
    
    case ActionTypes.REMOVE_FAVORITE_TEAM: {
      return {
        ...state,
        // Match by name (case-insensitive) for cross-source compatibility
        favoriteTeams: state.favoriteTeams.filter(
          t => t.name?.toLowerCase() !== action.payload.name?.toLowerCase()
        ),
        notifications: [...state.notifications, {
          id: Date.now(),
          type: 'info',
          message: `Removed ${action.payload.name} from favorites`,
        }]
      };
    }
    
    case ActionTypes.ADD_FAVORITE_PLAYER: {
      // Match by name (case-insensitive) for cross-source compatibility
      const exists = state.favoritePlayers.some(
        p => p.name?.toLowerCase() === action.payload.name?.toLowerCase()
      );
      if (exists) return state;
      return {
        ...state,
        favoritePlayers: [...state.favoritePlayers, action.payload],
        notifications: [...state.notifications, {
          id: Date.now(),
          type: 'success',
          message: `Added ${action.payload.name} to favorites`,
        }]
      };
    }
    
    case ActionTypes.REMOVE_FAVORITE_PLAYER: {
      return {
        ...state,
        // Match by name (case-insensitive) for cross-source compatibility
        favoritePlayers: state.favoritePlayers.filter(
          p => p.name?.toLowerCase() !== action.payload.name?.toLowerCase()
        ),
        notifications: [...state.notifications, {
          id: Date.now(),
          type: 'info',
          message: `Removed ${action.payload.name} from favorites`,
        }]
      };
    }
    
    case ActionTypes.SET_FAVORITES:
      return { 
        ...state, 
        favoriteTeams: action.payload.teams || state.favoriteTeams,
        favoritePlayers: action.payload.players || state.favoritePlayers
      };
    
    case ActionTypes.ADD_TO_FANTASY_SQUAD: {
      const player = action.payload;
      if (state.fantasySquad.length >= 11) return state;
      if (state.fantasyBudget < player.price) return state;
      if (state.fantasySquad.find(p => p.id === player.id)) return state;
      
      return {
        ...state,
        fantasySquad: [...state.fantasySquad, player],
        fantasyBudget: state.fantasyBudget - player.price,
        notifications: [...state.notifications, {
          id: Date.now(),
          type: 'success',
          message: `Added ${player.name} to your squad`,
        }]
      };
    }
    
    case ActionTypes.REMOVE_FROM_FANTASY_SQUAD: {
      const player = state.fantasySquad.find(p => p.id === action.payload.id);
      if (!player) return state;
      
      return {
        ...state,
        fantasySquad: state.fantasySquad.filter(p => p.id !== action.payload.id),
        fantasyBudget: state.fantasyBudget + player.price,
        notifications: [...state.notifications, {
          id: Date.now(),
          type: 'info',
          message: `Removed ${player.name} from your squad`,
        }]
      };
    }
    
    case ActionTypes.SET_FANTASY_SQUAD:
      return { 
        ...state, 
        fantasySquad: action.payload.squad || [],
        fantasyBudget: action.payload.budget ?? 100
      };
    
    case ActionTypes.CLEAR_FANTASY_SQUAD:
      return {
        ...state,
        fantasySquad: [],
        fantasyBudget: 100,
        notifications: [...state.notifications, {
          id: Date.now(),
          type: 'info',
          message: 'Squad cleared',
        }]
      };
    
    case ActionTypes.SET_LEAGUE_FILTER:
      return { 
        ...state, 
        activeLeague: action.payload.league_id || action.payload.league,
        notifications: [...state.notifications, {
          id: Date.now(),
          type: 'info',
          message: `Filtered by ${action.payload.league}`,
        }]
      };
    
    case ActionTypes.ADD_CHAT_MESSAGE:
      return {
        ...state,
        chatMessages: [...state.chatMessages, action.payload]
      };
    
    case ActionTypes.SET_CHAT_MESSAGES:
      return {
        ...state,
        chatMessages: action.payload
      };
    
    case ActionTypes.SET_CHAT_SESSION_ID:
      return {
        ...state,
        chatSessionId: action.payload
      };
    
    case ActionTypes.CLEAR_CHAT:
      return {
        ...state,
        chatMessages: [
          { 
            id: 1, 
            type: 'assistant', 
            content: "🏈 Welcome to Football Genie! I'm your AI-powered American Football assistant. Ask me about:\n\n• NFL, College Football, CFL, XFL, USFL games\n• Live scores & game updates\n• Team & conference standings\n• Player stats & injury reports\n• College football rankings\n• Betting odds & predictions\n\nHow can I help you today?" 
          }
        ],
        chatSessionId: null
      };
    
    case ActionTypes.ADD_CHAT_SESSION:
      // Check if session already exists
      const existingIndex = state.chatSessions.findIndex(s => s.id === action.payload.id);
      if (existingIndex >= 0) {
        // Update existing session
        const updatedSessions = [...state.chatSessions];
        updatedSessions[existingIndex] = { ...updatedSessions[existingIndex], ...action.payload };
        return { ...state, chatSessions: updatedSessions };
      }
      return {
        ...state,
        chatSessions: [action.payload, ...state.chatSessions.slice(0, 9)]
      };
    
    case ActionTypes.DELETE_CHAT_SESSION:
      return {
        ...state,
        chatSessions: state.chatSessions.filter(s => s.id !== action.payload)
      };
    
    case ActionTypes.SET_CHAT_SESSIONS:
      return {
        ...state,
        chatSessions: action.payload
      };
    
    case ActionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [...state.notifications, { id: Date.now(), ...action.payload }]
      };
    
    case ActionTypes.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload)
      };
    
    case ActionTypes.SET_LOADING:
      return { ...state, loading: action.payload };
    
    case ActionTypes.SET_LAST_ACTION:
      return { ...state, lastAction: action.payload };
    
    case ActionTypes.CLEAR_LAST_ACTION:
      return { ...state, lastAction: null };
    
    default:
      return state;
  }
}

// Context
const AppContext = createContext(null);

// Provider component
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Load calendar from backend on mount
  useEffect(() => {
    const loadCalendar = async () => {
      try {
        const response = await fetch('/api/calendar');
        if (response.ok) {
          const data = await response.json();
          dispatch({ type: ActionTypes.SET_CALENDAR, payload: data.matches || [] });
        }
      } catch (error) {
        console.error('Failed to load calendar:', error);
      }
    };
    loadCalendar();
  }, []);

  // Load chat sessions from backend on mount (for sidebar only)
  useEffect(() => {
    const loadChatSessions = async () => {
      try {
        const response = await fetch('/api/chat/sessions');
        if (response.ok) {
          const data = await response.json();
          if (data.sessions && data.sessions.length > 0) {
            dispatch({ type: ActionTypes.SET_CHAT_SESSIONS, payload: data.sessions });
          }
        }
      } catch (error) {
        console.error('Failed to load chat sessions:', error);
      }
    };
    loadChatSessions();
  }, []);

  // Load favorites from localStorage on mount
  useEffect(() => {
    try {
      const savedFavoriteTeams = localStorage.getItem('favoriteTeams');
      const savedFavoritePlayers = localStorage.getItem('favoritePlayers');
      
      if (savedFavoriteTeams || savedFavoritePlayers) {
        dispatch({ 
          type: ActionTypes.SET_FAVORITES, 
          payload: {
            teams: savedFavoriteTeams ? JSON.parse(savedFavoriteTeams) : [],
            players: savedFavoritePlayers ? JSON.parse(savedFavoritePlayers) : []
          }
        });
      }
    } catch (error) {
      console.error('Failed to load favorites from localStorage:', error);
    }
  }, []);

  // Save favorites to localStorage when they change
  useEffect(() => {
    try {
      localStorage.setItem('favoriteTeams', JSON.stringify(state.favoriteTeams || []));
      localStorage.setItem('favoritePlayers', JSON.stringify(state.favoritePlayers || []));
    } catch (error) {
      console.error('Failed to save favorites to localStorage:', error);
    }
  }, [state.favoriteTeams, state.favoritePlayers]);

  // Load fantasy squad from localStorage on mount
  useEffect(() => {
    try {
      const savedFantasySquad = localStorage.getItem('fantasySquad');
      const savedFantasyBudget = localStorage.getItem('fantasyBudget');
      
      if (savedFantasySquad) {
        dispatch({ 
          type: ActionTypes.SET_FANTASY_SQUAD, 
          payload: {
            squad: JSON.parse(savedFantasySquad),
            budget: savedFantasyBudget ? parseFloat(savedFantasyBudget) : 100
          }
        });
      }
    } catch (error) {
      console.error('Failed to load fantasy squad from localStorage:', error);
    }
  }, []);

  // Save fantasy squad to localStorage when it changes
  useEffect(() => {
    try {
      localStorage.setItem('fantasySquad', JSON.stringify(state.fantasySquad || []));
      localStorage.setItem('fantasyBudget', String(state.fantasyBudget ?? 100));
    } catch (error) {
      console.error('Failed to save fantasy squad to localStorage:', error);
    }
  }, [state.fantasySquad, state.fantasyBudget]);

  // Load calendar matches from localStorage on mount
  useEffect(() => {
    try {
      const savedCalendarMatches = localStorage.getItem('calendarMatches');
      
      if (savedCalendarMatches) {
        dispatch({ 
          type: ActionTypes.SET_CALENDAR, 
          payload: JSON.parse(savedCalendarMatches)
        });
      }
    } catch (error) {
      console.error('Failed to load calendar from localStorage:', error);
    }
  }, []);

  // Save calendar matches to localStorage when they change
  useEffect(() => {
    try {
      localStorage.setItem('calendarMatches', JSON.stringify(state.calendarMatches || []));
    } catch (error) {
      console.error('Failed to save calendar to localStorage:', error);
    }
  }, [state.calendarMatches]);

  // Auto-remove notifications after 5 seconds
  useEffect(() => {
    if (state.notifications.length > 0) {
      const timer = setTimeout(() => {
        dispatch({ type: ActionTypes.REMOVE_NOTIFICATION, payload: state.notifications[0].id });
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [state.notifications]);

  return (
    <AppContext.Provider value={{ state, dispatch, ActionTypes }}>
      {children}
    </AppContext.Provider>
  );
}

// Custom hook to use the context
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

// Hook to handle AI actions
export function useAIActions() {
  const { dispatch, ActionTypes } = useApp();
  
  const processAIResponse = useCallback((response) => {
    if (!response) return;
    
    const content = response.response || response;
    
    // Parse action markers from the response
    const actionMatches = content.match(/\[ACTION:(\w+)\]\s*(\{[^}]+\})\s*\[\/ACTION\]/g);
    
    if (actionMatches) {
      actionMatches.forEach(actionStr => {
        const match = actionStr.match(/\[ACTION:(\w+)\]\s*(\{[^}]+\})/);
        if (match) {
          const [, actionType, payloadStr] = match;
          try {
            const payload = JSON.parse(payloadStr);
            
            switch (actionType) {
              case 'ADD_TO_CALENDAR':
                dispatch({ type: ActionTypes.ADD_TO_CALENDAR, payload });
                break;
              case 'REMOVE_FROM_CALENDAR':
                dispatch({ type: ActionTypes.REMOVE_FROM_CALENDAR, payload });
                break;
              case 'NAVIGATE':
                dispatch({ type: ActionTypes.SET_LAST_ACTION, payload: { type: 'NAVIGATE', ...payload } });
                break;
              case 'SET_FILTER':
                dispatch({ type: ActionTypes.SET_LEAGUE_FILTER, payload });
                break;
              default:
                console.log('Unknown action type:', actionType);
            }
          } catch (e) {
            console.error('Failed to parse AI action payload:', e);
          }
        }
      });
    }
  }, [dispatch, ActionTypes]);
  
  return { processAIResponse };
}

// Hook for navigation from AI
export function useAINavigation() {
  const { state, dispatch, ActionTypes } = useApp();
  const navigate = useNavigate();
  const location = useLocation();
  
  useEffect(() => {
    if (state.lastAction?.type === 'NAVIGATE' && state.lastAction.route) {
      const targetRoute = state.lastAction.route;
      if (location.pathname !== targetRoute) {
        navigate(targetRoute);
      }
      dispatch({ type: ActionTypes.CLEAR_LAST_ACTION });
    }
  }, [state.lastAction, navigate, location.pathname, dispatch, ActionTypes]);
}

export { ActionTypes };
