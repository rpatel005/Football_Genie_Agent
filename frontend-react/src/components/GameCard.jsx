import React from 'react';
import { motion } from 'framer-motion';
import { Clock, MapPin, Trophy, TrendingUp } from 'lucide-react';
import './GameCard.css';

const GameCard = ({ match, onClick }) => {
  const isLive = match.status === 'in_progress' || match.status === 'LIVE';
  const isFinished = match.status === 'finished' || match.status === 'FT';
  
  return (
    <motion.div 
      className={`game-card ${isLive ? 'live' : ''}`}
      whileHover={{ scale: 1.02, y: -4 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {isLive && (
        <div className="live-badge">
          <span className="pulse"></span>
          LIVE
        </div>
      )}
      
      <div className="game-header">
        <span className="league-name">{match.league || 'Premier League'}</span>
        <span className="game-time">
          <Clock size={12} />
          {match.time || match.date || 'TBD'}
        </span>
      </div>

      <div className="teams-container">
        <div className="team home">
          <div className="team-logo">
            {match.home_logo ? (
              <img src={match.home_logo} alt={match.home_team} />
            ) : (
              <div className="team-initial">{match.home_team?.[0] || 'H'}</div>
            )}
          </div>
          <span className="team-name">{match.home_team || 'Home Team'}</span>
        </div>

        <div className="score-container">
          {isFinished || isLive ? (
            <div className="score">
              <span className="home-score">{match.home_score ?? '-'}</span>
              <span className="score-divider">:</span>
              <span className="away-score">{match.away_score ?? '-'}</span>
            </div>
          ) : (
            <div className="vs">VS</div>
          )}
          <span className="match-status">
            {isLive ? match.minute || 'Live' : isFinished ? 'Full Time' : 'Scheduled'}
          </span>
        </div>

        <div className="team away">
          <div className="team-logo">
            {match.away_logo ? (
              <img src={match.away_logo} alt={match.away_team} />
            ) : (
              <div className="team-initial">{match.away_team?.[0] || 'A'}</div>
            )}
          </div>
          <span className="team-name">{match.away_team || 'Away Team'}</span>
        </div>
      </div>

      <div className="game-footer">
        {match.venue && (
          <span className="venue">
            <MapPin size={12} />
            {match.venue}
          </span>
        )}
        {match.odds && (
          <span className="odds">
            <TrendingUp size={12} />
            {match.odds}
          </span>
        )}
      </div>
    </motion.div>
  );
};

export default GameCard;
