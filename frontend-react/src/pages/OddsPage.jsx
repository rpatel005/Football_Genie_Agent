import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, DollarSign, BarChart2, RefreshCw,
  ChevronDown, ChevronUp, Clock, Calendar,
  Target, Percent, AlertCircle, Trophy,
  ArrowUpRight, ArrowDownRight, Minus, Sparkles
} from 'lucide-react';
import { sportsAPI } from '../services/api';
import FootballGenie from '../components/FootballGenie';
import { useApp } from '../context/AppContext';
import './OddsPage.css';

const OddsPage = () => {
  const { state } = useApp();
  const [activeLeague, setActiveLeague] = useState(state.activeLeague || 'eng.1');
  const [activeTab, setActiveTab] = useState('odds');
  const [odds, setOdds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [genieOpen, setGenieOpen] = useState(false);

  // Sync with global league filter
  useEffect(() => {
    if (state.activeLeague && state.activeLeague !== activeLeague) {
      setActiveLeague(state.activeLeague);
    }
  }, [state.activeLeague]);

  const leagues = [
    { id: 'eng.1', name: 'Premier League', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿' },
    { id: 'esp.1', name: 'La Liga', flag: '🇪🇸' },
    { id: 'ger.1', name: 'Bundesliga', flag: '🇩🇪' },
    { id: 'ita.1', name: 'Serie A', flag: '🇮🇹' },
    { id: 'fra.1', name: 'Ligue 1', flag: '🇫🇷' },
    { id: 'usa.1', name: 'MLS', flag: '🇺🇸' },
  ];

  const tabs = [
    { id: 'odds', label: 'Match Odds', icon: DollarSign },
    { id: 'predictions', label: 'Win Probabilities', icon: Percent },
    { id: 'futures', label: 'Futures & Outrights', icon: Trophy },
  ];

  // Mock betting data
  const mockOdds = [
    {
      id: 1,
      home: 'Arsenal',
      away: 'Chelsea',
      date: '2024-01-25',
      time: '20:00',
      homeOdds: 1.85,
      drawOdds: 3.60,
      awayOdds: 4.20,
      homeProbability: 52,
      drawProbability: 26,
      awayProbability: 22,
      overUnder: { line: 2.5, over: 1.91, under: 1.95 },
      bothTeamsScore: { yes: 1.75, no: 2.05 },
      trend: 'home'
    },
    {
      id: 2,
      home: 'Liverpool',
      away: 'Man City',
      date: '2024-01-26',
      time: '17:30',
      homeOdds: 2.45,
      drawOdds: 3.40,
      awayOdds: 2.80,
      homeProbability: 38,
      drawProbability: 28,
      awayProbability: 34,
      overUnder: { line: 2.5, over: 1.65, under: 2.25 },
      bothTeamsScore: { yes: 1.55, no: 2.40 },
      trend: 'stable'
    },
    {
      id: 3,
      home: 'Man United',
      away: 'Tottenham',
      date: '2024-01-27',
      time: '14:00',
      homeOdds: 2.10,
      drawOdds: 3.50,
      awayOdds: 3.40,
      homeProbability: 45,
      drawProbability: 27,
      awayProbability: 28,
      overUnder: { line: 2.5, over: 1.85, under: 2.00 },
      bothTeamsScore: { yes: 1.70, no: 2.10 },
      trend: 'away'
    },
    {
      id: 4,
      home: 'Newcastle',
      away: 'Brighton',
      date: '2024-01-27',
      time: '16:30',
      homeOdds: 1.95,
      drawOdds: 3.60,
      awayOdds: 3.90,
      homeProbability: 48,
      drawProbability: 26,
      awayProbability: 26,
      overUnder: { line: 2.5, over: 2.00, under: 1.85 },
      bothTeamsScore: { yes: 1.80, no: 2.00 },
      trend: 'home'
    },
    {
      id: 5,
      home: 'Aston Villa',
      away: 'West Ham',
      date: '2024-01-28',
      time: '15:00',
      homeOdds: 1.75,
      drawOdds: 3.80,
      awayOdds: 4.50,
      homeProbability: 54,
      drawProbability: 24,
      awayProbability: 22,
      overUnder: { line: 2.5, over: 1.90, under: 1.95 },
      bothTeamsScore: { yes: 1.85, no: 1.95 },
      trend: 'home'
    },
  ];

  // Mock futures data
  const futuresData = [
    { id: 1, market: 'League Winner', selection: 'Man City', odds: 1.50, probability: 67 },
    { id: 2, market: 'League Winner', selection: 'Liverpool', odds: 4.00, probability: 25 },
    { id: 3, market: 'League Winner', selection: 'Arsenal', odds: 6.00, probability: 17 },
    { id: 4, market: 'Top 4 Finish', selection: 'Aston Villa', odds: 1.80, probability: 56 },
    { id: 5, market: 'Relegation', selection: 'Sheffield United', odds: 1.20, probability: 83 },
    { id: 6, market: 'Top Scorer', selection: 'Erling Haaland', odds: 1.40, probability: 71 },
    { id: 7, market: 'Top Scorer', selection: 'Mohamed Salah', odds: 5.50, probability: 18 },
  ];

  useEffect(() => {
    fetchOdds();
  }, [activeLeague]);

  const fetchOdds = async () => {
    setLoading(true);
    try {
      // Try to fetch from API
      const response = await sportsAPI.getOdds('soccer', activeLeague);
      if (response && response.odds) {
        setOdds(response.odds);
      } else {
        setOdds(mockOdds);
      }
    } catch (error) {
      console.error('Error fetching odds:', error);
      setOdds(mockOdds);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'home': return <ArrowUpRight size={14} className="trend-up" />;
      case 'away': return <ArrowDownRight size={14} className="trend-down" />;
      default: return <Minus size={14} className="trend-stable" />;
    }
  };

  const renderOddsTab = () => (
    <div className="odds-list">
      {odds.map((match) => (
        <motion.div
          key={match.id}
          className="odds-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="match-header">
            <div className="match-date">
              <Calendar size={14} />
              <span>{formatDate(match.date)}</span>
              <Clock size={14} />
              <span>{match.time}</span>
            </div>
            <div className="odds-trend">
              {getTrendIcon(match.trend)}
              <span>Line Moving</span>
            </div>
          </div>

          <div className="match-teams">
            <span className="team home">{match.home}</span>
            <span className="vs">vs</span>
            <span className="team away">{match.away}</span>
          </div>

          <div className="odds-grid">
            <div className="odds-item home">
              <span className="odds-label">Home</span>
              <span className="odds-value">{match.homeOdds.toFixed(2)}</span>
              <span className="odds-probability">{match.homeProbability}%</span>
            </div>
            <div className="odds-item draw">
              <span className="odds-label">Draw</span>
              <span className="odds-value">{match.drawOdds.toFixed(2)}</span>
              <span className="odds-probability">{match.drawProbability}%</span>
            </div>
            <div className="odds-item away">
              <span className="odds-label">Away</span>
              <span className="odds-value">{match.awayOdds.toFixed(2)}</span>
              <span className="odds-probability">{match.awayProbability}%</span>
            </div>
          </div>

          <div className="additional-markets">
            <div className="market">
              <span className="market-label">Over/Under {match.overUnder.line}</span>
              <div className="market-odds">
                <span>O {match.overUnder.over.toFixed(2)}</span>
                <span>U {match.overUnder.under.toFixed(2)}</span>
              </div>
            </div>
            <div className="market">
              <span className="market-label">Both Teams Score</span>
              <div className="market-odds">
                <span>Yes {match.bothTeamsScore.yes.toFixed(2)}</span>
                <span>No {match.bothTeamsScore.no.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );

  const renderPredictionsTab = () => (
    <div className="predictions-list">
      {odds.map((match) => (
        <motion.div
          key={match.id}
          className="prediction-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="prediction-header">
            <span className="prediction-date">{formatDate(match.date)} • {match.time}</span>
          </div>
          
          <div className="prediction-teams">
            <span>{match.home}</span>
            <span className="vs">vs</span>
            <span>{match.away}</span>
          </div>

          <div className="probability-bars">
            <div className="prob-row">
              <span className="prob-label">Home Win</span>
              <div className="prob-bar-container">
                <div 
                  className="prob-bar home" 
                  style={{ width: `${match.homeProbability}%` }}
                ></div>
              </div>
              <span className="prob-value">{match.homeProbability}%</span>
            </div>
            <div className="prob-row">
              <span className="prob-label">Draw</span>
              <div className="prob-bar-container">
                <div 
                  className="prob-bar draw" 
                  style={{ width: `${match.drawProbability}%` }}
                ></div>
              </div>
              <span className="prob-value">{match.drawProbability}%</span>
            </div>
            <div className="prob-row">
              <span className="prob-label">Away Win</span>
              <div className="prob-bar-container">
                <div 
                  className="prob-bar away" 
                  style={{ width: `${match.awayProbability}%` }}
                ></div>
              </div>
              <span className="prob-value">{match.awayProbability}%</span>
            </div>
          </div>

          <div className="prediction-insight">
            <AlertCircle size={14} />
            <span>
              {match.homeProbability > match.awayProbability + 10
                ? `${match.home} are clear favorites with ${match.homeProbability}% chance to win`
                : match.awayProbability > match.homeProbability + 10
                ? `${match.away} are favorites with ${match.awayProbability}% chance to win`
                : 'This is expected to be a closely contested match'}
            </span>
          </div>
        </motion.div>
      ))}
    </div>
  );

  const renderFuturesTab = () => (
    <div className="futures-list">
      {['League Winner', 'Top 4 Finish', 'Relegation', 'Top Scorer'].map((market) => (
        <div key={market} className="futures-section">
          <h3 className="futures-market-title">
            <Trophy size={16} />
            {market}
          </h3>
          <div className="futures-grid">
            {futuresData
              .filter((f) => f.market === market)
              .map((future) => (
                <motion.div
                  key={future.id}
                  className="future-card"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="future-selection">{future.selection}</div>
                  <div className="future-odds">{future.odds.toFixed(2)}</div>
                  <div className="future-probability">
                    <div 
                      className="prob-fill" 
                      style={{ width: `${future.probability}%` }}
                    ></div>
                    <span>{future.probability}%</span>
                  </div>
                </motion.div>
              ))}
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="odds-page">
      <motion.main 
        className="main-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="page-header">
          <div>
            <h1>Betting & Odds</h1>
            <p>Live odds, probabilities & futures markets</p>
          </div>
          <button className="refresh-btn" onClick={fetchOdds} disabled={loading}>
            <RefreshCw size={20} className={loading ? 'spinning' : ''} />
          </button>
        </div>

        {/* League Selector */}
        <div className="league-selector">
          {leagues.map((league) => (
            <button
              key={league.id}
              className={`league-btn ${activeLeague === league.id ? 'active' : ''}`}
              onClick={() => setActiveLeague(league.id)}
            >
              <span className="flag">{league.flag}</span>
              <span className="name">{league.name}</span>
            </button>
          ))}
        </div>

        {/* Tabs */}
        <div className="odds-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`odds-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon size={18} />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Disclaimer */}
        <div className="betting-disclaimer">
          <AlertCircle size={16} />
          <span>Odds are for informational purposes only. Please gamble responsibly.</span>
        </div>

        {/* Content */}
        {loading ? (
          <div className="loading-grid">
            {[1, 2, 3].map((i) => (
              <div key={i} className="loading-card"></div>
            ))}
          </div>
        ) : (
          <>
            {activeTab === 'odds' && renderOddsTab()}
            {activeTab === 'predictions' && renderPredictionsTab()}
            {activeTab === 'futures' && renderFuturesTab()}
          </>
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

export default OddsPage;
