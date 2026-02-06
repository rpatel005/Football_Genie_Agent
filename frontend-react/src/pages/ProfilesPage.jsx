import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, User, Search, Filter, Trophy,
  Calendar, MapPin, Star, TrendingUp,
  Award, Target, Clock, ChevronRight, Sparkles, Heart
} from 'lucide-react';
import FootballGenie from '../components/FootballGenie';
import { useApp } from '../context/AppContext';
import './ProfilesPage.css';

const ProfilesPage = () => {
  const { state, dispatch, ActionTypes } = useApp();
  const [activeTab, setActiveTab] = useState('teams');
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedItemType, setSelectedItemType] = useState(null); // 'team' or 'player'
  const [searchQuery, setSearchQuery] = useState('');
  const [genieOpen, setGenieOpen] = useState(false);

  // Helper to select item with type
  const selectTeam = (team) => {
    setSelectedItem(team);
    setSelectedItemType('team');
  };

  const selectPlayer = (player) => {
    setSelectedItem(player);
    setSelectedItemType('player');
  };

  const teams = [
    { id: 1, name: 'Kansas City Chiefs', league: 'NFL', founded: 1960, stadium: 'Arrowhead Stadium', manager: 'Andy Reid', trophies: 4, form: ['W', 'W', 'W', 'W', 'W'] },
    { id: 2, name: 'San Francisco 49ers', league: 'NFL', founded: 1946, stadium: "Levi's Stadium", manager: 'Kyle Shanahan', trophies: 5, form: ['W', 'W', 'L', 'W', 'W'] },
    { id: 3, name: 'Dallas Cowboys', league: 'NFL', founded: 1960, stadium: 'AT&T Stadium', manager: 'Mike McCarthy', trophies: 5, form: ['W', 'L', 'W', 'W', 'D'] },
    { id: 4, name: 'Buffalo Bills', league: 'NFL', founded: 1960, stadium: 'Highmark Stadium', manager: 'Sean McDermott', trophies: 0, form: ['W', 'W', 'W', 'L', 'W'] },
    { id: 5, name: 'Philadelphia Eagles', league: 'NFL', founded: 1933, stadium: 'Lincoln Financial Field', manager: 'Nick Sirianni', trophies: 4, form: ['W', 'W', 'W', 'W', 'L'] },
    { id: 6, name: 'Detroit Lions', league: 'NFL', founded: 1930, stadium: 'Ford Field', manager: 'Dan Campbell', trophies: 4, form: ['W', 'W', 'W', 'W', 'W'] },
    { id: 7, name: 'Baltimore Ravens', league: 'NFL', founded: 1996, stadium: 'M&T Bank Stadium', manager: 'John Harbaugh', trophies: 2, form: ['W', 'L', 'W', 'W', 'W'] },
    { id: 8, name: 'Miami Dolphins', league: 'NFL', founded: 1966, stadium: 'Hard Rock Stadium', manager: 'Mike McDaniel', trophies: 2, form: ['L', 'W', 'W', 'L', 'W'] },
  ];

  const players = [
    { id: 1, name: 'Patrick Mahomes', team: 'Kansas City Chiefs', position: 'QB', age: 29, goals: 41, assists: 4500, rating: 9.5 },
    { id: 2, name: 'Travis Kelce', team: 'Kansas City Chiefs', position: 'TE', age: 35, goals: 93, assists: 984, rating: 9.2 },
    { id: 3, name: 'Josh Allen', team: 'Buffalo Bills', position: 'QB', age: 28, goals: 40, assists: 4306, rating: 9.3 },
    { id: 4, name: 'Tyreek Hill', team: 'Miami Dolphins', position: 'WR', age: 30, goals: 13, assists: 1799, rating: 9.0 },
    { id: 5, name: 'CeeDee Lamb', team: 'Dallas Cowboys', position: 'WR', age: 25, goals: 14, assists: 1749, rating: 8.9 },
    { id: 6, name: 'Lamar Jackson', team: 'Baltimore Ravens', position: 'QB', age: 27, goals: 36, assists: 4172, rating: 9.4 },
    { id: 7, name: 'Jalen Hurts', team: 'Philadelphia Eagles', position: 'QB', age: 26, goals: 38, assists: 3858, rating: 9.1 },
    { id: 8, name: 'Brock Purdy', team: 'San Francisco 49ers', position: 'QB', age: 24, goals: 31, assists: 4280, rating: 9.0 },
  ];

  const getFormColor = (result) => {
    switch (result) {
      case 'W': return '#10b981';
      case 'D': return '#f59e0b';
      case 'L': return '#ef4444';
      default: return '#6b7280';
    }
  };

  // Check if item is in favorites (match by name for cross-source compatibility)
  const isTeamFavorite = (teamName) => (state.favoriteTeams || []).some(
    t => t.name?.toLowerCase() === teamName?.toLowerCase()
  );
  const isPlayerFavorite = (playerName) => (state.favoritePlayers || []).some(
    p => p.name?.toLowerCase() === playerName?.toLowerCase()
  );

  // Toggle favorite handlers
  const toggleTeamFavorite = (e, team) => {
    e.stopPropagation();
    if (isTeamFavorite(team.name)) {
      dispatch({ type: ActionTypes.REMOVE_FAVORITE_TEAM, payload: team });
    } else {
      dispatch({ type: ActionTypes.ADD_FAVORITE_TEAM, payload: team });
    }
  };

  const togglePlayerFavorite = (e, player) => {
    e.stopPropagation();
    if (isPlayerFavorite(player.name)) {
      dispatch({ type: ActionTypes.REMOVE_FAVORITE_PLAYER, payload: player });
    } else {
      dispatch({ type: ActionTypes.ADD_FAVORITE_PLAYER, payload: player });
    }
  };

  const filteredItems = activeTab === 'teams' 
    ? teams.filter(t => t.name.toLowerCase().includes(searchQuery.toLowerCase()))
    : players.filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="profiles-page">
      <motion.main 
        className="main-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="page-header">
          <div>
            <h1>Team & Player Profiles</h1>
            <p>Stats, biographies, and performance records</p>
          </div>
          <div className="search-box">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* Tabs */}
        <div className="profile-tabs">
          <button
            className={`tab-btn ${activeTab === 'teams' ? 'active' : ''}`}
            onClick={() => setActiveTab('teams')}
          >
            <Users size={18} />
            Teams
          </button>
          <button
            className={`tab-btn ${activeTab === 'players' ? 'active' : ''}`}
            onClick={() => setActiveTab('players')}
          >
            <User size={18} />
            Players
          </button>
          <button
            className={`tab-btn favorites-tab ${activeTab === 'favorites' ? 'active' : ''}`}
            onClick={() => setActiveTab('favorites')}
          >
            <Heart size={18} />
            Favorites
            {((state.favoriteTeams || []).length + (state.favoritePlayers || []).length) > 0 && (
              <span className="favorites-count">
                {(state.favoriteTeams || []).length + (state.favoritePlayers || []).length}
              </span>
            )}
          </button>
        </div>

        <div className="profiles-content">
          {/* List */}
          <div className="profiles-list">
            {activeTab === 'favorites' ? (
              /* Favorites Tab Content */
              <>
                {/* Favorite Teams */}
                {(state.favoriteTeams || []).length > 0 && (
                  <div className="favorites-section">
                    <h3 className="favorites-section-title">
                      <Users size={18} />
                      Favorite Teams ({(state.favoriteTeams || []).length})
                    </h3>
                    {(state.favoriteTeams || []).map((team, index) => (
                      <motion.div
                        key={team.id}
                        className={`profile-card ${selectedItem?.id === team.id && selectedItemType === 'team' ? 'selected' : ''}`}
                        onClick={() => selectTeam(team)}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <div className="profile-avatar team">
                          <Trophy size={24} />
                        </div>
                        <div className="profile-info">
                          <h3>{team.name}</h3>
                          <span>{team.league}</span>
                        </div>
                        <div className="profile-stats">
                          <span><Trophy size={14} /> {team.trophies}</span>
                        </div>
                        <button 
                          className="favorite-btn active"
                          onClick={(e) => toggleTeamFavorite(e, team)}
                          title="Remove from favorites"
                        >
                          <Heart size={18} fill="currentColor" />
                        </button>
                        <ChevronRight size={18} className="arrow" />
                      </motion.div>
                    ))}
                  </div>
                )}

                {/* Favorite Players */}
                {(state.favoritePlayers || []).length > 0 && (
                  <div className="favorites-section">
                    <h3 className="favorites-section-title">
                      <User size={18} />
                      Favorite Players ({(state.favoritePlayers || []).length})
                    </h3>
                    {(state.favoritePlayers || []).map((player, index) => (
                      <motion.div
                        key={player.id}
                        className={`profile-card ${selectedItem?.id === player.id && selectedItemType === 'player' ? 'selected' : ''}`}
                        onClick={() => selectPlayer(player)}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <div className="profile-avatar player">
                          <User size={24} />
                        </div>
                        <div className="profile-info">
                          <h3>{player.name}</h3>
                          <span>{player.team} • {player.position}</span>
                        </div>
                        <div className="profile-stats">
                          <span><Target size={14} /> {player.goals}</span>
                          <span><Star size={14} /> {player.rating}</span>
                        </div>
                        <button 
                          className="favorite-btn active"
                          onClick={(e) => togglePlayerFavorite(e, player)}
                          title="Remove from favorites"
                        >
                          <Heart size={18} fill="currentColor" />
                        </button>
                        <ChevronRight size={18} className="arrow" />
                      </motion.div>
                    ))}
                  </div>
                )}

                {/* Empty State */}
                {(state.favoriteTeams || []).length === 0 && (state.favoritePlayers || []).length === 0 && (
                  <div className="favorites-empty">
                    <Heart size={48} />
                    <h3>No Favorites Yet</h3>
                    <p>Click the heart icon on any team or player to add them to your favorites.</p>
                  </div>
                )}
              </>
            ) : activeTab === 'teams' ? (
              teams.filter(t => t.name.toLowerCase().includes(searchQuery.toLowerCase())).map((team, index) => (
                <motion.div
                  key={team.id}
                  className={`profile-card ${selectedItem?.id === team.id && selectedItemType === 'team' ? 'selected' : ''}`}
                  onClick={() => selectTeam(team)}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <div className="profile-avatar team">
                    <Trophy size={24} />
                  </div>
                  <div className="profile-info">
                    <h3>{team.name}</h3>
                    <span>{team.league}</span>
                  </div>
                  <div className="profile-stats">
                    <span><Trophy size={14} /> {team.trophies}</span>
                  </div>
                  <button 
                    className={`favorite-btn ${isTeamFavorite(team.name) ? 'active' : ''}`}
                    onClick={(e) => toggleTeamFavorite(e, team)}
                    title={isTeamFavorite(team.name) ? 'Remove from favorites' : 'Add to favorites'}
                  >
                    <Heart size={18} fill={isTeamFavorite(team.name) ? 'currentColor' : 'none'} />
                  </button>
                  <ChevronRight size={18} className="arrow" />
                </motion.div>
              ))
            ) : (
              players.filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase())).map((player, index) => (
                <motion.div
                  key={player.id}
                  className={`profile-card ${selectedItem?.id === player.id && selectedItemType === 'player' ? 'selected' : ''}`}
                  onClick={() => selectPlayer(player)}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <div className="profile-avatar player">
                    <User size={24} />
                  </div>
                  <div className="profile-info">
                    <h3>{player.name}</h3>
                    <span>{player.team} • {player.position}</span>
                  </div>
                  <div className="profile-stats">
                    <span><Target size={14} /> {player.goals}</span>
                    <span><Star size={14} /> {player.rating}</span>
                  </div>
                  <button 
                    className={`favorite-btn ${isPlayerFavorite(player.name) ? 'active' : ''}`}
                    onClick={(e) => togglePlayerFavorite(e, player)}
                    title={isPlayerFavorite(player.name) ? 'Remove from favorites' : 'Add to favorites'}
                  >
                    <Heart size={18} fill={isPlayerFavorite(player.name) ? 'currentColor' : 'none'} />
                  </button>
                  <ChevronRight size={18} className="arrow" />
                </motion.div>
              ))
            )}
          </div>

          {/* Detail Panel */}
          {selectedItem && (
            <motion.div 
              className="profile-detail"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <div className="detail-header">
                <div className={`detail-avatar ${selectedItemType === 'team' ? 'teams' : 'players'}`}>
                  {selectedItemType === 'team' ? <Trophy size={32} /> : <User size={32} />}
                </div>
                <h2>{selectedItem.name}</h2>
                <span>{selectedItemType === 'team' ? selectedItem.league : `${selectedItem.team} • ${selectedItem.position}`}</span>
                <button 
                  className={`favorite-btn-large ${
                    selectedItemType === 'team' 
                      ? isTeamFavorite(selectedItem.name) ? 'active' : ''
                      : isPlayerFavorite(selectedItem.name) ? 'active' : ''
                  }`}
                  onClick={(e) => selectedItemType === 'team' 
                    ? toggleTeamFavorite(e, selectedItem) 
                    : togglePlayerFavorite(e, selectedItem)
                  }
                >
                  <Heart 
                    size={20} 
                    fill={
                      (selectedItemType === 'team' ? isTeamFavorite(selectedItem.name) : isPlayerFavorite(selectedItem.name)) 
                        ? 'currentColor' 
                        : 'none'
                    } 
                  />
                  {(selectedItemType === 'team' ? isTeamFavorite(selectedItem.name) : isPlayerFavorite(selectedItem.name))
                    ? 'Remove from Favorites'
                    : 'Add to Favorites'}
                </button>
              </div>

              <div className="detail-stats">
                {selectedItemType === 'team' ? (
                  <>
                    <div className="stat-item">
                      <span className="stat-label">Founded</span>
                      <span className="stat-value">{selectedItem.founded}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Stadium</span>
                      <span className="stat-value">{selectedItem.stadium}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Manager</span>
                      <span className="stat-value">{selectedItem.manager}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">League Titles</span>
                      <span className="stat-value highlight">{selectedItem.trophies}</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="stat-item">
                      <span className="stat-label">Age</span>
                      <span className="stat-value">{selectedItem.age}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">TDs</span>
                      <span className="stat-value highlight">{selectedItem.goals}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Yards</span>
                      <span className="stat-value">{selectedItem.assists}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Rating</span>
                      <span className="stat-value highlight">{selectedItem.rating}</span>
                    </div>
                  </>
                )}
              </div>

              {selectedItemType === 'team' && selectedItem.form && (
                <div className="form-guide">
                  <h4>Recent Form</h4>
                  <div className="form-badges">
                    {selectedItem.form.map((result, i) => (
                      <span 
                        key={i} 
                        className="form-badge"
                        style={{ backgroundColor: getFormColor(result) }}
                      >
                        {result}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </div>
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

export default ProfilesPage;
