import React, { useState, useEffect } from 'react';
import api from '../services/api';
import Modal from '../components/Modal';
import Skeleton from '../components/Skeleton';
import EmptyState from '../components/EmptyState';
import { AlertTriangle, CheckCircle, ShieldAlert, Filter, Check } from 'lucide-react';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [resolutionNotes, setResolutionNotes] = useState('Inspected and fixed by operator');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await api.get('/alerts');
      setAlerts(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleResolveClick = (alert) => {
    setSelectedAlert(alert);
    setIsModalOpen(true);
  };

  const confirmResolve = async () => {
    if (!selectedAlert) return;
    try {
      await api.put(`/alerts/${selectedAlert.alert_id}/resolve`, { resolution_notes: resolutionNotes });
      setIsModalOpen(false);
      setSelectedAlert(null);
      fetchAlerts();
    } catch (err) {
      console.error(err);
    }
  };

  const filteredAlerts = alerts.filter(a => {
    if (statusFilter === 'all') return true;
    return a.status === statusFilter;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ padding: '10px', background: 'rgba(239, 68, 68, 0.15)', borderRadius: '10px', color: '#ef4444' }}>
            <AlertTriangle size={22} />
          </div>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)' }}>System Alerts & Anomaly Incidents</h2>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Automated anomaly detection alerts & operator resolution workflow</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Filter size={16} style={{ color: 'var(--text-muted)' }} />
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ padding: '8px 14px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: '13px', fontWeight: '600' }}
          >
            <option value="all">All Alerts</option>
            <option value="active">Active Only</option>
            <option value="resolved">Resolved Only</option>
          </select>
        </div>
      </div>

      <div className="card">
        {loading ? <Skeleton height="300px" /> : (
          filteredAlerts.length === 0 ? (
            <EmptyState title="No alerts found" description="There are no active or resolved alerts matching your criteria." />
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Alert ID</th>
                    <th>Building</th>
                    <th>Metric</th>
                    <th>Severity</th>
                    <th>Description</th>
                    <th>Created At</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAlerts.map(alt => (
                    <tr key={alt.alert_id}>
                      <td style={{ fontWeight: '600' }}>{alt.alert_id}</td>
                      <td>{alt.building_name || alt.building_id}</td>
                      <td style={{ textTransform: 'capitalize' }}>{alt.metric || alt.type || 'General'}</td>
                      <td>
                        <span className={`badge ${alt.severity === 'high' ? 'badge-danger' : 'badge-warning'}`}>
                          {alt.severity}
                        </span>
                      </td>
                      <td style={{ fontSize: '13px', maxWidth: '300px' }}>{alt.description || alt.message || 'System anomaly detected.'}</td>
                      <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{new Date(alt.created_at).toLocaleString()}</td>
                      <td>
                        <span className={`badge ${alt.status === 'resolved' ? 'badge-success' : 'badge-danger'}`}>
                          {alt.status}
                        </span>
                      </td>
                      <td>
                        {alt.status === 'active' ? (
                          <button 
                            onClick={() => handleResolveClick(alt)}
                            className="btn btn-primary"
                            style={{ fontSize: '12px', padding: '6px 12px' }}
                          >
                            <Check size={14} /> Resolve
                          </button>
                        ) : (
                          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Resolved</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </div>

      {/* Resolve Confirmation Modal */}
      <Modal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)}
        title={`Resolve Alert: ${selectedAlert?.alert_id}`}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Confirm resolving alert for <b>{selectedAlert?.building_name}</b>.
          </p>
          <div>
            <label style={{ fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '6px' }}>Resolution Notes</label>
            <textarea 
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
              rows={3}
              style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)', fontSize: '13px', outline: 'none' }}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button onClick={() => setIsModalOpen(false)} className="btn btn-secondary">Cancel</button>
            <button onClick={confirmResolve} className="btn btn-primary">Confirm Resolution</button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Alerts;
