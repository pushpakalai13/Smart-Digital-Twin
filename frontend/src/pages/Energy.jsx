import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import Skeleton from '../components/Skeleton';
import EmptyState from '../components/EmptyState';
import { Zap, Sparkles } from 'lucide-react';

const Energy = () => {
  const [buildings, setBuildings] = useState([]);
  const [selectedBuilding, setSelectedBuilding] = useState('B001');
  const [energyData, setEnergyData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [showPredictions, setShowPredictions] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initData = async () => {
      try {
        const bRes = await api.get('/buildings');
        setBuildings(bRes.data);
      } catch (err) {
        console.error(err);
      }
    };
    initData();
  }, []);

  useEffect(() => {
    const fetchEnergyAndPred = async () => {
      setLoading(true);
      try {
        const eRes = await api.get(`/energy/${selectedBuilding}?limit=72`);
        setEnergyData(eRes.data || []);

        const pRes = await api.get(`/energy/predict/${selectedBuilding}?hours=24`);
        setPredictions(pRes.data.predictions || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchEnergyAndPred();
  }, [selectedBuilding]);

  const formatChartTimestamp = (ts) => {
    if (!ts) return '';
    const dt = new Date(ts);
    return `${dt.getDate()} ${dt.toLocaleString('en-US', { month: 'short' })}, ${dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  };

  const actualPoints = (energyData || []).map((d, idx, arr) => ({
    timestamp: formatChartTimestamp(d.timestamp),
    actual: d.value,
    predicted: idx === arr.length - 1 ? d.value : null
  }));

  const predPoints = (predictions || []).map(p => ({
    timestamp: formatChartTimestamp(p.timestamp),
    actual: null,
    predicted: p.predicted_kwh
  }));

  const combinedChartData = [...actualPoints, ...predPoints];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header & Controls */}
      <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ padding: '10px', background: 'rgba(37, 99, 235, 0.15)', borderRadius: '10px', color: '#2563eb' }}>
            <Zap size={22} />
          </div>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)' }}>Energy Analytics & Load Forecasting</h2>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Hourly electricity consumption patterns and ML predictive load overlay</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <select 
            value={selectedBuilding}
            onChange={(e) => setSelectedBuilding(e.target.value)}
            style={{
              padding: '8px 14px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              backgroundColor: 'var(--bg-secondary)',
              color: 'var(--text-primary)',
              fontSize: '13px',
              fontWeight: '600',
              outline: 'none'
            }}
          >
            {buildings.map(b => (
              <option key={b.building_id} value={b.building_id}>{b.name} ({b.building_id})</option>
            ))}
          </select>

          <button 
            onClick={() => setShowPredictions(!showPredictions)}
            className={`btn ${showPredictions ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '13px', padding: '8px 14px' }}
          >
            <Sparkles size={16} />
            <span>{showPredictions ? 'Hide AI Predictions' : 'Show 24h AI Forecast'}</span>
          </button>
        </div>
      </div>

      {/* Main Energy Chart */}
      <div className="card">
        <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px' }}>
          Consumption (kWh) Over Time
        </h3>
        {loading ? (
          <Skeleton height="350px" />
        ) : combinedChartData.length === 0 ? (
          <EmptyState title="No energy telemetry available" description="No consumption records found for this building." />
        ) : (
          <div style={{ width: '100%', height: '380px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={combinedChartData}>
                <defs>
                  <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorPred" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0891b2" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#0891b2" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                <XAxis dataKey="timestamp" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} unit=" kWh" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)' }} />
                <Legend />
                <Area type="monotone" dataKey="actual" name="Historical Load (kWh)" stroke="#2563eb" strokeWidth={2} fillOpacity={1} fill="url(#colorActual)" />
                {showPredictions && (
                  <Area type="monotone" dataKey="predicted" name="24h AI Load Forecast (kWh)" stroke="#0891b2" strokeWidth={2} strokeDasharray="5 5" fillOpacity={1} fill="url(#colorPred)" />
                )}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default Energy;
