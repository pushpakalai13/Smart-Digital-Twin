import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import Skeleton from '../components/Skeleton';
import EmptyState from '../components/EmptyState';
import { Car, ParkingCircle, Sparkles } from 'lucide-react';

const Traffic = () => {
  const [buildings, setBuildings] = useState([]);
  const [selectedBuilding, setSelectedBuilding] = useState('B001');
  const [trafficData, setTrafficData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [parkingData, setParkingData] = useState([]);
  const [showPredictions, setShowPredictions] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initBuildings = async () => {
      try {
        const bRes = await api.get('/buildings');
        setBuildings(bRes.data || []);
      } catch (err) {
        console.error('Error fetching buildings:', err);
      }
    };
    initBuildings();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const tRes = await api.get(`/traffic?building_id=${selectedBuilding}&limit=72`);
        setTrafficData(tRes.data || []);

        const pRes = await api.get(`/traffic/predict/${selectedBuilding}?hours=24`);
        setPredictions(pRes.data.predictions || []);

        const pkRes = await api.get('/parking?limit=24');
        setParkingData(pkRes.data || []);
      } catch (err) {
        console.error('Traffic data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [selectedBuilding]);

  const latestParking = parkingData[0] || { total_slots: 500, occupied_slots: 491, occupancy_rate: 0.982 };
  const parkingTotal = latestParking.total_slots || 500;
  const parkingOccupied = latestParking.occupied_slots ?? 0;
  const parkingOccupancyPct = (latestParking.occupancy_rate != null && !isNaN(latestParking.occupancy_rate))
    ? (latestParking.occupancy_rate * 100).toFixed(1)
    : (parkingTotal > 0 ? ((parkingOccupied / parkingTotal) * 100).toFixed(1) : '0.0');

  const formatChartTimestamp = (ts) => {
    if (!ts) return '';
    const dt = new Date(ts);
    return `${dt.getDate()} ${dt.toLocaleString('en-US', { month: 'short' })}, ${dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  };

  const actualPoints = (trafficData || []).map((d, idx, arr) => ({
    timestamp: formatChartTimestamp(d.timestamp),
    actual: d.value,
    predicted: idx === arr.length - 1 ? d.value : null
  }));

  const predPoints = (predictions || []).map(p => ({
    timestamp: formatChartTimestamp(p.timestamp),
    actual: null,
    predicted: p.predicted_vehicles ?? p.predicted_vehicle_count ?? 0
  }));

  const combinedChartData = [...actualPoints, ...predPoints];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header & Controls */}
      <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ padding: '10px', background: 'rgba(16, 185, 129, 0.15)', borderRadius: '10px', color: '#10b981' }}>
            <Car size={22} />
          </div>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)' }}>Traffic & Parking Intelligence</h2>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Campus vehicle entry telemetry & Random Forest AI flow forecasting</p>
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

      {/* Parking KPI Card */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <ParkingCircle size={36} className="text-emerald-500" />
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Central Parking Lot Capacity</div>
            <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-primary)' }}>
              {parkingOccupied} / {parkingTotal}
            </div>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#10b981', marginTop: '2px' }}>
              {parkingOccupancyPct}% Occupied
            </div>
          </div>
        </div>
      </div>

      {/* Main Traffic & Prediction Chart */}
      <div className="card">
        <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px' }}>
          Vehicle Flow Rate (Vehicles / Hr) Over Time & 24h AI Forecast
        </h3>
        {loading ? (
          <Skeleton height="350px" />
        ) : combinedChartData.length === 0 ? (
          <EmptyState title="No traffic telemetry available" description="No vehicle flow records logged." />
        ) : (
          <div style={{ width: '100%', height: '380px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={combinedChartData}>
                <defs>
                  <linearGradient id="colorActualTraffic" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorPredTraffic" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#a855f7" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                <XAxis dataKey="timestamp" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} unit=" veh/hr" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)' }} />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="actual" 
                  name="Historical Traffic (Vehicles/Hr)" 
                  stroke="#10b981" 
                  strokeWidth={2.5} 
                  fillOpacity={1} 
                  fill="url(#colorActualTraffic)" 
                />
                {showPredictions && (
                  <Area 
                    type="monotone" 
                    dataKey="predicted" 
                    name="24h AI Traffic Forecast (Vehicles/Hr)" 
                    stroke="#a855f7" 
                    strokeWidth={2.5} 
                    strokeDasharray="5 5" 
                    fillOpacity={1} 
                    fill="url(#colorPredTraffic)" 
                  />
                )}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default Traffic;
