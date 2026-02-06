import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import SchedulePage from './pages/SchedulePage'
import ProfilesPage from './pages/ProfilesPage'
import StandingsPage from './pages/StandingsPage'
import FantasyPage from './pages/FantasyPage'
import NewsPage from './pages/NewsPage'
import HighlightsPage from './pages/HighlightsPage'
import OddsPage from './pages/OddsPage'
import Sidebar from './components/Sidebar'
import Notifications from './components/Notifications'
import ErrorBoundary from './components/ErrorBoundary'
import { AppProvider } from './context/AppContext'
import './App.css'

function App() {
  return (
    <ErrorBoundary>
    <Router>
      <AppProvider>
        <Notifications />
        <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/schedule" element={
          <div className="app-layout">
            <Sidebar isOpen={true} />
            <SchedulePage />
          </div>
        } />
        <Route path="/profiles" element={
          <div className="app-layout">
            <Sidebar isOpen={true} />
            <ProfilesPage />
          </div>
        } />
        <Route path="/fantasy" element={
          <div className="app-layout">
            <Sidebar isOpen={true} />
            <FantasyPage />
          </div>
        } />
        <Route path="/news" element={
          <div className="app-layout">
            <Sidebar isOpen={true} />
            <NewsPage />
          </div>
        } />
        <Route path="/highlights" element={
          <div className="app-layout">
            <Sidebar isOpen={true} />
            <HighlightsPage />
          </div>
        } />
        <Route path="/odds" element={
          <div className="app-layout">
            <Sidebar isOpen={true} />
            <OddsPage />
          </div>
        } />
        <Route path="/predictions" element={
          <div className="app-layout">
            <Sidebar isOpen={true} />
            <OddsPage />
          </div>
        } />
        <Route path="/standings" element={
          <div className="app-layout">
            <Sidebar isOpen={true} />
            <StandingsPage />
          </div>
        } />
        </Routes>
      </AppProvider>
    </Router>
    </ErrorBoundary>
  )
}

export default App
