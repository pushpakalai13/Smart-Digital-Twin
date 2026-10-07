import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import Skeleton from '../components/Skeleton';
import EmptyState from '../components/EmptyState';
import { Building2, Users, Sparkles, Lightbulb, CheckCircle2 } from 'lucide-react';

const Facilities = () => {
  const [facilities, setFacilities] = useState([]);
  const [selectedFacilityId, setSelectedFacilityId] = useState('F001');
  const [occupancyData, setOccupancyData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [showPredictions, setShowPredictions] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFacilities = async () => {
      try {
        const res = await api.get('/facilities');
        const facList = res.data || [];
        setFacilities(facList);
        if (facList.length > 0 && !facList.some(f => f.facility_id === selectedFacilityId)) {
          setSelectedFacilityId(facList[0].facility_id);
        }
      } catch (err) {
        console.error('Error fetching facilities:', err);
      }
    };
    fetchFacilities();
  }, []);

  useEffect(() => {
    const selectedFacility = facilities.find(f => f.facility_id === selectedFacilityId);
    const targetBid = selectedFacility?.building_id || selectedFacilityId;

    const fetchTelemetryAndPred = async () => {
      setLoading(true);
      try {
        const [occRes, pRes] = await Promise.all([
          api.get(`/occupancy?facility_id=${selectedFacilityId}&building_id=${targetBid}&limit=72`),
          api.get(`/occupancy/predict/${selectedFacilityId}`)
        ]);
        setOccupancyData(occRes.data || []);
        setPredictions(pRes.data.predictions || []);
      } catch (err) {
        console.error('Error fetching occupancy data/prediction:', err);
      } finally {
        setLoading(false);
      }
    };

    if (selectedFacilityId) {
      fetchTelemetryAndPred();
    }
  }, [selectedFacilityId, facilities]);

  const formatChartTimestamp = (ts) => {
    if (!ts) return '';
    const dt = new Date(ts);
    return `${dt.getDate()} ${dt.toLocaleString('en-US', { month: 'short' })}, ${dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  };

  const actualPoints = (occupancyData || []).map((d, idx, arr) => ({
    timestamp: formatChartTimestamp(d.timestamp),
    actual: d.value ?? d.occupancy_count ?? 0,
    predicted: idx === arr.length - 1 ? (d.value ?? d.occupancy_count ?? 0) : null
  }));

  const predPoints = (predictions || []).map(p => ({
    timestamp: formatChartTimestamp(p.timestamp),
    actual: null,
    predicted: p.predicted_occupancy ?? 0
  }));

  const combinedChartData = [...actualPoints, ...predPoints];

  const selectedFac = facilities.find(f => f.facility_id === selectedFacilityId) || facilities[0];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header & Controls */}
      <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ padding: '10px', background: 'rgba(99, 102, 241, 0.15)', borderRadius: '10px', color: '#6366f1' }}>
            <Building2 size={22} />
          </div>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)' }}>Facilities & Space Utilization Analytics</h2>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Live space occupancy monitoring, utilization rates, and 24h AI predictive forecast</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Facility Selector Dropdown */}
          <select 
            value={selectedFacilityId}
            onChange={(e) => setSelectedFacilityId(e.target.value)}
            style={{
              padding: '8px 14px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              backgroundColor: 'var(--bg-secondary)',
              color: 'var(--text-primary)',
              fontSize: '13px',
              fontWeight: '600',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {facilities.map(f => (
              <option key={f.facility_id} value={f.facility_id}>
                {f.name} ({f.facility_id} • {f.building_id})
              </option>
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

      {/* Summary Cards for ALL 5 Facilities */}
      <div>
        <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '12px' }}>
          All Campus Facilities Overview (Click any card to view detailed telemetry)
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
          {facilities.map((f) => {
            const isSelected = f.facility_id === selectedFacilityId;
            return (
              <div 
                key={f.facility_id} 
                className="card card-hover" 
                onClick={() => setSelectedFacilityId(f.facility_id)}
                style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  gap: '12px',
                  cursor: 'pointer',
                  border: isSelected ? '2px solid #6366f1' : '1px solid var(--border-color)',
                  backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.04)' : 'var(--bg-secondary)',
                  boxShadow: isSelected ? '0 4px 12px rgba(99, 102, 241, 0.15)' : 'none',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className={`badge ${f.status === 'critical' ? 'badge-danger' : (f.status === 'warning' ? 'badge-warning' : 'badge-success')}`} style={{ textTransform: 'uppercase' }}>
                    {f.status?.toUpperCase() || 'NORMAL'}
                  </span>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{f.facility_id} • {f.building_id}</span>
                </div>

                <div>
                  <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)' }}>{f.name}</h3>
                  <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Type: {f.type}</p>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', background: 'var(--bg-primary)', padding: '8px 10px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Current Occupancy</span>
                    <div style={{ fontSize: '15px', fontWeight: '800', color: 'var(--text-primary)' }}>
                      {f.current_occupancy_count ?? 'N/A'} ppl
                    </div>
                  </div>
                  <div>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Utilization Rate</span>
                    <div style={{ fontSize: '15px', fontWeight: '800', color: f.status === 'critical' ? '#ef4444' : (f.status === 'warning' ? '#f59e0b' : '#10b981') }}>
                      {f.current_occupancy_rate ?? 0}%
                    </div>
                  </div>
                </div>

                {f.recommended_action && (
                  <div style={{ padding: '8px 10px', borderRadius: '6px', backgroundColor: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', fontSize: '11px' }}>
                    <span style={{ fontWeight: '700', color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                      <Lightbulb size={13} /> Recommended Action:
                    </span>
                    <span style={{ color: 'var(--text-primary)' }}>{f.recommended_action}</span>
                  </div>
                )}

                <div style={{ marginTop: 'auto', paddingTop: '8px', borderTop: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                    <Users size={14} />
                    <span>Max Capacity:</span>
                  </div>
                  <span style={{ fontSize: '14px', fontWeight: '700', color: 'var(--text-primary)' }}>{f.capacity} Seats</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Occupancy & Prediction Chart */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)' }}>
            Occupancy Telemetry & 24h AI Forecast — {selectedFac?.name} ({selectedFac?.facility_id} • {selectedFac?.building_id})
          </h3>
          <span className={`badge ${selectedFac?.status === 'critical' ? 'badge-danger' : (selectedFac?.status === 'warning' ? 'badge-warning' : 'badge-success')}`}>
            {selectedFac?.status?.toUpperCase() || 'NORMAL'} STATUS
          </span>
        </div>

        {loading ? (
          <Skeleton height="350px" />
        ) : combinedChartData.length === 0 ? (
          <EmptyState title="No occupancy telemetry available" description="No space utilization records logged for this facility." />
        ) : (
          <div style={{ width: '100%', height: '380px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={combinedChartData}>
                <defs>
                  <linearGradient id="colorActualOccupancy" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorPredOccupancy" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ec4899" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#ec4899" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                <XAxis dataKey="timestamp" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} unit=" ppl" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)' }} />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="actual" 
                  name={`Historical Occupancy - ${selectedFac?.name} (People)`} 
                  stroke="#6366f1" 
                  strokeWidth={2.5} 
                  fillOpacity={1} 
                  fill="url(#colorActualOccupancy)" 
                />
                {showPredictions && (
                  <Area 
                    type="monotone" 
                    dataKey="predicted" 
                    name={`24h AI Occupancy Forecast - ${selectedFac?.name} (People)`} 
                    stroke="#ec4899" 
                    strokeWidth={2.5} 
                    strokeDasharray="5 5" 
                    fillOpacity={1} 
                    fill="url(#colorPredOccupancy)" 
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

export default Facilities;
