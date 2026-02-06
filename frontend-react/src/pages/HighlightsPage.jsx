import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, Clock, Eye, ThumbsUp, MessageCircle, Share2, Bookmark, 
  Filter, Search, ChevronRight, Video, Film, TrendingUp, 
  Calendar, Download, X, Sparkles
} from 'lucide-react';
import FootballGenie from '../components/FootballGenie';
import { useApp } from '../context/AppContext';
import './HighlightsPage.css';

const HighlightsPage = () => {
  const { state } = useApp();
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [genieOpen, setGenieOpen] = useState(false);

  const filters = [
    { id: 'all', label: 'All Highlights' },
    { id: 'goals', label: 'Goals' },
    { id: 'skills', label: 'Skills & Tricks' },
    { id: 'saves', label: 'Best Saves' },
    { id: 'full-match', label: 'Full Highlights' },
    { id: 'interviews', label: 'Post-Match' }
  ];

  const videos = [
    {
      id: 1,
      category: 'goals',
      title: 'Haaland Hat-trick vs Newcastle - All Goals',
      thumbnail: 'https://via.placeholder.com/640x360/6366f1/ffffff?text=Haaland+Hat-trick',
      duration: '5:42',
      views: 2450000,
      likes: 89000,
      comments: 3400,
      date: '2 hours ago',
      channel: 'Premier League',
      featured: true,
      description: 'Watch all three goals from Erling Haaland\'s stunning hat-trick performance against Newcastle United.'
    },
    {
      id: 2,
      category: 'full-match',
      title: 'Liverpool 4-1 Everton - Extended Highlights',
      thumbnail: 'https://via.placeholder.com/640x360/ef4444/ffffff?text=Liverpool+vs+Everton',
      duration: '12:35',
      views: 1890000,
      likes: 56000,
      comments: 2100,
      date: '5 hours ago',
      channel: 'Premier League',
      featured: true,
      description: 'Extended highlights from the Merseyside derby as Liverpool dominate Everton at Anfield.'
    },
    {
      id: 3,
      category: 'skills',
      title: 'Vinicius Jr - Insane Skills & Dribbles 2024',
      thumbnail: 'https://via.placeholder.com/640x360/10b981/ffffff?text=Vinicius+Skills',
      duration: '8:20',
      views: 4200000,
      likes: 145000,
      comments: 5600,
      date: '1 day ago',
      channel: 'La Liga',
      featured: false,
      description: 'The best skills, dribbles and tricks from Vinicius Jr this season in La Liga.'
    },
    {
      id: 4,
      category: 'saves',
      title: 'Top 10 Saves of the Week - Gameweek 25',
      thumbnail: 'https://via.placeholder.com/640x360/f59e0b/ffffff?text=Top+Saves',
      duration: '6:15',
      views: 890000,
      likes: 34000,
      comments: 980,
      date: '1 day ago',
      channel: 'Premier League',
      featured: false,
      description: 'The most spectacular goalkeeper saves from Gameweek 25 of the Premier League season.'
    },
    {
      id: 5,
      category: 'goals',
      title: 'Salah Bicycle Kick Goal vs Man City',
      thumbnail: 'https://via.placeholder.com/640x360/8b5cf6/ffffff?text=Salah+Bicycle+Kick',
      duration: '2:30',
      views: 5600000,
      likes: 234000,
      comments: 8900,
      date: '2 days ago',
      channel: 'Premier League',
      featured: true,
      description: 'Mohamed Salah scores an incredible bicycle kick goal in the clash against Manchester City.'
    },
    {
      id: 6,
      category: 'interviews',
      title: 'Arteta Post-Match Interview After Arsenal Win',
      thumbnail: 'https://via.placeholder.com/640x360/0ea5e9/ffffff?text=Arteta+Interview',
      duration: '4:45',
      views: 450000,
      likes: 12000,
      comments: 890,
      date: '3 days ago',
      channel: 'Arsenal FC',
      featured: false,
      description: 'Mikel Arteta speaks to the press after Arsenal\'s crucial victory in the title race.'
    },
    {
      id: 7,
      category: 'full-match',
      title: 'Real Madrid 3-2 Barcelona - El Clasico Highlights',
      thumbnail: 'https://via.placeholder.com/640x360/ec4899/ffffff?text=El+Clasico',
      duration: '15:22',
      views: 8900000,
      likes: 345000,
      comments: 15600,
      date: '4 days ago',
      channel: 'La Liga',
      featured: true,
      description: 'Full highlights from an incredible El Clasico match with 5 goals and non-stop action.'
    },
    {
      id: 8,
      category: 'skills',
      title: 'Mbappe Speed & Skill Show 2024',
      thumbnail: 'https://via.placeholder.com/640x360/14b8a6/ffffff?text=Mbappe+Speed',
      duration: '7:50',
      views: 3400000,
      likes: 123000,
      comments: 4500,
      date: '5 days ago',
      channel: 'Ligue 1',
      featured: false,
      description: 'Kylian Mbappe\'s incredible speed and skill moments from Ligue 1 this season.'
    }
  ];

  const featuredVideos = videos.filter(v => v.featured);
  
  const filteredVideos = videos.filter(video => {
    const matchesFilter = activeFilter === 'all' || video.category === activeFilter;
    const matchesSearch = video.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          video.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const formatViews = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(0) + 'K';
    }
    return num;
  };

  return (
    <div className="highlights-page">
      <main className="main-content">
        <header className="page-header">
          <div className="header-left">
            <h1>
              <Video size={28} />
              Video Highlights
            </h1>
            <p>Watch the best moments, goals, and highlights from football around the world</p>
          </div>
          <div className="search-box">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search videos..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </header>

        {/* Featured Video */}
        {featuredVideos.length > 0 && activeFilter === 'all' && !searchQuery && (
          <section className="featured-section">
            <h2><TrendingUp size={20} /> Featured Highlights</h2>
            <div className="featured-grid">
              <motion.div 
                className="featured-main"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                onClick={() => setSelectedVideo(featuredVideos[0])}
              >
                <div className="video-thumbnail">
                  <img src={featuredVideos[0].thumbnail} alt={featuredVideos[0].title} />
                  <div className="play-overlay">
                    <Play size={48} />
                  </div>
                  <span className="duration">{featuredVideos[0].duration}</span>
                </div>
                <div className="video-info">
                  <h3>{featuredVideos[0].title}</h3>
                  <p>{featuredVideos[0].description}</p>
                  <div className="video-meta">
                    <span><Eye size={14} /> {formatViews(featuredVideos[0].views)} views</span>
                    <span><Calendar size={14} /> {featuredVideos[0].date}</span>
                  </div>
                </div>
              </motion.div>
              <div className="featured-sidebar">
                {featuredVideos.slice(1, 4).map((video, index) => (
                  <motion.div 
                    key={video.id}
                    className="featured-item"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={() => setSelectedVideo(video)}
                  >
                    <div className="video-thumbnail-small">
                      <img src={video.thumbnail} alt={video.title} />
                      <span className="duration">{video.duration}</span>
                    </div>
                    <div className="video-info-small">
                      <h4>{video.title}</h4>
                      <span>{formatViews(video.views)} views • {video.date}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* Filters */}
        <div className="video-filters">
          {filters.map(filter => (
            <button
              key={filter.id}
              className={`filter-btn ${activeFilter === filter.id ? 'active' : ''}`}
              onClick={() => setActiveFilter(filter.id)}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {/* Videos Grid */}
        <section className="videos-section">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeFilter}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="videos-grid"
            >
              {filteredVideos.map((video, index) => (
                <motion.div
                  key={video.id}
                  className="video-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => setSelectedVideo(video)}
                  whileHover={{ y: -5 }}
                >
                  <div className="video-thumbnail">
                    <img src={video.thumbnail} alt={video.title} />
                    <div className="play-overlay">
                      <Play size={32} />
                    </div>
                    <span className="duration">{video.duration}</span>
                    <span className="category-tag">{video.category.replace('-', ' ')}</span>
                  </div>
                  <div className="video-content">
                    <h3>{video.title}</h3>
                    <div className="channel-name">{video.channel}</div>
                    <div className="video-stats">
                      <span><Eye size={12} /> {formatViews(video.views)}</span>
                      <span><ThumbsUp size={12} /> {formatViews(video.likes)}</span>
                      <span>{video.date}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </AnimatePresence>
        </section>

        {/* Video Modal */}
        <AnimatePresence>
          {selectedVideo && (
            <motion.div
              className="video-modal-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedVideo(null)}
            >
              <motion.div
                className="video-modal"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={e => e.stopPropagation()}
              >
                <button className="close-modal" onClick={() => setSelectedVideo(null)}>
                  <X size={20} />
                </button>
                <div className="video-player">
                  <img src={selectedVideo.thumbnail} alt={selectedVideo.title} />
                  <div className="play-button-large">
                    <Play size={64} fill="white" />
                  </div>
                </div>
                <div className="modal-content">
                  <h2>{selectedVideo.title}</h2>
                  <div className="modal-meta">
                    <span className="channel">{selectedVideo.channel}</span>
                    <span>{formatViews(selectedVideo.views)} views</span>
                    <span>{selectedVideo.date}</span>
                  </div>
                  <p>{selectedVideo.description}</p>
                  <div className="modal-actions">
                    <button className="action-btn primary">
                      <ThumbsUp size={16} /> {formatViews(selectedVideo.likes)}
                    </button>
                    <button className="action-btn">
                      <MessageCircle size={16} /> {formatViews(selectedVideo.comments)}
                    </button>
                    <button className="action-btn">
                      <Share2 size={16} /> Share
                    </button>
                    <button className="action-btn">
                      <Bookmark size={16} /> Save
                    </button>
                    <button className="action-btn">
                      <Download size={16} /> Download
                    </button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

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

export default HighlightsPage;
