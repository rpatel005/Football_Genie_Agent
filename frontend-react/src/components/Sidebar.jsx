import React from 'react';
import { motion } from 'framer-motion';
import { 
  Home, Trophy, Calendar, TrendingUp, 
  MessageCircle, ChevronRight, Clock,
  Newspaper, Users, BarChart2, Video,
  Star, Target, Plus, Trash2
} from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import './Sidebar.css';

const Sidebar = ({ isOpen, activeMenu, onMenuChange }) => {
  const { state, dispatch, ActionTypes } = useApp();
  const chatSessions = state.chatSessions || [];

  const handleSessionClick = (session) => {
    // Load the session's messages into the chat
    if (session.messages) {
      dispatch({ type: ActionTypes.SET_CHAT_MESSAGES, payload: session.messages });
      dispatch({ type: ActionTypes.SET_CHAT_SESSION_ID, payload: session.id });
    }
  };

  const handleNewChat = () => {
    dispatch({ type: ActionTypes.CLEAR_CHAT });
  };

  const handleDeleteSession = (e, sessionId) => {
    e.stopPropagation();
    dispatch({ type: ActionTypes.DELETE_CHAT_SESSION, payload: sessionId });
    // Also delete from backend
    fetch(`/api/chat/history/${sessionId}`, { method: 'DELETE' })
      .catch(err => console.error('Failed to delete session:', err));
  };
  const footballItems = [
    { id: 'home', label: 'Home', icon: Home, path: '/' },
    { id: 'schedule', label: 'Match Schedule & Calendar', icon: Calendar, path: '/schedule' },
    { id: 'profiles', label: 'Team & Player Profiles', icon: Users, path: '/profiles' },
    { id: 'standings', label: 'League Standings', icon: Trophy, path: '/standings' },
  ];

  const fantasyItems = [
    { id: 'fantasy', label: 'Fantasy Football League', icon: Star, path: '/fantasy' },
  ];

  const contentItems = [
    { id: 'news', label: 'News & Articles', icon: Newspaper, path: '/news' },
    { id: 'highlights', label: 'Video Highlights', icon: Video, path: '/highlights' },
  ];

  const bettingItems = [
    { id: 'odds', label: 'Betting Odds', icon: TrendingUp, path: '/odds' },
    { id: 'predictions', label: 'Predictions', icon: Target, path: '/predictions' },
  ];

  return (
    <>
      {isOpen && (
        <aside className="sidebar">
          {/* Chat Sessions */}
          <div className="sidebar-section chat-section">
            <div className="section-header">
              <h3 className="section-title">
                <MessageCircle size={16} />
                <span>Chat Sessions</span>
              </h3>
              <motion.button 
                className="new-chat-btn"
                onClick={handleNewChat}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                title="Start new chat"
              >
                <Plus size={14} />
              </motion.button>
            </div>
            <div className="chat-sessions">
              {chatSessions.length > 0 ? (
                chatSessions.map((session) => (
                  <motion.div
                    key={session.id}
                    className={`chat-session ${state.chatSessionId === session.id ? 'active' : ''}`}
                    whileHover={{ x: 4 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSessionClick(session)}
                  >
                    <div className="session-icon">
                      <MessageCircle size={14} />
                    </div>
                    <div className="session-info">
                      <span className="session-title">{session.title}</span>
                      <span className="session-preview">{session.preview}</span>
                      <span className="session-time">{session.timestamp}</span>
                    </div>
                    <button 
                      className="delete-session-btn"
                      onClick={(e) => handleDeleteSession(e, session.id)}
                      title="Delete session"
                    >
                      <Trash2 size={12} />
                    </button>
                  </motion.div>
                ))
              ) : (
                <div className="no-sessions">
                  <Clock size={20} />
                  <span>No chat history yet</span>
                  <p>Click "Football Genie" to start!</p>
                </div>
              )}
            </div>
          </div>

          {/* Football Navigation */}
          <div className="sidebar-section">
            <h3 className="section-title">
              <Trophy size={16} />
              <span>Football</span>
            </h3>
            <nav className="sidebar-nav">
              {footballItems.map((item) => (
                <NavLink
                  key={item.id}
                  to={item.path}
                  className={({ isActive }) => 
                    `nav-item ${isActive ? 'active' : ''}`
                  }
                  onClick={() => onMenuChange?.(item.id)}
                >
                  <item.icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>
          </div>

          {/* Fantasy League */}
          <div className="sidebar-section">
            <h3 className="section-title">
              <Star size={16} />
              <span>Fantasy League</span>
            </h3>
            <nav className="sidebar-nav">
              {fantasyItems.map((item) => (
                <NavLink
                  key={item.id}
                  to={item.path}
                  className={({ isActive }) => 
                    `nav-item ${isActive ? 'active' : ''}`
                  }
                  onClick={() => onMenuChange?.(item.id)}
                >
                  <item.icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>
          </div>

          {/* Content & Media */}
          <div className="sidebar-section">
            <h3 className="section-title">
              <Video size={16} />
              <span>Content & Media</span>
            </h3>
            <nav className="sidebar-nav">
              {contentItems.map((item) => (
                <NavLink
                  key={item.id}
                  to={item.path}
                  className={({ isActive }) => 
                    `nav-item ${isActive ? 'active' : ''}`
                  }
                  onClick={() => onMenuChange?.(item.id)}
                >
                  <item.icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>
          </div>

          {/* Betting & Odds */}
          <div className="sidebar-section">
            <h3 className="section-title">
              <TrendingUp size={16} />
              <span>Betting & Odds</span>
            </h3>
            <nav className="sidebar-nav">
              {bettingItems.map((item) => (
                <NavLink
                  key={item.id}
                  to={item.path}
                  className={({ isActive }) => 
                    `nav-item ${isActive ? 'active' : ''}`
                  }
                  onClick={() => onMenuChange?.(item.id)}
                >
                  <item.icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>
          </div>

          {/* Footer */}
          <div className="sidebar-footer">
            <span>Powered by ESPN API</span>
          </div>
        </aside>
      )}
    </>
  );
};

export default Sidebar;
