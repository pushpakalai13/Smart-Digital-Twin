import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Cpu, Lock, Mail, ShieldAlert, ArrowRight } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('admin@smartcampus.edu');
  const [password, setPassword] = useState('ALxM21AllspN');
  const [error, setError] = useState('');
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const res = await login(email, password);
    if (res.success) {
      navigate('/dashboard');
    } else {
      setError(res.message);
    }
  };

  const fillPreset = (type) => {
    if (type === 'admin') {
      setEmail('admin@smartcampus.edu');
      setPassword('ALxM21AllspN');
    } else {
      setEmail('staff@smartcampus.edu');
      setPassword('SLxM21AllspF');
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-primary)' }}>
      {/* Left Branding Side */}
      <div 
        style={{
          flex: 1.2,
          background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #2563eb 100%)',
          color: '#ffffff',
          padding: '60px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ padding: '10px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '12px', backdropFilter: 'blur(10px)' }}>
            <Cpu size={28} />
          </div>
          <span style={{ fontSize: '22px', fontWeight: '800', letterSpacing: '-0.5px' }}>SmartCampus Digital Twin</span>
        </div>

        <div>
          <h2 style={{ fontSize: '36px', fontWeight: '800', lineHeight: 1.2, marginBottom: '20px' }}>
            Predictive Intelligence & Multi-Resource Optimization
          </h2>
          <p style={{ fontSize: '16px', color: '#94a3b8', maxWidth: '480px', lineHeight: 1.6 }}>
            Unified real-time IoT monitoring, anomaly detection, machine learning load forecasting, and digital twin simulation for energy, water, traffic, and facility management.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '24px', fontSize: '13px', color: '#cbd5e1' }}>
          <div>⚡ Machine Learning Load Forecasting</div>
          <div>💧 Water Leak Detection</div>
          <div>🚗 Traffic Optimization</div>
        </div>
      </div>

      {/* Right Form Side */}
      <div 
        style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px'
        }}
      >
        <div style={{ maxWidth: '400px', width: '100%' }}>
          <div style={{ marginBottom: '32px' }}>
            <h2 style={{ fontSize: '26px', fontWeight: '800', color: 'var(--text-primary)', marginBottom: '8px' }}>Operator Sign In</h2>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Access the smart campus digital twin dashboard</p>
          </div>

          {error && (
            <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--danger)', padding: '12px', borderRadius: '8px', fontSize: '13px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={16} />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '6px' }}>Email Address</label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-muted)' }} />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '10px 12px 10px 36px',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)',
                    backgroundColor: 'var(--bg-secondary)',
                    color: 'var(--text-primary)',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '6px' }}>Password</label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-muted)' }} />
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '10px 12px 10px 36px',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)',
                    backgroundColor: 'var(--bg-secondary)',
                    color: 'var(--text-primary)',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                />
              </div>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading}
              style={{ width: '100%', padding: '12px', marginTop: '8px', fontSize: '15px' }}
            >
              {loading ? 'Authenticating...' : 'Sign In to Dashboard'}
              <ArrowRight size={18} />
            </button>
          </form>

          {/* Quick Demo Presets */}
          <div style={{ marginTop: '32px', paddingTop: '24px', borderTop: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-muted)', display: 'block', marginBottom: '12px' }}>DEMO ACCOUNTS PRESETS</span>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                type="button" 
                onClick={() => fillPreset('admin')}
                style={{ flex: 1, padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: '12px', fontWeight: '600', cursor: 'pointer' }}
              >
                Admin Preset
              </button>
              <button 
                type="button" 
                onClick={() => fillPreset('staff')}
                style={{ flex: 1, padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: '12px', fontWeight: '600', cursor: 'pointer' }}
              >
                Staff Preset
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
