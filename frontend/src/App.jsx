import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import DigitalTwin from './pages/DigitalTwin';
import Energy from './pages/Energy';
import Water from './pages/Water';
import Traffic from './pages/Traffic';
import Facilities from './pages/Facilities';
import Alerts from './pages/Alerts';
import Analytics from './pages/Analytics';
import DataManagement from './pages/DataManagement';

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user, token } = useAuth();
  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }
  if (adminOnly && user.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
};

const PageLayout = () => {
  const location = useLocation();
  const getTitle = (path) => {
    switch(path) {
      case '/dashboard': return 'Campus Dashboard';
      case '/digital-twin': return 'Digital Twin 3D/Map View';
      case '/energy': return 'Energy Intelligence';
      case '/water': return 'Water Management';
      case '/traffic': return 'Traffic & Parking';
      case '/facilities': return 'Facilities & Space';
      case '/alerts': return 'Alerts & Anomalies';
      case '/analytics': return 'Cross Analytics';
      case '/data-management': return 'Data Management & ML Retrain';
      default: return 'Smart Campus Digital Twin';
    }
  };

  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        <TopBar pageTitle={getTitle(location.pathname)} />
        <div className="page-body">
          <Routes>
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/digital-twin" element={<ProtectedRoute><DigitalTwin /></ProtectedRoute>} />
            <Route path="/energy" element={<ProtectedRoute><Energy /></ProtectedRoute>} />
            <Route path="/water" element={<ProtectedRoute><Water /></ProtectedRoute>} />
            <Route path="/traffic" element={<ProtectedRoute><Traffic /></ProtectedRoute>} />
            <Route path="/facilities" element={<ProtectedRoute><Facilities /></ProtectedRoute>} />
            <Route path="/alerts" element={<ProtectedRoute><Alerts /></ProtectedRoute>} />
            <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
            <Route path="/data-management" element={<ProtectedRoute adminOnly={true}><DataManagement /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/*" element={<PageLayout />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
