import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Trophy, Users, Star, DollarSign, 
  TrendingUp, MessageCircle, Heart,
  Plus, Check, X, Search, Sparkles
} from 'lucide-react';
import FootballGenie from '../components/FootballGenie';
import { useApp } from '../context/AppContext';
import './FantasyPage.css';

const FantasyPage = () => {
  const { state, dispatch, ActionTypes } = useApp();
  const [activeTab, setActiveTab] = useState('team');
  const [genieOpen, setGenieOpen] = useState(false);

  // Use global state for squad and budget
  const myTeam = state.fantasySquad || [];
  const budget = state.fantasyBudget ?? 100;

  const positions = ['GK', 'DEF', 'DEF', 'DEF', 'DEF', 'MID', 'MID', 'MID', 'FWD', 'FWD', 'FWD'];
  
  const availablePlayers = [
    { id: 1, name: 'Erling Haaland', team: 'Man City', position: 'FWD', price: 14, points: 156, form: 8.9 },
    { id: 2, name: 'Mohamed Salah', team: 'Liverpool', position: 'FWD', price: 13, points: 142, form: 8.5 },
    { id: 3, name: 'Bukayo Saka', team: 'Arsenal', position: 'MID', price: 10, points: 128, form: 8.2 },
    { id: 4, name: 'Cole Palmer', team: 'Chelsea', position: 'MID', price: 9, points: 134, form: 8.7 },
    { id: 5, name: 'Virgil van Dijk', team: 'Liverpool', position: 'DEF', price: 7, points: 98, form: 7.8 },
    { id: 6, name: 'William Saliba', team: 'Arsenal', position: 'DEF', price: 6, points: 102, form: 7.9 },
    { id: 7, name: 'Alisson', team: 'Liverpool', position: 'GK', price: 6, points: 86, form: 7.5 },
    { id: 8, name: 'Martin Odegaard', team: 'Arsenal', position: 'MID', price: 9, points: 118, form: 8.1 },
  ];

  const rankings = [
    { rank: 1, name: 'FootballKing99', points: 1245, team: 'City Destroyers' },
    { rank: 2, name: 'SoccerPro', points: 1198, team: 'Dream XI' },
    { rank: 3, name: 'GoalMachine', points: 1156, team: 'Premier Squad' },
    { rank: 4, name: 'TacticsMaster', points: 1134, team: 'Fantasy FC' },
    { rank: 5, name: 'WinnerWinner', points: 1089, team: 'Golden Boot' },
  ];

  const discussions = [
    { id: 1, user: 'JohnDoe', message: 'Haaland is a must-have this week!', likes: 24, time: '2h ago' },
    { id: 2, user: 'SarahK', message: 'Anyone considering Palmer over Saka?', likes: 18, time: '4h ago' },
    { id: 3, user: 'MikeB', message: 'Triple captain on Salah for the double gameweek', likes: 32, time: '6h ago' },
  ];

  const addPlayer = (player) => {
    if (myTeam.length >= 11) return;
    if (budget < player.price) return;
    if (myTeam.find(p => p.id === player.id)) return;
    
    dispatch({ type: ActionTypes.ADD_TO_FANTASY_SQUAD, payload: player });
  };

  const removePlayer = (playerId) => {
    const player = myTeam.find(p => p.id === playerId);
    if (player) {
      dispatch({ type: ActionTypes.REMOVE_FROM_FANTASY_SQUAD, payload: player });
    }
  };

  const clearSquad = () => {
    dispatch({ type: ActionTypes.CLEAR_FANTASY_SQUAD });
  };

  const totalPoints = myTeam.reduce((sum, p) => sum + p.points, 0);

  return (
    <div className="fantasy-page">
      <motion.main 
        className="main-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="page-header">
          <div>
            <h1>Fantasy Football League</h1>
            <p>Build your dream team and compete</p>
          </div>
          <div className="budget-display">
            <DollarSign size={18} />
            <span>Budget: <strong>${budget}M</strong></span>
          </div>
        </div>

        {/* Tabs */}
        <div className="fantasy-tabs">
          <button
            className={`tab-btn ${activeTab === 'team' ? 'active' : ''}`}
            onClick={() => setActiveTab('team')}
          >
            <Users size={18} />
            My Team
          </button>
          <button
            className={`tab-btn ${activeTab === 'rankings' ? 'active' : ''}`}
            onClick={() => setActiveTab('rankings')}
          >
            <Trophy size={18} />
            Rankings
          </button>
          <button
            className={`tab-btn ${activeTab === 'discussion' ? 'active' : ''}`}
            onClick={() => setActiveTab('discussion')}
          >
            <MessageCircle size={18} />
            Discussion
          </button>
        </div>

        {activeTab === 'team' && (
          <div className="team-builder">
            {/* Team Summary */}
            <div className="team-summary">
              <div className="team-summary-header">
                <h3>Your Squad ({myTeam.length}/11)</h3>
                {myTeam.length > 0 && (
                  <button className="clear-squad-btn" onClick={clearSquad}>
                    <X size={14} />
                    Clear Squad
                  </button>
                )}
              </div>
              <div className="team-stats">
                <div className="stat">
                  <span className="label">Total Points</span>
                  <span className="value">{totalPoints}</span>
                </div>
                <div className="stat">
                  <span className="label">Remaining Budget</span>
                  <span className="value">${budget}M</span>
                </div>
              </div>
              
              <div className="selected-players">
                {myTeam.map(player => (
                  <div key={player.id} className="selected-player">
                    <span className="pos-badge">{player.position}</span>
                    <span className="name">{player.name}</span>
                    <span className="price">${player.price}M</span>
                    <button onClick={() => removePlayer(player.id)} className="remove-btn">
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Available Players */}
            <div className="available-players">
              <h3>Available Players</h3>
              <div className="players-grid">
                {availablePlayers.map(player => (
                  <motion.div
                    key={player.id}
                    className={`player-card ${myTeam.find(p => p.id === player.id) ? 'selected' : ''}`}
                    whileHover={{ scale: 1.02 }}
                  >
                    <div className="player-header">
                      <span className="position">{player.position}</span>
                      <span className="price">${player.price}M</span>
                    </div>
                    <h4>{player.name}</h4>
                    <span className="team">{player.team}</span>
                    <div className="player-stats">
                      <span><Star size={12} /> {player.form}</span>
                      <span><TrendingUp size={12} /> {player.points} pts</span>
                    </div>
                    <button 
                      className="add-btn"
                      onClick={() => addPlayer(player)}
                      disabled={myTeam.find(p => p.id === player.id) || budget < player.price}
                    >
                      {myTeam.find(p => p.id === player.id) ? <Check size={16} /> : <Plus size={16} />}
                    </button>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'rankings' && (
          <div className="rankings-section">
            <div className="rankings-list">
              {rankings.map((user, index) => (
                <motion.div
                  key={user.rank}
                  className={`ranking-card ${user.rank <= 3 ? 'top-three' : ''}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className={`rank-badge rank-${user.rank}`}>
                    {user.rank <= 3 ? <Trophy size={16} /> : user.rank}
                  </div>
                  <div className="rank-info">
                    <h4>{user.name}</h4>
                    <span>{user.team}</span>
                  </div>
                  <div className="rank-points">
                    <strong>{user.points}</strong>
                    <span>pts</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'discussion' && (
          <div className="discussion-section">
            <div className="discussion-list">
              {discussions.map(post => (
                <div key={post.id} className="discussion-card">
                  <div className="discussion-header">
                    <strong>{post.user}</strong>
                    <span>{post.time}</span>
                  </div>
                  <p>{post.message}</p>
                  <button className="like-btn">
                    <Heart size={14} />
                    <span>{post.likes}</span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.main>

      {/* Football Genie Button */}
      <AnimatePresence>
        {!genieOpen && (
          <motion.button
            className="genie-main-button"
            onClick={() => setGenieOpen(true)}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            <Sparkles className="genie-sparkle" />
            <span>Football Genie</span>
          </motion.button>
        )}
      </AnimatePresence>

      <FootballGenie 
        isOpen={genieOpen} 
        onToggle={() => setGenieOpen(!genieOpen)}
      />
    </div>
  );
};

export default FantasyPage;
