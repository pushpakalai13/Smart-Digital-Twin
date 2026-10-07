import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import Skeleton from '../components/Skeleton';
import { BarChart3, Trophy } from 'lucide-react';

const Analytics = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await api.get('/analytics');
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) return <Skeleton height="500px" />;

  const rankings = data?.building_rankings || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ padding: '10px', background: 'rgba(168, 85, 247, 0.15)', borderRadius: '10px', color: '#a855f7' }}>
          <BarChart3 size={22} />
        </div>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)' }}>Cross-Resource Analytics & Building Rankings</h2>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Energy & water intensity comparison across all campus blocks</p>
        </div>
      </div>

      <div className="card">
        <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px' }}>24h Energy Load by Building (kWh)</h3>
        <div style={{ width: '100%', height: '350px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rankings}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="building_name" stroke="var(--text-muted)" fontSize={11} interval={0} angle={-15} textAnchor="end" />
              <YAxis stroke="var(--text-muted)" fontSize={11} unit=" kWh" />
              <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)', borderRadius: '8px' }} />
              <Bar dataKey="energy_kwh_24h" name="24h Energy (kWh)" fill="#2563eb" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <Trophy size={18} className="text-amber-400" />
          <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)' }}>Building Energy Intensity Rankings</h3>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Building Name</th>
                <th>Category</th>
                <th>Area (sqft)</th>
                <th>24h Energy (kWh)</th>
                <th>Energy Intensity (kWh/kSqft)</th>
                <th>24h Water (L)</th>
              </tr>
            </thead>
            <tbody>
              {rankings.map((b, idx) => (
                <tr key={b.building_id}>
                  <td style={{ fontWeight: '700', color: idx === 0 ? '#ef4444' : 'var(--text-primary)' }}>#{idx + 1}</td>
                  <td style={{ fontWeight: '600' }}>{b.building_name}</td>
                  <td style={{ textTransform: 'capitalize' }}>{b.category}</td>
                  <td>{b.area_sqft?.toLocaleString()}</td>
                  <td style={{ fontWeight: '700' }}>{b.energy_kwh_24h}</td>
                  <td>{b.energy_intensity}</td>
                  <td>{b.water_litres_24h?.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
