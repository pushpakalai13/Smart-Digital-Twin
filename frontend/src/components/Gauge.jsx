import React from 'react';

const Gauge = ({ score = 88.5, title = "Campus Efficiency Score" }) => {
  const strokeDashoffset = 440 - (440 * score) / 100;
  
  let color = '#10b981';
  if (score < 70) color = '#ef4444';
  else if (score < 85) color = '#f59e0b';

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
      <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '16px' }}>{title}</div>
      <div style={{ position: 'relative', width: '160px', height: '160px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <svg width="160" height="160" style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx="80"
            cy="80"
            r="70"
            stroke="var(--border-color)"
            strokeWidth="12"
            fill="transparent"
          />
          <circle
            cx="80"
            cy="80"
            r="70"
            stroke={color}
            strokeWidth="12"
            fill="transparent"
            strokeDasharray="440"
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
          />
        </svg>
        <div style={{ position: 'absolute', textAlign: 'center' }}>
          <div style={{ fontSize: '32px', fontWeight: '800', color: 'var(--text-primary)' }}>{score}</div>
          <div style={{ fontSize: '12px', fontWeight: '600', color: color }}>
            {score >= 85 ? 'OPTIMAL' : (score >= 70 ? 'MODERATE' : 'ATTENTION')}
          </div>
        </div>
      </div>
      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '12px', textAlign: 'center' }}>
        Real-time multi-resource optimization index
      </div>
    </div>
  );
};

export default Gauge;
