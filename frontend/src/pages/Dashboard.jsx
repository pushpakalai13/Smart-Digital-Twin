import React, { useState, useEffect } from 'react';
import api from '../services/api';
import KpiCard from '../components/KpiCard';
import Gauge from '../components/Gauge';
import Skeleton from '../components/Skeleton';
import { Zap, Droplet, Car, AlertTriangle, ShieldCheck, ArrowRight, ToggleLeft, ToggleRight, Sparkles } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [source, setSource] = useState('simulated');
  const navigate = useNavigate();

  const fetchDashboardData = async (src) => {
    setLoading(true);
    try {
      const res = await api.get(`/dashboard${src ? `?source=${src}` : ''}`);
      setData(res.data);
      setSource(res.data.source || 'simulated');
    } catch (err) {
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleSourceToggle = async () => {
    const newSource = source === 'simulated' ? 'uploaded' : 'simulated';
    setSource(newSource);
    try {
      await api.put('/settings/data-source', { source: newSource });
      fetchDashboardData(newSource);
    } catch (err) {
      console.error('Source toggle error:', err);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <Skeleton height="120px" />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          <Skeleton height="100px" />
          <Skeleton height="100px" />
          <Skeleton height="100px" />
          <Skeleton height="100px" />
        </div>
        <Skeleton height="300px" />
      </div>
    );
  }

  const kpis = data?.kpis || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner & Source Toggle */}
      <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--text-primary)' }}>Campus Operations Intelligence</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Real-time monitoring across 10 campus blocks & predictive ML models
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'var(--bg-primary)', padding: '8px 14px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)' }}>Data Source:</span>
          <button 
            onClick={handleSourceToggle}
            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: '700', color: source === 'uploaded' ? 'var(--accent-cyan)' : 'var(--accent-primary)' }}
          >
            {source === 'uploaded' ? <ToggleRight size={24} /> : <ToggleLeft size={24} />}
            <span style={{ textTransform: 'uppercase' }}>{source}</span>
          </button>
        </div>
      </div>

      {/* KPI Cards & Gauge Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <KpiCard 
          title="Energy Consumption (24h)" 
          value={kpis.energy?.total_kwh_24h || 0} 
          unit="kWh" 
          changePct={kpis.energy?.change_pct} 
          trendData={kpis.energy?.trend || []}
          icon={Zap}
          color="#2563eb"
        />
        <KpiCard 
          title="Water Demand (24h)" 
          value={kpis.water?.total_litres_24h || 0} 
          unit="L" 
          changePct={kpis.water?.change_pct} 
          trendData={kpis.water?.trend || []}
          icon={Droplet}
          color="#0891b2"
        />
        <KpiCard 
          title="Traffic Flow Rate" 
          value={kpis.traffic?.avg_vehicles_per_hr || 0} 
          unit="veh/hr" 
          changePct={kpis.traffic?.change_pct} 
          trendData={kpis.traffic?.trend || []}
          icon={Car}
          color="#10b981"
        />
        <KpiCard 
          title="Active Alerts" 
          value={kpis.alerts?.active_count || 0} 
          unit="issues" 
          icon={AlertTriangle}
          color="#ef4444"
        />
      </div>

      {/* Efficiency Gauge & Recommendations */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
        <Gauge score={data?.efficiency_score || 88.5} />

        {/* Top AI Recommendations */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={18} className="text-amber-400" />
              <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)' }}>AI Optimization Recommendations</h3>
            </div>
            <button onClick={() => navigate('/alerts')} style={{ background: 'none', border: 'none', color: 'var(--accent-primary)', fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>View All</button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {(data?.top_recommendations || []).map((rec, i) => (
              <div key={i} style={{ padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-primary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-primary)' }}>{rec.title}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>{rec.description}</div>
                </div>
                <span className="badge badge-warning" style={{ flexShrink: 0 }}>{rec.impact}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Alerts Section */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)' }}>Recent Active System Alerts</h3>
          <button onClick={() => navigate('/alerts')} className="btn btn-secondary" style={{ fontSize: '12px', padding: '6px 12px' }}>
            Manage Alerts <ArrowRight size={14} />
          </button>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Building</th>
                <th>Metric</th>
                <th>Severity</th>
                <th>Description</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {(data?.recent_alerts || []).map((alt) => (
                <tr key={alt.alert_id}>
                  <td style={{ fontWeight: '600' }}>{alt.alert_id}</td>
                  <td>{alt.building_name || alt.building_id}</td>
                  <td style={{ textTransform: 'capitalize' }}>{alt.metric || alt.type || 'General'}</td>
                  <td>
                    <span className={`badge ${alt.severity === 'high' ? 'badge-danger' : 'badge-warning'}`}>
                      {alt.severity}
                    </span>
                  </td>
                  <td style={{ fontSize: '13px' }}>{alt.description || alt.message || 'System anomaly detected.'}</td>
                  <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{new Date(alt.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
