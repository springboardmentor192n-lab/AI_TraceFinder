import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import Results from './pages/Results';
import Dashboard from './pages/Dashboard';
import Tamper from './pages/Tamper';
import Features from './pages/Features';
import History from './pages/History';
import Groups from './pages/Groups';
import About from './pages/About';
import Auth from './components/Auth';
import { User, LogOut } from 'lucide-react';
import './App.css';

function AppContent() {
  const [history, setHistory] = useState([]);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const location = useLocation();

  // Load history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('tracefinder-history');
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }

    // Check authentication status
    const authStatus = localStorage.getItem('tracefinder-auth');
    const userData = localStorage.getItem('tracefinder-user');
    
    if (authStatus === 'true' && userData) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userData));
    }
  }, []);

  // Save history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('tracefinder-history', JSON.stringify(history));
  }, [history]);

  const handleLogout = () => {
    localStorage.removeItem('tracefinder-auth');
    localStorage.removeItem('tracefinder-user');
    setIsAuthenticated(false);
    setUser(null);
    triggerToast('Logged out successfully', 'success');
  };

  const addToHistory = (analysis) => {
    const newEntry = {
      ...analysis,
      id: Date.now(),
      timestamp: new Date().toISOString(),
    };
    setHistory(prev => [newEntry, ...prev]);
  };

  const triggerToast = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // If not authenticated, show auth screen
  if (!isAuthenticated) {
    return <Auth setIsAuthenticated={setIsAuthenticated} />;
  }

  return (
    <div className="page-shell">
      <header>
        <div className="brand" style={{ cursor: 'pointer' }} onClick={() => window.location.href = '/'}>
          <div className="brand-icon">🔬</div>
          <div className="brand-text">
            <span>TraceFinder</span>
          </div>
        </div>
        <nav>
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
            Home
          </Link>
          <Link to="/dashboard" className={location.pathname === '/dashboard' ? 'active' : ''}>
            Dashboard
          </Link>
          <Link to="/history" className={location.pathname === '/history' ? 'active' : ''}>
            History
          </Link>
          <Link to="/groups" className={location.pathname === '/groups' ? 'active' : ''}>
            Groups
          </Link>
          <Link to="/about" className={location.pathname === '/about' ? 'active' : ''}>
            About
          </Link>
        </nav>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            padding: '8px 12px',
            backgroundColor: 'var(--surface-soft)',
            borderRadius: '12px',
            fontSize: '0.9rem'
          }}>
            <User size={16} />
            <span>{user?.name || 'User'}</span>
          </div>
          <button
            onClick={handleLogout}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 12px',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              backgroundColor: 'white',
              cursor: 'pointer',
              fontSize: '0.9rem',
              color: 'var(--muted)'
            }}
            title="Logout"
          >
            <LogOut size={16} />
          </button>
        </div>
      </header>

      <Routes>
        <Route path="/" element={<Home onAnalysis={addToHistory} triggerToast={triggerToast} />} />
        <Route path="/results" element={<Results triggerToast={triggerToast} />} />
        <Route path="/dashboard" element={<Dashboard history={history} />} />
        <Route path="/tamper" element={<Tamper triggerToast={triggerToast} />} />
        <Route path="/features" element={<Features triggerToast={triggerToast} />} />
        <Route path="/history" element={<History history={history} setHistory={setHistory} triggerToast={triggerToast} />} />
        <Route path="/groups" element={<Groups history={history} triggerToast={triggerToast} />} />
        <Route path="/about" element={<About />} />
      </Routes>

      {showToast && (
        <div className={`toast ${toastType}`}>
          <span>{toastType === 'success' ? '✓' : toastType === 'warning' ? '⚠' : 'ℹ'}</span>
          <span>{toastMessage}</span>
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
