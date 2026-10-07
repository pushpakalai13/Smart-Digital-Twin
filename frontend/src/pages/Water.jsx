import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import Skeleton from '../components/Skeleton';
import EmptyState from '../components/EmptyState';
import { Droplet, Sparkles } from 'lucide-react';

const Water = () => {
  const [buildings, setBuildings] = useState([]);
  const [selectedBuilding, setSelectedBuilding] = useState('B001');
  const [waterData, setWaterData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initData = async () => {
      try {
        const bRes = await api.get('/buildings');
        setBuildings(bRes.data);
      } catch (err) { console.error(err); }
    };
    initData();
  }, []);

  useEffect(() => {
    const fetchWater = async () => {
      setLoading(true);
      try {
        const wRes = await api.get(`/water/${selectedBuilding}?limit=72`);
        setWaterData(wRes.data || []);
        const pRes = await api.get(`/water/predict/${selectedBuilding}?hours=24`);
        setPredictions(pRes.data.predictions || []);
      } catch (err) { console.error(err); }
      finally { setLoading(false); }
    };
    fetchWater();
  }, [selectedBuilding]);

  const formatChartTimestamp = (ts) => {
    if (!ts) return '';
    const dt = new Date(ts);
    return `${dt.getDate()} ${dt.toLocaleString('en-US', { month: 'short' })}, ${dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  };

  const actualPoints = (waterData || []).map((d, idx, arr) => ({
    timestamp: formatChartTimestamp(d.timestamp),
    actual: d.value,
    predicted: idx === arr.length - 1 ? d.value : null
  }));

  const predPoints = (predictions || []).map(p => ({
    timestamp: formatChartTimestamp(p.timestamp),
    actual: null,
    predicted: p.predicted_litres
  }));

  const combinedChartData = [...actualPoints, ...predPoints];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ padding: '10px', background: 'rgba(8, 145, 178, 0.15)', borderRadius: '10px', color: '#0891b2' }}>
            <Droplet size={22} />
          </div>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)' }}>Water Demand & Leak Management</h2>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Water discharge telemetry & predictive leak forecasting</p>
          </div>
        </div>

        <select 
          value={selectedBuilding}
          onChange={(e) => setSelectedBuilding(e.target.value)}
          style={{ padding: '8px 14px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: '13px', fontWeight: '600' }}
        >
          {buildings.map(b => (
            <option key={b.building_id} value={b.building_id}>{b.name} ({b.building_id})</option>
          ))}
        </select>
      </div>

      <div className="card">
        <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px' }}>Water Discharge (Litres)</h3>
        {loading ? <Skeleton height="350px" /> : combinedChartData.length === 0 ? (
          <EmptyState title="No water telemetry available" description="No water discharge records found for this building." />
        ) : (
          <div style={{ width: '100%', height: '380px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={combinedChartData}>
                <defs>
                  <linearGradient id="colorWater" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0891b2" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#0891b2" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                <XAxis dataKey="timestamp" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} unit=" L" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)', borderRadius: '8px' }} />
                <Legend />
                <Area type="monotone" dataKey="actual" name="Water Discharge (L)" stroke="#0891b2" strokeWidth={2} fill="url(#colorWater)" />
                <Area type="monotone" dataKey="predicted" name="Forecasted Demand (L)" stroke="#10b981" strokeWidth={2} strokeDasharray="5 5" fill="none" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default Water;
