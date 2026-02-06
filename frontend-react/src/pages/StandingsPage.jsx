import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Trophy, ChevronUp, ChevronDown, Minus,
  TrendingUp, TrendingDown, Activity, Filter, Sparkles
} from 'lucide-react';
import { footballAPI } from '../services/api';
import FootballGenie from '../components/FootballGenie';
import { useApp } from '../context/AppContext';
import './StandingsPage.css';

const StandingsPage = () => {
  const { state } = useApp();
  const [standings, setStandings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeLeague, setActiveLeague] = useState(state.activeLeague || 'nfl');
  const [genieOpen, setGenieOpen] = useState(false);

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

  useEffect(() => {
    fetchStandings();
  }, [activeLeague]);

  const fetchStandings = async () => {
    setLoading(true);
    try {
      const response = await footballAPI.getStandings(activeLeague);
      setStandings(response.standings || response || []);
    } catch (error) {
      console.error('Error fetching standings:', error);
      // Mock NFL data for demo
      setStandings([
        { position: 1, team: 'Kansas City Chiefs', logo: '', played: 17, won: 14, lost: 3, tied: 0, pointsFor: 496, pointsAgainst: 328, pointDiff: 168, winPct: '.824', division: 'AFC West', form: ['W', 'W', 'W', 'W', 'W'] },
        { position: 2, team: 'Baltimore Ravens', logo: '', played: 17, won: 13, lost: 4, tied: 0, pointsFor: 483, pointsAgainst: 280, pointDiff: 203, winPct: '.765', division: 'AFC North', form: ['W', 'W', 'L', 'W', 'W'] },
        { position: 3, team: 'San Francisco 49ers', logo: '', played: 17, won: 12, lost: 5, tied: 0, pointsFor: 491, pointsAgainst: 298, pointDiff: 193, winPct: '.706', division: 'NFC West', form: ['W', 'W', 'W', 'L', 'W'] },
        { position: 4, team: 'Detroit Lions', logo: '', played: 17, won: 12, lost: 5, tied: 0, pointsFor: 461, pointsAgainst: 355, pointDiff: 106, winPct: '.706', division: 'NFC North', form: ['W', 'L', 'W', 'W', 'W'] },
        { position: 5, team: 'Dallas Cowboys', logo: '', played: 17, won: 12, lost: 5, tied: 0, pointsFor: 509, pointsAgainst: 315, pointDiff: 194, winPct: '.706', division: 'NFC East', form: ['W', 'W', 'W', 'L', 'W'] },
        { position: 6, team: 'Buffalo Bills', logo: '', played: 17, won: 11, lost: 6, tied: 0, pointsFor: 451, pointsAgainst: 311, pointDiff: 140, winPct: '.647', division: 'AFC East', form: ['W', 'L', 'W', 'W', 'L'] },
        { position: 7, team: 'Philadelphia Eagles', logo: '', played: 17, won: 11, lost: 6, tied: 0, pointsFor: 433, pointsAgainst: 350, pointDiff: 83, winPct: '.647', division: 'NFC East', form: ['L', 'W', 'L', 'W', 'W'] },
        { position: 8, team: 'Miami Dolphins', logo: '', played: 17, won: 11, lost: 6, tied: 0, pointsFor: 496, pointsAgainst: 391, pointDiff: 105, winPct: '.647', division: 'AFC East', form: ['W', 'W', 'L', 'W', 'L'] },
        { position: 9, team: 'Cleveland Browns', logo: '', played: 17, won: 11, lost: 6, tied: 0, pointsFor: 396, pointsAgainst: 362, pointDiff: 34, winPct: '.647', division: 'AFC North', form: ['W', 'L', 'W', 'W', 'L'] },
        { position: 10, team: 'Green Bay Packers', logo: '', played: 17, won: 9, lost: 8, tied: 0, pointsFor: 383, pointsAgainst: 365, pointDiff: 18, winPct: '.529', division: 'NFC North', form: ['L', 'W', 'W', 'L', 'W'] },
        { position: 11, team: 'Pittsburgh Steelers', logo: '', played: 17, won: 10, lost: 7, tied: 0, pointsFor: 304, pointsAgainst: 324, pointDiff: -20, winPct: '.588', division: 'AFC North', form: ['L', 'L', 'W', 'W', 'W'] },
        { position: 12, team: 'Los Angeles Rams', logo: '', played: 17, won: 10, lost: 7, tied: 0, pointsFor: 398, pointsAgainst: 380, pointDiff: 18, winPct: '.588', division: 'NFC West', form: ['W', 'W', 'L', 'W', 'L'] },
        { position: 13, team: 'Tampa Bay Buccaneers', logo: '', played: 17, won: 9, lost: 8, tied: 0, pointsFor: 346, pointsAgainst: 333, pointDiff: 13, winPct: '.529', division: 'NFC South', form: ['L', 'W', 'L', 'W', 'W'] },
        { position: 14, team: 'Seattle Seahawks', logo: '', played: 17, won: 9, lost: 8, tied: 0, pointsFor: 364, pointsAgainst: 401, pointDiff: -37, winPct: '.529', division: 'NFC West', form: ['L', 'L', 'W', 'W', 'L'] },
        { position: 15, team: 'Houston Texans', logo: '', played: 17, won: 10, lost: 7, tied: 0, pointsFor: 378, pointsAgainst: 353, pointDiff: 25, winPct: '.588', division: 'AFC South', form: ['W', 'W', 'L', 'W', 'W'] },
        { position: 16, team: 'Jacksonville Jaguars', logo: '', played: 17, won: 9, lost: 8, tied: 0, pointsFor: 369, pointsAgainst: 373, pointDiff: -4, winPct: '.529', division: 'AFC South', form: ['L', 'W', 'L', 'L', 'W'] },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getPositionClass = (position) => {
    if (position <= 1) return 'division-leader';
    if (position <= 7) return 'playoff-spot';
    if (position <= 10) return 'wild-card-hunt';
    return '';
  };

  const getFormClass = (result) => {
    switch (result) {
      case 'W': return 'form-win';
      case 'D': return 'form-draw';
      case 'L': return 'form-loss';
      default: return '';
    }
  };

  const getCurrentLeagueName = () => {
    const league = leagues.find(l => l.id === activeLeague);
    return league ? `${league.flag} ${league.name}` : 'League';
  };

  return (
    <div className="standings-page">
      <motion.main 
        className="main-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="page-header">
          <div>
            <h1>
              <Trophy size={28} className="header-icon" />
              League Standings
            </h1>
            <p>{getCurrentLeagueName()} - Season 2025/26</p>
          </div>
        </div>

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

        {/* Standings Legend */}
        <div className="standings-legend">
          <div className="legend-item champions-league">
            <span className="legend-dot"></span>
            <span>Champions League</span>
          </div>
          <div className="legend-item europa-league">
            <span className="legend-dot"></span>
            <span>Europa League</span>
          </div>
          <div className="legend-item conference-league">
            <span className="legend-dot"></span>
            <span>Conference League</span>
          </div>
          <div className="legend-item relegation">
            <span className="legend-dot"></span>
            <span>Relegation</span>
          </div>
        </div>

        {/* Standings Table */}
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading standings...</p>
          </div>
        ) : (
          <div className="standings-table-container">
            <table className="standings-table">
              <thead>
                <tr>
                  <th className="col-pos">#</th>
                  <th className="col-team">Team</th>
                  <th className="col-stat">P</th>
                  <th className="col-stat">W</th>
                  <th className="col-stat">D</th>
                  <th className="col-stat">L</th>
                  <th className="col-stat hide-mobile">GF</th>
                  <th className="col-stat hide-mobile">GA</th>
                  <th className="col-stat">GD</th>
                  <th className="col-stat col-points">Pts</th>
                  <th className="col-form hide-mobile">Form</th>
                </tr>
              </thead>
              <tbody>
                {standings.map((team, index) => (
                  <motion.tr
                    key={team.team || index}
                    className={`standings-row ${getPositionClass(team.position || index + 1)}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.03 }}
                  >
                    <td className="col-pos">
                      <span className={`position-badge ${getPositionClass(team.position || index + 1)}`}>
                        {team.position || index + 1}
                      </span>
                    </td>
                    <td className="col-team">
                      <div className="team-info">
                        {team.logo && (
                          <img src={team.logo} alt="" className="team-logo" />
                        )}
                        <span className="team-name">{team.team || team.name}</span>
                      </div>
                    </td>
                    <td className="col-stat">{team.played || team.games || '-'}</td>
                    <td className="col-stat">{team.won || team.wins || '-'}</td>
                    <td className="col-stat">{team.drawn || team.draws || '-'}</td>
                    <td className="col-stat">{team.lost || team.losses || '-'}</td>
                    <td className="col-stat hide-mobile">{team.goalsFor || team.goals_for || '-'}</td>
                    <td className="col-stat hide-mobile">{team.goalsAgainst || team.goals_against || '-'}</td>
                    <td className="col-stat">
                      <span className={`goal-diff ${(team.goalDiff || team.goal_diff || 0) > 0 ? 'positive' : (team.goalDiff || team.goal_diff || 0) < 0 ? 'negative' : ''}`}>
                        {(team.goalDiff || team.goal_diff || 0) > 0 ? '+' : ''}{team.goalDiff || team.goal_diff || 0}
                      </span>
                    </td>
                    <td className="col-stat col-points">
                      <span className="points-badge">{team.points || '-'}</span>
                    </td>
                    <td className="col-form hide-mobile">
                      <div className="form-indicators">
                        {(team.form || []).slice(-5).map((result, i) => (
                          <span key={i} className={`form-badge ${getFormClass(result)}`}>
                            {result}
                          </span>
                        ))}
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Stats Summary */}
        <div className="stats-summary">
          <div className="stat-card">
            <TrendingUp size={24} />
            <div className="stat-info">
              <span className="stat-label">Top Scorer Team</span>
              <span className="stat-value">{standings[0]?.team || 'Arsenal'} - {standings[0]?.goalsFor || 52} goals</span>
            </div>
          </div>
          <div className="stat-card">
            <Activity size={24} />
            <div className="stat-info">
              <span className="stat-label">Best Defense</span>
              <span className="stat-value">Liverpool - 16 conceded</span>
            </div>
          </div>
          <div className="stat-card">
            <Trophy size={24} />
            <div className="stat-info">
              <span className="stat-label">Most Wins</span>
              <span className="stat-value">{standings[0]?.team || 'Arsenal'} - {standings[0]?.won || 16} wins</span>
            </div>
          </div>
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

export default StandingsPage;
