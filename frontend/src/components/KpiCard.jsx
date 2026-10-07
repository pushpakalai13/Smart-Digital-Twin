import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line } from 'recharts';

const KpiCard = ({ title, value, unit = '', changePct, trendData = [], icon: Icon, color = '#2563eb' }) => {
  const isPositive = changePct > 0;
  const isNegative = changePct < 0;

  const sparkData = trendData.map((val, idx) => ({ i: idx, v: val }));

  return (
    <div className="card card-hover" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)' }}>{title}</span>
        {Icon && (
          <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: `${color}15`, color: color }}>
            <Icon size={18} />
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
        <span style={{ fontSize: '28px', fontWeight: '800', color: 'var(--text-primary)', letterSpacing: '-0.5px' }}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </span>
        {unit && <span style={{ fontSize: '14px', fontWeight: '500', color: 'var(--text-muted)' }}>{unit}</span>}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '4px' }}>
        {changePct !== undefined && (
          <div 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '4px', 
              fontSize: '12px', 
              fontWeight: '600',
              color: isNegative ? '#10b981' : (isPositive ? '#ef4444' : 'var(--text-muted)')
            }}
          >
            {isPositive ? <TrendingUp size={14} /> : (isNegative ? <TrendingDown size={14} /> : <Minus size={14} />)}
            <span>{Math.abs(changePct)}% vs yesterday</span>
          </div>
        )}

        {sparkData.length > 0 && (
          <div style={{ width: '80px', height: '30px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sparkData}>
                <Line type="monotone" dataKey="v" stroke={color} strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default KpiCard;
