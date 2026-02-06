import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageCircle, Send, X, Minimize2, 
  Sparkles, Loader, User, Bot, Calendar, Navigation, Filter,
  Check, XCircle, CalendarPlus, Trash2, Search, Database,
  Brain, Zap, CheckCircle, AlertCircle, Clock
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { agentAPI } from '../services/api';
import { useApp } from '../context/AppContext';
import './FootballGenie.css';

// Helper to parse and clean action markers from display text
const parseAIResponse = (content) => {
  // Extract actions - handle multiline markers with [\s\S] for any char including newlines
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
      console.error('Failed to parse action:', e);
    }
  }
  
  // Clean the display text (remove action markers)
  const cleanContent = content.replace(/\[ACTION:\w+\][\s\S]*?\{[\s\S]*?\}[\s\S]*?\[\/ACTION\]/g, '').trim();
  
  return { actions, cleanContent };
};

const WELCOME_MESSAGE = { 
  id: 1, 
  type: 'assistant', 
  content: "⚽ Welcome to Football Genie! I'm your AI-powered sports assistant. Ask me about:\n\n• Live scores & match updates\n• Team standings & statistics\n• Player information\n• Sports news & trends\n• Betting odds & predictions\n\nHow can I help you today?" 
};

const FootballGenie = ({ isOpen, onToggle, onNewChat }) => {
  const { state, dispatch, ActionTypes } = useApp();
  const navigate = useNavigate();
  
  // Use local state for messages (current session only)
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [sessionId, setSessionId] = useState(null);
  
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(null);
  const [activitySteps, setActivitySteps] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Helper to add a message to local state (current session only)
  const addMessage = (message) => {
    setMessages(prev => [...prev, message]);
  };
  
  // Helper to update session ID
  const updateSessionId = (newSessionId) => {
    setSessionId(newSessionId);
  };

  // Load a session from sidebar
  const loadSession = (session) => {
    if (session.messages && session.messages.length > 0) {
      setMessages(session.messages);
      setSessionId(session.id);
    }
  };

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Process AI actions and dispatch to global state
  const processActions = (actions, messageId) => {
    actions.forEach(action => {
      switch (action.type) {
        case 'PENDING_APPROVAL':
          // Store the pending approval for user confirmation (add to calendar)
          setPendingApproval({ ...action.payload, actionType: 'add_calendar', messageId });
          break;
        
        case 'PENDING_REMOVAL':
          // Store the pending removal for user confirmation (remove from calendar)
          setPendingApproval({ ...action.payload, actionType: 'remove_calendar', messageId });
          break;
        
        case 'PENDING_FAVORITE_TEAM':
          // Store pending team favorite for confirmation
          setPendingApproval({ ...action.payload, actionType: 'add_favorite_team', messageId });
          break;
        
        case 'PENDING_REMOVE_FAVORITE_TEAM':
          // Store pending team removal for confirmation
          setPendingApproval({ ...action.payload, actionType: 'remove_favorite_team', messageId });
          break;
        
        case 'PENDING_FAVORITE_PLAYER':
          // Store pending player favorite for confirmation
          setPendingApproval({ ...action.payload, actionType: 'add_favorite_player', messageId });
          break;
        
        case 'PENDING_REMOVE_FAVORITE_PLAYER':
          // Store pending player removal for confirmation
          setPendingApproval({ ...action.payload, actionType: 'remove_favorite_player', messageId });
          break;
          
        case 'ADD_TO_CALENDAR':
          dispatch({ type: ActionTypes.ADD_TO_CALENDAR, payload: action.payload });
          // Also persist to backend
          fetch('/api/calendar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action.payload)
          }).catch(err => console.error('Failed to persist calendar:', err));
          // Clear any pending approval
          setPendingApproval(null);
          break;
          
        case 'REMOVE_FROM_CALENDAR':
          dispatch({ type: ActionTypes.REMOVE_FROM_CALENDAR, payload: action.payload });
          // Also remove from backend
          fetch('/api/calendar', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(action.payload)
          }).catch(err => console.error('Failed to remove from calendar:', err));
          // Clear any pending approval
          setPendingApproval(null);
          break;
        
        case 'ADD_FAVORITE_TEAM':
          dispatch({ type: ActionTypes.ADD_FAVORITE_TEAM, payload: action.payload });
          // Clear any pending approval
          setPendingApproval(null);
          break;
        
        case 'REMOVE_FAVORITE_TEAM':
          dispatch({ type: ActionTypes.REMOVE_FAVORITE_TEAM, payload: action.payload });
          // Clear any pending approval
          setPendingApproval(null);
          break;
        
        case 'ADD_FAVORITE_PLAYER':
          dispatch({ type: ActionTypes.ADD_FAVORITE_PLAYER, payload: action.payload });
          // Clear any pending approval
          setPendingApproval(null);
          break;
        
        case 'REMOVE_FAVORITE_PLAYER':
          dispatch({ type: ActionTypes.REMOVE_FAVORITE_PLAYER, payload: action.payload });
          // Clear any pending approval
          setPendingApproval(null);
          break;
          
        case 'NAVIGATE':
          if (action.payload.route) {
            setTimeout(() => navigate(action.payload.route), 500);
          }
          break;
          
        case 'SET_FILTER':
          dispatch({ type: ActionTypes.SET_LEAGUE_FILTER, payload: action.payload });
          break;
          
        default:
          console.log('Unknown action:', action.type);
      }
    });
  };

  // Handle user approval/rejection of pending action
  const handleApproval = async (approved) => {
    if (!pendingApproval) return;
    
    const actionType = pendingApproval.actionType;
    
    // Generate appropriate response text based on action type
    let response;
    let stepMessage;
    let defaultSuccessMessage;
    
    switch (actionType) {
      case 'add_calendar':
        response = approved ? "Yes, add it to my calendar" : "No, don't add it";
        stepMessage = approved ? '📅 Adding to calendar...' : '❌ Cancelling...';
        defaultSuccessMessage = approved ? 'Match added!' : 'Okay, cancelled.';
        break;
      case 'remove_calendar':
        response = approved ? "Yes, remove it from my calendar" : "No, keep it";
        stepMessage = approved ? '🗑️ Removing from calendar...' : '❌ Cancelling...';
        defaultSuccessMessage = approved ? 'Match removed!' : 'Okay, cancelled.';
        break;
      case 'add_favorite_team':
        response = approved ? "Yes, add this team to my favorites" : "No, don't add it";
        stepMessage = approved ? '⭐ Adding team to favorites...' : '❌ Cancelling...';
        defaultSuccessMessage = approved ? 'Team added to favorites!' : 'Okay, cancelled.';
        break;
      case 'remove_favorite_team':
        response = approved ? "Yes, remove this team from my favorites" : "No, keep it";
        stepMessage = approved ? '🗑️ Removing team from favorites...' : '❌ Cancelling...';
        defaultSuccessMessage = approved ? 'Team removed from favorites!' : 'Okay, cancelled.';
        break;
      case 'add_favorite_player':
        response = approved ? "Yes, add this player to my favorites" : "No, don't add it";
        stepMessage = approved ? '⭐ Adding player to favorites...' : '❌ Cancelling...';
        defaultSuccessMessage = approved ? 'Player added to favorites!' : 'Okay, cancelled.';
        break;
      case 'remove_favorite_player':
        response = approved ? "Yes, remove this player from my favorites" : "No, keep it";
        stepMessage = approved ? '🗑️ Removing player from favorites...' : '❌ Cancelling...';
        defaultSuccessMessage = approved ? 'Player removed from favorites!' : 'Okay, cancelled.';
        break;
      default:
        response = approved ? "Yes" : "No";
        stepMessage = approved ? '⏳ Processing...' : '❌ Cancelling...';
        defaultSuccessMessage = 'Done!';
    }
    
    // Add user's response to messages
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: response
    };
    addMessage(userMessage);
    
    // Build activity steps
    let allSteps = [
      { step: 'processing', status: 'in_progress', message: stepMessage }
    ];
    setActivitySteps([...allSteps]);
    
    // Clear pending approval
    const pendingData = { ...pendingApproval };
    setPendingApproval(null);
    
    // Send to AI to process the confirmation/rejection
    setIsLoading(true);
    try {
      const aiResponse = await agentAPI.chat(response, sessionId);
      
      // Mark step as completed
      allSteps = allSteps.map(s => ({ ...s, status: 'completed' }));
      setActivitySteps([...allSteps]);
      
      const rawContent = aiResponse.response || defaultSuccessMessage;
      const { actions, cleanContent } = parseAIResponse(rawContent);
      
      if (actions.length > 0) {
        processActions(actions);
      }
      
      // Store activity steps with the message
      const finalSteps = allSteps.map(s => ({ ...s, status: 'completed' }));
      
      addMessage({
        id: Date.now() + 1,
        type: 'assistant',
        content: cleanContent,
        actions: actions,
        activitySteps: finalSteps
      });
    } catch (error) {
      console.error('Approval error:', error);
      addMessage({
        id: Date.now() + 1,
        type: 'assistant',
        content: approved ? '❌ Failed to complete action. Please try again.' : 'Okay, I won\'t make any changes.',
        activitySteps: [{ step: 'error', status: 'failed', message: '❌ Action failed' }]
      });
    } finally {
      setIsLoading(false);
      setActivitySteps([]);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input.trim()
    };

    addMessage(userMessage);
    setInput('');
    setIsLoading(true);
    
    // Show initial "Analyzing" step with spinner
    setActivitySteps([
      { step: 'analyzing', status: 'in_progress', message: '🧠 Analyzing your request...' }
    ]);

    try {
      const response = await agentAPI.chat(userMessage.content, sessionId);
      
      // Build all activity steps progressively
      const backendSteps = response.activity_steps || [];
      let allSteps = [
        { step: 'analyzing', status: 'completed', message: '🧠 Analyzing your request...' }
      ];
      
      // First, mark analyzing as completed
      setActivitySteps([...allSteps]);
      
      // Then progressively add each step from backend with delays
      if (backendSteps.length > 0) {
        for (let i = 0; i < backendSteps.length; i++) {
          await new Promise(resolve => setTimeout(resolve, 300)); // Small delay between steps
          
          const step = backendSteps[i];
          if (step.step !== 'thinking') {
            // Add step as in_progress first
            allSteps = [...allSteps, { ...step, status: 'in_progress' }];
            setActivitySteps([...allSteps]);
            
            // After a short delay, mark it as completed
            await new Promise(resolve => setTimeout(resolve, 400));
            allSteps = allSteps.map((s, idx) => 
              idx === allSteps.length - 1 ? { ...s, status: 'completed' } : s
            );
            setActivitySteps([...allSteps]);
          }
        }
      }
      
      // Add a "Creating response" step
      allSteps = [...allSteps, { step: 'response', status: 'in_progress', message: '✍️ Creating response...' }];
      setActivitySteps([...allSteps]);
      await new Promise(resolve => setTimeout(resolve, 300));
      allSteps = allSteps.map((s, idx) => 
        idx === allSteps.length - 1 ? { ...s, status: 'completed' } : s
      );
      setActivitySteps([...allSteps]);
      
      if (response.session_id) {
        updateSessionId(response.session_id);
      }

      const rawContent = response.response;


      // Parse actions from response
      const { actions, cleanContent } = parseAIResponse(rawContent);
      
      // Check if this message requires approval
      const requiresApproval = actions.some(a => a.type === 'PENDING_APPROVAL' || a.type === 'PENDING_REMOVAL');

      // Store the final activity steps with the message (all marked as completed)
      const finalSteps = allSteps.map(s => ({ ...s, status: 'completed' }));

      const messageId = Date.now() + 1;
      const assistantMessage = {
        id: messageId,
        type: 'assistant',
        content: cleanContent,
        actions: actions, // Store actions for rendering action badges
        activitySteps: finalSteps, // Store activity steps with this message
        requiresApproval: requiresApproval // Flag for showing inline buttons
      };

      addMessage(assistantMessage);
      
      // Process any UI actions (pass message ID for pending approvals)
      if (actions.length > 0) {
        processActions(actions, messageId);
      }
      
      // Clear current activity steps (they're now stored with the message)
      setActivitySteps([]);
      
      // Save chat session to sidebar
      const chatSession = {
        id: response.session_id || sessionId || `session-${Date.now()}`,
        title: userMessage.content.slice(0, 35) + (userMessage.content.length > 35 ? '...' : ''),
        preview: cleanContent.slice(0, 50) + (cleanContent.length > 50 ? '...' : ''),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        messages: [...messages, userMessage, assistantMessage]
      };
      
      dispatch({ type: ActionTypes.ADD_CHAT_SESSION, payload: chatSession });
      
      // Persist session to backend
      fetch('/api/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(chatSession)
      }).catch(err => console.error('Failed to persist chat session:', err));
      
    } catch (error) {
      console.error('Chat error:', error);
      setActivitySteps(prev => [
        ...prev.map(s => ({ ...s, status: 'completed' })),
        { step: 'error', status: 'failed', message: '❌ Request failed' }
      ]);
      addMessage({
        id: Date.now() + 1,
        type: 'assistant',
        content: '❌ Sorry, I encountered an error. Please check if the backend is running and try again.'
      });
    } finally {
      setIsLoading(false);
      // Keep activity steps visible - don't clear them
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickQuestions = [
    "Show me today's Premier League matches",
    "Add Arsenal vs Chelsea to my calendar",
    "Take me to the match schedule",
    "Latest football news"
  ];

  return (
    <>
      {/* Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="genie-panel"
            initial={{ opacity: 0, y: 100, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 100, scale: 0.8 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            {/* Header */}
            <div className="genie-header">
              <div className="genie-title">
                <Sparkles className="sparkle-icon" />
                <span>Football Genie</span>
              </div>
              <div className="genie-actions">
                <button onClick={onToggle} className="action-btn minimize">
                  <Minimize2 size={16} />
                </button>
                <button onClick={onToggle} className="action-btn close">
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="genie-messages">
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  className={`message ${msg.type}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <div className="message-avatar">
                    {msg.type === 'user' ? <User size={16} /> : <Bot size={16} />}
                  </div>
                  <div className="message-content">
                    {/* Show stored activity steps for this message */}
                    {msg.activitySteps && msg.activitySteps.length > 0 && (
                      <div className="message-activity-steps">
                        {msg.activitySteps.map((step, idx) => (
                          <div key={idx} className={`activity-step-inline ${step.status}`}>
                            <span className="step-icon-inline">
                              {step.status === 'completed' && <CheckCircle size={12} />}
                              {step.status === 'in_progress' && <Loader size={12} />}
                              {step.status === 'failed' && <AlertCircle size={12} />}
                            </span>
                            <span className="step-text">{step.message}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {(msg.content || '').split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                    {/* Inline Approval Buttons */}
                    {pendingApproval && pendingApproval.messageId === msg.id && !isLoading && (
                      <div className="inline-approval-buttons">
                        <button 
                          className="inline-approval-btn yes"
                          onClick={() => handleApproval(true)}
                        >
                          <Check size={14} />
                          Yes, {pendingApproval.actionType === 'remove' ? 'Remove' : 'Add'}
                        </button>
                        <button 
                          className="inline-approval-btn no"
                          onClick={() => handleApproval(false)}
                        >
                          <X size={14} />
                          No, Cancel
                        </button>
                      </div>
                    )}
                    {/* Action badges */}
                    {msg.actions && msg.actions.length > 0 && (
                      <div className="action-badges">
                        {msg.actions.map((action, idx) => (
                          <span key={idx} className={`action-badge action-${action.type.toLowerCase()}`}>
                            {action.type === 'ADD_TO_CALENDAR' && <Calendar size={12} />}
                            {action.type === 'NAVIGATE' && <Navigation size={12} />}
                            {action.type === 'SET_FILTER' && <Filter size={12} />}
                            {action.type === 'ADD_TO_CALENDAR' && ' Added to Calendar'}
                            {action.type === 'NAVIGATE' && ` Going to ${action.payload.route}`}
                            {action.type === 'SET_FILTER' && ` Filter: ${action.payload.league}`}
                            {action.type === 'REMOVE_FROM_CALENDAR' && ' Removed from Calendar'}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
              
              {/* Activity Steps - Show during loading (current request) */}
              {activitySteps.length > 0 && (
                <motion.div
                  className="activity-steps"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  {activitySteps.map((step, idx) => (
                    <motion.div 
                      key={`${step.step}-${idx}`} 
                      className={`activity-step ${step.status}`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                    >
                      <div className="step-icon">
                        {step.status === 'completed' && <CheckCircle size={14} />}
                        {step.status === 'in_progress' && <Loader size={14} className="spin" />}
                        {step.status === 'failed' && <AlertCircle size={14} />}
                      </div>
                      <span className="step-message">{step.message}</span>
                    </motion.div>
                  ))}
                </motion.div>
              )}
              
              {isLoading && activitySteps.length === 0 && (
                <motion.div
                  className="message assistant loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div className="message-avatar">
                    <Bot size={16} />
                  </div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Questions */}
            {messages.length <= 1 && (
              <div className="quick-questions">
                {quickQuestions.map((q, i) => (
                  <button
                    key={i}
                    className="quick-btn"
                    onClick={() => {
                      setInput(q);
                      setTimeout(() => handleSend(), 100);
                    }}
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}

            {/* Input */}
            <div className="genie-input-container">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about matches, standings, news..."
                className="genie-input"
                disabled={isLoading}
              />
              <button 
                className="send-btn"
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
              >
                {isLoading ? <Loader className="spin" size={18} /> : <Send size={18} />}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default FootballGenie;
