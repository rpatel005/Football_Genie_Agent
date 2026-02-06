import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Calendar, ChevronLeft, ChevronRight, Clock, 
  MapPin, Bell, BellOff, Filter, Search,
  Trophy, Star, Plus, Check, Sparkles, X, RefreshCw
} from 'lucide-react';
import FootballGenie from '../components/FootballGenie';
import { footballAPI } from '../services/api';
import { useApp } from '../context/AppContext';
import './SchedulePage.css';

const SchedulePage = () => {
  const { state, dispatch, ActionTypes } = useApp();
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedLeague, setSelectedLeague] = useState('nfl');
  const [viewMode, setViewMode] = useState('list');
  const [genieOpen, setGenieOpen] = useState(false);
  const [fixtures, setFixtures] = useState([]);
  const [loading, setLoading] = useState(true);

  // Use global calendar from context (with defensive check)
  const calendarMatches = state.calendarMatches || [];

  // Refresh calendar from backend on mount (in case Football Genie added items)
  useEffect(() => {
    const refreshCalendar = async () => {
      try {
        const response = await fetch('/api/calendar');
        if (response.ok) {
          const data = await response.json();
          if (data.matches && data.matches.length > 0) {
            dispatch({ type: ActionTypes.SET_CALENDAR, payload: data.matches });
          }
        }
      } catch (error) {
        console.error('Failed to refresh calendar:', error);
      }
    };
    refreshCalendar();
  }, [dispatch, ActionTypes]);

  const leagues = [
    { id: 'all', name: 'All Leagues' },
    { id: 'nfl', name: 'NFL', flag: '🏈' },
    { id: 'college-football', name: 'College Football', flag: '🎓' },
    { id: 'cfl', name: 'CFL', flag: '🇨🇦' },
    { id: 'xfl', name: 'XFL', flag: '⚡' },
    { id: 'usfl', name: 'USFL', flag: '🇺🇸' },
  ];

  // Fetch fixtures from ESPN API
  useEffect(() => {
    fetchFixtures();
  }, [selectedLeague]);

  const fetchFixtures = async () => {
    setLoading(true);
    try {
      if (selectedLeague === 'all') {
        // Fetch from multiple leagues
        const [nflRes, cfbRes] = await Promise.all([
          footballAPI.getGames('nfl'),
          footballAPI.getGames('college-football')
        ]);
        const nflGames = (nflRes?.games || []).map(g => ({ ...g, league: 'nfl' }));
        const cfbGames = (cfbRes?.games || []).map(g => ({ ...g, league: 'college-football' }));
        setFixtures([...nflGames, ...cfbGames].sort((a, b) => new Date(a.date) - new Date(b.date)));
      } else {
        const response = await footballAPI.getGames(selectedLeague);
        const games = (response?.games || []).map(g => ({ ...g, league: selectedLeague }));
        setFixtures(games);
      }
    } catch (error) {
      console.error('Error fetching fixtures:', error);
      setFixtures([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredFixtures = fixtures;

  // Helper to get team names (handles both API and old format)
  const getHomeTeam = (fixture) => fixture.home_team || fixture.home;
  const getAwayTeam = (fixture) => fixture.away_team || fixture.away;

  // Check if a fixture is in the calendar (by team names)
  const isInCalendar = (fixture) => {
    const home = getHomeTeam(fixture)?.toLowerCase();
    const away = getAwayTeam(fixture)?.toLowerCase();
    return calendarMatches.some(
      m => m.home_team?.toLowerCase() === home && m.away_team?.toLowerCase() === away
    );
  };

  const togglePersonalCalendar = (fixture) => {
    const home = getHomeTeam(fixture);
    const away = getAwayTeam(fixture);
    
    if (isInCalendar(fixture)) {
      // Remove from calendar
      dispatch({
        type: ActionTypes.REMOVE_FROM_CALENDAR,
        payload: { home_team: home, away_team: away }
      });
      // Also remove from backend
      fetch('/api/calendar', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ home_team: home, away_team: away })
      }).catch(err => console.error('Failed to remove from calendar:', err));
    } else {
      // Add to calendar
      const match = {
        home_team: home,
        away_team: away,
        date: fixture.date,
        time: fixture.time,
        venue: fixture.venue,
        league: fixture.league
      };
      dispatch({ type: ActionTypes.ADD_TO_CALENDAR, payload: match });
      // Also persist to backend
      fetch('/api/calendar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(match)
      }).catch(err => console.error('Failed to persist calendar:', err));
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  const getLeagueName = (leagueId) => {
    const league = leagues.find(l => l.id === leagueId);
    return league ? `${league.flag || ''} ${league.name}` : leagueId;
  };

  return (
    <div className="schedule-page">
      <motion.main 
        className="main-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="page-header">
          <div>
            <h1>Match Schedule & Calendar</h1>
            <p>Upcoming fixtures across all leagues</p>
          </div>
          <div className="header-actions">
            <button className="refresh-btn" onClick={fetchFixtures} disabled={loading}>
              <RefreshCw size={18} className={loading ? 'spinning' : ''} />
            </button>
            <div className="view-toggle">
              <button 
                className={viewMode === 'list' ? 'active' : ''}
                onClick={() => setViewMode('list')}
              >
                List
              </button>
              <button 
                className={viewMode === 'calendar' ? 'active' : ''}
                onClick={() => setViewMode('calendar')}
              >
                Calendar
              </button>
            </div>
          </div>
        </div>

        {/* League Filter */}
        <div className="league-filter">
          {leagues.map(league => (
            <button
              key={league.id}
              className={`filter-btn ${selectedLeague === league.id ? 'active' : ''}`}
              onClick={() => setSelectedLeague(league.id)}
            >
              {league.flag && <span>{league.flag}</span>}
              <span>{league.name}</span>
            </button>
          ))}
        </div>

        {/* My Calendar */}
        {calendarMatches.length > 0 && (
          <div className="personal-calendar">
            <h3><Star size={18} /> My Matches ({calendarMatches.length})</h3>
            <div className="personal-matches">
              {calendarMatches.map((match, idx) => (
                <div key={match.id || idx} className="personal-match">
                  <span>{match.home_team} vs {match.away_team}</span>
                  <span>{match.date ? formatDate(match.date) : 'TBD'} • {match.time || 'TBD'}</span>
                  <button 
                    className="remove-match"
                    onClick={() => {
                      dispatch({
                        type: ActionTypes.REMOVE_FROM_CALENDAR,
                        payload: { home_team: match.home_team, away_team: match.away_team }
                      });
                      fetch('/api/calendar', {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ home_team: match.home_team, away_team: match.away_team })
                      }).catch(err => console.error('Failed to remove:', err));
                    }}
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Fixtures List */}
        <div className="fixtures-list">
          {loading ? (
            <div className="loading-state">
              <RefreshCw size={24} className="spinning" />
              <p>Loading fixtures...</p>
            </div>
          ) : filteredFixtures.length === 0 ? (
            <div className="empty-state">
              <Calendar size={48} />
              <h3>No fixtures available</h3>
              <p>Check back later for upcoming games in {selectedLeague === 'all' ? 'all leagues' : selectedLeague.toUpperCase()}</p>
            </div>
          ) : filteredFixtures.map((fixture, index) => (
            <motion.div
              key={fixture.id || index}
              className="fixture-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="fixture-header">
                <span className="fixture-league">{getLeagueName(fixture.league)}</span>
                <span className={`fixture-status ${fixture.status}`}>
                  {fixture.status === 'live' ? '🔴 LIVE' : fixture.status === 'finished' ? 'Final' : 'Upcoming'}
                </span>
                <button 
                  className={`add-to-calendar ${isInCalendar(fixture) ? 'added' : ''}`}
                  onClick={() => togglePersonalCalendar(fixture)}
                >
                  {isInCalendar(fixture) ? (
                    <><Check size={14} /> Added</>
                  ) : (
                    <><Plus size={14} /> Add to Calendar</>
                  )}
                </button>
              </div>
              
              <div className="fixture-teams">
                <span className="team home">
                  {fixture.home_logo && <img src={fixture.home_logo} alt="" className="team-logo" />}
                  {getHomeTeam(fixture)}
                  {fixture.home_score !== undefined && <span className="score">{fixture.home_score}</span>}
                </span>
                <span className="vs">VS</span>
                <span className="team away">
                  {fixture.away_logo && <img src={fixture.away_logo} alt="" className="team-logo" />}
                  {getAwayTeam(fixture)}
                  {fixture.away_score !== undefined && <span className="score">{fixture.away_score}</span>}
                </span>
              </div>
              
              <div className="fixture-details">
                <span><Calendar size={14} /> {fixture.date ? formatDate(fixture.date) : 'TBD'}</span>
                <span><Clock size={14} /> {fixture.time || 'TBD'}</span>
                <span><MapPin size={14} /> {fixture.venue || 'TBD'}</span>
              </div>
            </motion.div>
          ))}
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

export default SchedulePage;
