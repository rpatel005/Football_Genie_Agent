import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Newspaper, Clock, User, MessageCircle, ThumbsUp, Share2, 
  Bookmark, TrendingUp, Filter, Search, ChevronRight, Eye, Sparkles
} from 'lucide-react';
import FootballGenie from '../components/FootballGenie';
import { useApp } from '../context/AppContext';
import './NewsPage.css';

const NewsPage = () => {
  const { state } = useApp();
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [genieOpen, setGenieOpen] = useState(false);

  const categories = [
    { id: 'all', label: 'All News' },
    { id: 'trade', label: 'Trades & Free Agency' },
    { id: 'game-reports', label: 'Game Reports' },
    { id: 'injuries', label: 'Injuries' },
    { id: 'analysis', label: 'Analysis' },
    { id: 'draft', label: 'NFL Draft' }
  ];

  const articles = [
    {
      id: 1,
      category: 'trade',
      title: 'Chiefs Acquire Star Wide Receiver in Blockbuster Trade',
      excerpt: 'Kansas City bolsters their receiving corps with a major trade acquisition ahead of the playoffs.',
      author: 'James Wilson',
      date: '2 hours ago',
      readTime: '5 min read',
      image: 'https://via.placeholder.com/600x400/6366f1/ffffff?text=Trade+News',
      views: 12500,
      likes: 342,
      comments: 89,
      trending: true,
      content: `The Kansas City Chiefs have made a blockbuster move, acquiring a Pro Bowl wide receiver to strengthen their offense for the playoff push.

      The trade sends draft picks to the opposing team in exchange for the talented receiver who has amassed over 1,000 receiving yards this season.

      GM Brett Veach indicated this move was necessary to provide more weapons for Patrick Mahomes as they pursue another Super Bowl title.`
    },
    {
      id: 2,
      category: 'game-reports',
      title: '49ers Dominate in 35-17 NFC Championship Victory',
      excerpt: 'A dominant defensive performance propels San Francisco to the Super Bowl with a comprehensive win.',
      author: 'Sarah Mitchell',
      date: '5 hours ago',
      readTime: '7 min read',
      image: 'https://via.placeholder.com/600x400/10b981/ffffff?text=Game+Report',
      views: 28400,
      likes: 567,
      comments: 156,
      trending: true,
      content: `The San Francisco 49ers delivered a masterclass defensive performance, shutting down the opposition en route to a 35-17 NFC Championship victory.

      Brock Purdy threw for 267 yards and 3 touchdowns, while the defense forced 4 turnovers including 2 interceptions.

      The 49ers will face the winner of the AFC Championship in the Super Bowl, seeking their sixth championship in franchise history.`
    },
    {
      id: 3,
      category: 'injuries',
      title: 'Star Quarterback Questionable for Playoff Game with Ankle Injury',
      excerpt: 'A significant concern for playoff contenders as their franchise QB is listed as questionable heading into the postseason.',
      author: 'Mark Thompson',
      date: '1 day ago',
      readTime: '3 min read',
      image: 'https://via.placeholder.com/600x400/ef4444/ffffff?text=Injury+Update',
      views: 8900,
      likes: 123,
      comments: 45,
      trending: false,
      content: `In what comes as a major concern heading into the playoffs, the team has listed their starting quarterback as questionable with an ankle injury sustained in the final regular season game.

      The injury was confirmed following an MRI scan, with the player already beginning his rehabilitation program.

      This leaves the manager with limited options upfront during a crucial period of the season.`
    },
    {
      id: 4,
      category: 'analysis',
      title: 'Tactical Breakdown: How Arsenal\'s New Formation is Working',
      excerpt: 'A deep dive into Arteta\'s innovative 3-2-5 system that has transformed Arsenal into title contenders.',
      author: 'David Martinez',
      date: '1 day ago',
      readTime: '10 min read',
      image: 'https://via.placeholder.com/600x400/f59e0b/ffffff?text=Tactical+Analysis',
      views: 15600,
      likes: 445,
      comments: 78,
      trending: false,
      content: `Mikel Arteta's tactical evolution has been one of the most fascinating stories of the season. His innovative approach to formations has caught many opponents off guard.

      The 3-2-5 shape in possession allows Arsenal to overload attacking areas while maintaining defensive solidity. Key to this system is the role of the inverted full-backs.

      Statistical analysis shows Arsenal create 35% more chances from central areas compared to last season.`
    },
    {
      id: 5,
      category: 'interviews',
      title: 'Exclusive: Haaland on His Premier League Journey',
      excerpt: 'The Norwegian striker opens up about adapting to English football and his goals for the future.',
      author: 'Emma Collins',
      date: '2 days ago',
      readTime: '8 min read',
      image: 'https://via.placeholder.com/600x400/8b5cf6/ffffff?text=Exclusive+Interview',
      views: 45200,
      likes: 892,
      comments: 234,
      trending: true,
      content: `In an exclusive interview, Erling Haaland reflects on his incredible first season in the Premier League and what drives him to be the best.

      "The intensity is unlike anything I've experienced before," Haaland reveals. "Every game feels like a final. That's what makes this league special."

      When asked about records, the striker's ambition is clear: "I want to break every record possible. That's just how I'm wired."`
    },
    {
      id: 6,
      category: 'transfers',
      title: 'Chelsea Eye Summer Move for French Defender',
      excerpt: 'The Blues are looking to strengthen their backline with a €50M bid for the Ligue 1 star.',
      author: 'James Wilson',
      date: '3 days ago',
      readTime: '4 min read',
      image: 'https://via.placeholder.com/600x400/0ea5e9/ffffff?text=Chelsea+Target',
      views: 9800,
      likes: 234,
      comments: 67,
      trending: false,
      content: `Chelsea are preparing a significant bid for one of France's most promising defenders as they look to rebuild their backline.

      The 22-year-old has impressed in Ligue 1 this season, earning comparisons to some of the game's best center-backs.

      Negotiations are expected to begin in the coming weeks, with Chelsea confident of completing the deal before pre-season.`
    }
  ];

  const trendingArticles = articles.filter(a => a.trending);
  
  const filteredArticles = articles.filter(article => {
    const matchesCategory = activeCategory === 'all' || article.category === activeCategory;
    const matchesSearch = article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          article.excerpt.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const formatNumber = (num) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num;
  };

  return (
    <div className="news-page">
      <main className="main-content">
        <header className="page-header">
          <div className="header-left">
            <h1>
              <Newspaper size={28} />
              News & Articles
            </h1>
            <p>Stay updated with the latest football news from around the world</p>
          </div>
          <div className="search-box">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </header>

        {/* Category Tabs */}
        <div className="category-tabs">
          {categories.map(cat => (
            <button
              key={cat.id}
              className={`category-btn ${activeCategory === cat.id ? 'active' : ''}`}
              onClick={() => setActiveCategory(cat.id)}
            >
              {cat.label}
            </button>
          ))}
        </div>

        <div className="news-layout">
          {/* Main Articles */}
          <div className="articles-section">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeCategory}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="articles-grid"
              >
                {filteredArticles.map((article, index) => (
                  <motion.article
                    key={article.id}
                    className={`article-card ${index === 0 ? 'featured' : ''}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={() => setSelectedArticle(article)}
                    whileHover={{ y: -5 }}
                  >
                    <div className="article-image">
                      <img src={article.image} alt={article.title} />
                      <span className="category-badge">{article.category.replace('-', ' ')}</span>
                      {article.trending && (
                        <span className="trending-badge">
                          <TrendingUp size={12} /> Trending
                        </span>
                      )}
                    </div>
                    <div className="article-content">
                      <h3>{article.title}</h3>
                      <p>{article.excerpt}</p>
                      <div className="article-meta">
                        <div className="author-info">
                          <User size={14} />
                          <span>{article.author}</span>
                        </div>
                        <div className="meta-right">
                          <span><Clock size={14} /> {article.readTime}</span>
                          <span><Eye size={14} /> {formatNumber(article.views)}</span>
                        </div>
                      </div>
                      <div className="article-actions">
                        <button className="action-btn">
                          <ThumbsUp size={14} /> {article.likes}
                        </button>
                        <button className="action-btn">
                          <MessageCircle size={14} /> {article.comments}
                        </button>
                        <button className="action-btn">
                          <Share2 size={14} />
                        </button>
                        <button className="action-btn">
                          <Bookmark size={14} />
                        </button>
                      </div>
                    </div>
                  </motion.article>
                ))}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Sidebar */}
          <aside className="news-sidebar">
            <div className="sidebar-section">
              <h3><TrendingUp size={18} /> Trending Now</h3>
              <div className="trending-list">
                {trendingArticles.map((article, index) => (
                  <div 
                    key={article.id} 
                    className="trending-item"
                    onClick={() => setSelectedArticle(article)}
                  >
                    <span className="trending-rank">{index + 1}</span>
                    <div className="trending-info">
                      <h4>{article.title}</h4>
                      <span>{article.views.toLocaleString()} views</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="sidebar-section">
              <h3><Filter size={18} /> Quick Links</h3>
              <div className="quick-links">
                <a href="#" className="quick-link">
                  Transfer Deadline Day Coverage <ChevronRight size={16} />
                </a>
                <a href="#" className="quick-link">
                  Champions League Updates <ChevronRight size={16} />
                </a>
                <a href="#" className="quick-link">
                  Premier League Table <ChevronRight size={16} />
                </a>
                <a href="#" className="quick-link">
                  Top Goal Scorers <ChevronRight size={16} />
                </a>
              </div>
            </div>
          </aside>
        </div>

        {/* Article Modal */}
        <AnimatePresence>
          {selectedArticle && (
            <motion.div
              className="article-modal-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedArticle(null)}
            >
              <motion.div
                className="article-modal"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={e => e.stopPropagation()}
              >
                <button className="close-modal" onClick={() => setSelectedArticle(null)}>×</button>
                <img src={selectedArticle.image} alt={selectedArticle.title} />
                <div className="modal-content">
                  <span className="category-badge">{selectedArticle.category.replace('-', ' ')}</span>
                  <h2>{selectedArticle.title}</h2>
                  <div className="modal-meta">
                    <span><User size={14} /> {selectedArticle.author}</span>
                    <span><Clock size={14} /> {selectedArticle.date}</span>
                    <span><Eye size={14} /> {selectedArticle.views.toLocaleString()} views</span>
                  </div>
                  <div className="modal-body">
                    {selectedArticle.content.split('\n\n').map((para, i) => (
                      <p key={i}>{para.trim()}</p>
                    ))}
                  </div>
                  <div className="modal-actions">
                    <button className="action-btn"><ThumbsUp size={16} /> Like</button>
                    <button className="action-btn"><Share2 size={16} /> Share</button>
                    <button className="action-btn"><Bookmark size={16} /> Save</button>
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

export default NewsPage;
