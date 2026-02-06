import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, Activity, Flame, Star, 
  ChevronRight, Menu, X, RefreshCw,
  Trophy, Calendar, Zap, MapPin, 
  Play, Eye, Clock, Users, Newspaper,
  BarChart2, Video, Sparkles
} from 'lucide-react';
import { NavLink } from 'react-router-dom';
import GameCard from '../components/GameCard';
import Sidebar from '../components/Sidebar';
import FootballGenie from '../components/FootballGenie';
import { footballAPI } from '../services/api';
import { useApp } from '../context/AppContext';
import './LandingPage.css';

const LandingPage = () => {
  const { state } = useApp();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [genieOpen, setGenieOpen] = useState(false);
  const [chatSessions, setChatSessions] = useState([]);
  const [matches, setMatches] = useState([]);
  const [standings, setStandings] = useState([]);
  const [news, setNews] = useState([]);
  const [leaders, setLeaders] = useState([]);
  const [featuredGames, setFeaturedGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeLeague, setActiveLeague] = useState(state.activeLeague || 'nfl');
  const [userCountry] = useState('USA');

  // Sync with global league filter
  useEffect(() => {
    if (state.activeLeague && state.activeLeague !== activeLeague) {
      setActiveLeague(state.activeLeague);
    }
  }, [state.activeLeague]);

  const leagues = [
    { id: 'nfl', name: 'NFL', flag: '🏈' },
    { id: 'college-football', name: 'College Football', flag: '🎓' },
    { id: 'cfl', name: 'CFL', flag: '🇨🇦' },
    { id: 'xfl', name: 'XFL', flag: '⚡' },
    { id: 'usfl', name: 'USFL', flag: '🇺🇸' },
  ];

  // Dynamic trends from leaders data
  const getTrends = () => {
    if (leaders.length === 0) {
      return [
        { id: 1, icon: Flame, label: 'Loading...', value: 'Fetching data', color: '#ef4444' },
      ];
    }
    const trends = [];
    const passingLeader = leaders.find(l => l.category === 'passing')?.leaders?.[0];
    const rushingLeader = leaders.find(l => l.category === 'rushing')?.leaders?.[0];
    const receivingLeader = leaders.find(l => l.category === 'receiving')?.leaders?.[0];
    
    if (passingLeader) trends.push({ id: 1, icon: Flame, label: 'Passing Leader', value: `${passingLeader.name} - ${passingLeader.value}`, color: '#ef4444' });
    if (rushingLeader) trends.push({ id: 2, icon: TrendingUp, label: 'Rushing Leader', value: `${rushingLeader.name} - ${rushingLeader.value}`, color: '#10b981' });
    if (receivingLeader) trends.push({ id: 3, icon: Star, label: 'Receiving Leader', value: `${receivingLeader.name} - ${receivingLeader.value}`, color: '#f59e0b' });
    if (trends.length < 3) trends.push({ id: 4, icon: Zap, label: 'Active League', value: activeLeague.toUpperCase(), color: '#8b5cf6' });
    
    return trends.length > 0 ? trends : [{ id: 1, icon: Activity, label: 'No Data', value: 'Check back soon', color: '#6b7280' }];
  };
  const trends = getTrends();

  // Use featured games from API (live or upcoming)
  const localGames = featuredGames.slice(0, 3).map(game => ({
    id: game.id,
    home: game.home_team,
    away: game.away_team,
    time: game.status === 'live' ? 'LIVE' : (game.time || game.date || 'TBD'),
    venue: game.venue || 'TBD',
    league: activeLeague.toUpperCase(),
    status: game.status === 'live' ? 'live' : (game.status === 'finished' ? 'finished' : 'upcoming'),
    homeScore: game.home_score,
    awayScore: game.away_score
  }));

  useEffect(() => {
    fetchData();
  }, [activeLeague]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [matchesRes, standingsRes, newsRes, leadersRes] = await Promise.all([
        footballAPI.getGames(activeLeague),
        footballAPI.getStandings(activeLeague),
        footballAPI.getNews(activeLeague, 5),
        footballAPI.getLeaders(activeLeague)
      ]);
      
      // Ensure we always get arrays
      const matchesData = matchesRes?.games || matchesRes?.matches || matchesRes;
      const allMatches = Array.isArray(matchesData) ? matchesData : [];
      setMatches(allMatches);
      
      // Set featured games (live games first, then upcoming)
      const liveGames = allMatches.filter(m => m.status === 'live');
      const upcomingGames = allMatches.filter(m => m.status === 'scheduled' || m.status === 'upcoming');
      const recentGames = allMatches.filter(m => m.status === 'finished').slice(0, 2);
      setFeaturedGames([...liveGames, ...upcomingGames.slice(0, 3), ...recentGames].slice(0, 5));
      
      const standingsData = standingsRes?.standings || standingsRes;
      setStandings((Array.isArray(standingsData) ? standingsData : []).slice(0, 5));
      
      const newsData = newsRes?.news || newsRes;
      setNews(Array.isArray(newsData) ? newsData : []);
      
      const leadersData = leadersRes?.leaders || leadersRes;
      setLeaders(Array.isArray(leadersData) ? leadersData : []);
    } catch (error) {
      console.error('Error fetching data:', error);
      // Fallback data for NFL
      setMatches([]);
      setFeaturedGames([]);
      setStandings([]);
      setLeaders([]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = (session) => {
    setChatSessions(prev => [session, ...prev.slice(0, 9)]);
  };

  const handleGenieToggle = () => {
    setGenieOpen(!genieOpen);
  };

  return (
    <div className="landing-page">
      {/* Sidebar */}
      <Sidebar 
        isOpen={sidebarOpen} 
        chatSessions={chatSessions}
      />

      {/* Main Content */}
      <main className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
        {/* Header */}
        <header className="landing-header">
          <button 
            className="menu-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          
          <div className="header-title">
            <Trophy className="header-icon" />
            <h1>Football Hub</h1>
          </div>

          <div className="header-location">
            <MapPin size={16} />
            <span>{userCountry}</span>
          </div>

          <button className="refresh-btn" onClick={fetchData} disabled={loading}>
            <RefreshCw size={20} className={loading ? 'spinning' : ''} />
          </button>
        </header>

        {/* Featured Games Section */}
        <section className="local-games-section">
          <div className="section-header">
            <h2 className="section-heading">
              <Flame size={20} />
              Featured Games
            </h2>
            <NavLink to="/schedule" className="view-all">
              View All <ChevronRight size={16} />
            </NavLink>
          </div>
          <div className="local-games-grid">
            {loading ? (
              <div className="loading-card" style={{ gridColumn: '1 / -1', padding: '2rem', textAlign: 'center' }}>Loading games...</div>
            ) : localGames.length === 0 ? (
              <div className="empty-state" style={{ gridColumn: '1 / -1', padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                No games available for {activeLeague.toUpperCase()}. Check back later!
              </div>
            ) : localGames.map((game, index) => (
              <motion.div
                key={game.id}
                className={`local-game-card ${game.status}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="local-game-header">
                  <span className="local-league">{game.league}</span>
                  <span className={`local-status ${game.status}`}>
                    {game.status === 'finished' ? 'FT' : game.time}
                  </span>
                </div>
                <div className="local-game-teams">
                  <div className="local-team">
                    <span className="team-name">{game.home}</span>
                    {game.homeScore !== undefined && <span className="team-score">{game.homeScore}</span>}
                  </div>
                  <span className="vs">vs</span>
                  <div className="local-team">
                    <span className="team-name">{game.away}</span>
                    {game.awayScore !== undefined && <span className="team-score">{game.awayScore}</span>}
                  </div>
                </div>
                <div className="local-game-venue">
                  <MapPin size={12} />
                  <span>{game.venue}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* League Tabs */}
        <div className="league-tabs">
          {leagues.map((league) => (
            <button
              key={league.id}
              className={`league-tab ${activeLeague === league.id ? 'active' : ''}`}
              onClick={() => setActiveLeague(league.id)}
            >
              <span className="league-flag">{league.flag}</span>
              <span className="league-name">{league.name}</span>
            </button>
          ))}
        </div>

        {/* Trends Section */}
        <section className="trends-section">
          <h2 className="section-heading">
            <Activity size={20} />
            Trending Now
          </h2>
          <div className="trends-grid">
            {trends.map((trend, index) => (
              <motion.div
                key={trend.id}
                className="trend-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                style={{ '--trend-color': trend.color }}
              >
                <div className="trend-icon">
                  <trend.icon size={20} />
                </div>
                <div className="trend-info">
                  <span className="trend-label">{trend.label}</span>
                  <span className="trend-value">{trend.value}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Matches Section */}
        <section className="matches-section">
          <div className="section-header">
            <h2 className="section-heading">
              <Calendar size={20} />
              Recent & Upcoming Matches
            </h2>
            <NavLink to="/schedule" className="view-all">
              View All <ChevronRight size={16} />
            </NavLink>
          </div>
          
          {loading ? (
            <div className="loading-grid">
              {[1, 2, 3].map((i) => (
                <div key={i} className="loading-card"></div>
              ))}
            </div>
          ) : (
            <div className="matches-grid">
              {(Array.isArray(matches) ? matches : []).slice(0, 6).map((match, index) => (
                <GameCard key={match.id || index} match={match} />
              ))}
            </div>
          )}
        </section>

        {/* Quick Stats */}
        <section className="stats-section">
          <div className="section-header">
            <h2 className="section-heading">
              <Trophy size={20} />
              Top 5 Standings
            </h2>
            <NavLink to="/standings" className="view-all">
              Full Table <ChevronRight size={16} />
            </NavLink>
          </div>
          
          <div className="standings-table">
            <div className="standings-header">
              <span className="pos">#</span>
              <span className="team">Team</span>
              <span className="won">W</span>
              <span className="lost">L</span>
              <span className="pct">PCT</span>
              <span className="streak">Streak</span>
            </div>
            {(Array.isArray(standings) ? standings : []).map((team, index) => (
              <motion.div
                key={team.id || index}
                className="standings-row"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <span className="pos">{team.position || team.rank || index + 1}</span>
                <span className="team">
                  {team.logo && <img src={team.logo} alt="" className="team-logo" />}
                  {team.team || team.name}
                </span>
                <span className="won">{team.wins ?? team.won ?? '-'}</span>
                <span className="lost">{team.losses ?? team.lost ?? '-'}</span>
                <span className="pct">{team.win_pct ?? team.pct ?? (team.wins && team.losses ? (team.wins / (team.wins + team.losses)).toFixed(3) : '-')}</span>
                <span className="streak">{team.streak || '-'}</span>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Navigation Quick Links */}
        <section className="quick-nav-section">
          <h2 className="section-heading">
            <Zap size={20} />
            Explore More
          </h2>
          <div className="quick-nav-grid">
            <NavLink to="/schedule" className="quick-nav-card">
              <div className="quick-nav-icon" style={{ '--nav-color': '#3b82f6' }}>
                <Calendar size={24} />
              </div>
              <div className="quick-nav-info">
                <h3>Match Schedule</h3>
                <p>Fixtures, calendar & personal reminders</p>
              </div>
              <ChevronRight size={20} />
            </NavLink>
            
            <NavLink to="/profiles" className="quick-nav-card">
              <div className="quick-nav-icon" style={{ '--nav-color': '#10b981' }}>
                <Users size={24} />
              </div>
              <div className="quick-nav-info">
                <h3>Team & Player Profiles</h3>
                <p>Stats, biographies & historical records</p>
              </div>
              <ChevronRight size={20} />
            </NavLink>
            
            <NavLink to="/fantasy" className="quick-nav-card">
              <div className="quick-nav-icon" style={{ '--nav-color': '#8b5cf6' }}>
                <Trophy size={24} />
              </div>
              <div className="quick-nav-info">
                <h3>Fantasy Football</h3>
                <p>Build your team & compete</p>
              </div>
              <ChevronRight size={20} />
            </NavLink>
            
            <NavLink to="/news" className="quick-nav-card">
              <div className="quick-nav-icon" style={{ '--nav-color': '#f59e0b' }}>
                <Newspaper size={24} />
              </div>
              <div className="quick-nav-info">
                <h3>News & Articles</h3>
                <p>Transfer rumors & expert analysis</p>
              </div>
              <ChevronRight size={20} />
            </NavLink>
            
            <NavLink to="/highlights" className="quick-nav-card">
              <div className="quick-nav-icon" style={{ '--nav-color': '#ef4444' }}>
                <Video size={24} />
              </div>
              <div className="quick-nav-info">
                <h3>Video Highlights</h3>
                <p>Key moments & replays</p>
              </div>
              <ChevronRight size={20} />
            </NavLink>
            
            <NavLink to="/odds" className="quick-nav-card">
              <div className="quick-nav-icon" style={{ '--nav-color': '#06b6d4' }}>
                <BarChart2 size={24} />
              </div>
              <div className="quick-nav-info">
                <h3>Betting & Odds</h3>
                <p>Live odds & predictions</p>
              </div>
              <ChevronRight size={20} />
            </NavLink>
          </div>
        </section>
      </main>

      {/* Football Genie Button (centered at bottom when closed) */}
      <AnimatePresence>
        {!genieOpen && (
          <motion.button
            className="genie-main-button"
            onClick={handleGenieToggle}
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

      {/* Football Genie Chat (bottom right when open) */}
      <FootballGenie 
        isOpen={genieOpen} 
        onToggle={handleGenieToggle}
        onNewChat={handleNewChat}
      />
    </div>
  );
};

export default LandingPage;
