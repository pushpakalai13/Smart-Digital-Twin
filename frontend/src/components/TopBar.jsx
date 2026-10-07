import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import DatabaseStatusIndicator from './DatabaseStatusIndicator';
import api from '../services/api';
import { Sun, Moon, Bell, LogOut, Search, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const TopBar = ({ pageTitle = "Overview" }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [alertCount, setAlertCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAlertCount = async () => {
      try {
        const res = await api.get('/alerts?status=active');
        setAlertCount(res.data.length || 0);
      } catch (err) {
        setAlertCount(0);
      }
    };
    fetchAlertCount();
    const timer = setInterval(fetchAlertCount, 20000);
    return () => clearInterval(timer);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    const q = searchQuery.trim().toLowerCase();
    if (!q) return;

    if (q.includes('dashboard') || q.includes('home') || q.includes('overview') || q.includes('summary')) {
      navigate('/dashboard');
    } else if (q.includes('energy') || q.includes('power') || q.includes('kwh') || q.includes('electricity') || q.includes('solar')) {
      navigate('/energy');
    } else if (q.includes('water') || q.includes('flow') || q.includes('litre') || q.includes('liter') || q.includes('pipe') || q.includes('leak')) {
      navigate('/water');
    } else if (q.includes('traffic') || q.includes('parking') || q.includes('vehicle') || q.includes('car') || q.includes('slot') || q.includes('gate')) {
      navigate('/traffic');
    } else if (q.includes('facility') || q.includes('facilities') || q.includes('room') || q.includes('space') || q.includes('capacity')) {
      navigate('/facilities');
    } else if (q.includes('alert') || q.includes('incident') || q.includes('anomaly') || q.includes('issue') || q.includes('warning')) {
      navigate('/alerts');
    } else if (q.includes('analytics') || q.includes('ranking') || q.includes('intensity') || q.includes('report') || q.includes('chart') || q.includes('insight')) {
      navigate('/analytics');
    } else if (q.includes('data') || q.includes('upload') || q.includes('dataset') || q.includes('import') || q.includes('csv') || q.includes('retrain')) {
      navigate('/data-management');
    } else {
      // Default mapping for campus buildings, hostels, library, twin, map -> Digital Twin Map with building highlight
      navigate(`/digital-twin?search=${encodeURIComponent(q)}`);
    }
  };

  return (
    <header 
      style={{
        height: '64px',
        backgroundColor: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-color)',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 40
      }}
    >
      {/* Title & Search */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        <h1 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)' }}>{pageTitle}</h1>
        <form onSubmit={handleSearch} style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
          <Search size={16} style={{ position: 'absolute', left: '10px', color: 'var(--text-muted)', cursor: 'pointer' }} onClick={handleSearch} />
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search campus metrics or buildings..." 
            style={{
              padding: '6px 12px 6px 32px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              backgroundColor: 'var(--bg-primary)',
              color: 'var(--text-primary)',
              fontSize: '13px',
              outline: 'none',
              width: '240px',
              transition: 'all 0.2s ease'
            }}
          />
        </form>
      </div>

      {/* Right Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Atlas Health Indicator */}
        <DatabaseStatusIndicator />

        {/* Theme Toggle */}
        <button 
          onClick={toggleTheme}
          style={{
            background: 'var(--bg-primary)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-primary)',
            padding: '8px',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          title="Toggle Light/Dark Theme"
        >
          {theme === 'dark' ? <Sun size={18} className="text-amber-400" /> : <Moon size={18} className="text-indigo-600" />}
        </button>

        {/* Alerts Bell */}
        <button 
          onClick={() => navigate('/alerts')}
          style={{
            position: 'relative',
            background: 'var(--bg-primary)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-primary)',
            padding: '8px',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          title="View Active Alerts"
        >
          <Bell size={18} />
          {alertCount > 0 && (
            <span 
              style={{
                position: 'absolute',
                top: '-4px',
                right: '-4px',
                backgroundColor: 'var(--danger)',
                color: '#fff',
                fontSize: '10px',
                fontWeight: 'bold',
                width: '18px',
                height: '18px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              {alertCount}
            </span>
          )}
        </button>

        {/* Logout */}
        <button 
          onClick={logout}
          style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: 'var(--danger)',
            padding: '8px 12px',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '13px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </div>
    </header>
  );
};

export default TopBar;
