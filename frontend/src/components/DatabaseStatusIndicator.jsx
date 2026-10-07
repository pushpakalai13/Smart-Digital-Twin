import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Database, CheckCircle2, AlertTriangle } from 'lucide-react';

const DatabaseStatusIndicator = () => {
  const [dbStatus, setDbStatus] = useState('checking');

  const checkHealth = async () => {
    try {
      const res = await api.get('/health');
      setDbStatus(res.data.database || 'disconnected');
    } catch (err) {
      setDbStatus('disconnected');
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000); // Poll health every 15s
    return () => clearInterval(interval);
  }, []);

  const isConnected = dbStatus === 'connected';

  return (
    <div 
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
        isConnected 
          ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30' 
          : 'bg-rose-500/10 text-rose-500 border-rose-500/30'
      }`}
      title={isConnected ? 'MongoDB Atlas is connected and healthy' : 'MongoDB Atlas is disconnected or unreachable'}
    >
      <Database className="w-3.5 h-3.5" />
      <span>{isConnected ? 'Atlas Connected' : 'Atlas Offline'}</span>
      <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}></span>
    </div>
  );
};

export default DatabaseStatusIndicator;
