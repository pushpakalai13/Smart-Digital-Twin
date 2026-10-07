import React from 'react';
import { Inbox } from 'lucide-react';

const EmptyState = ({ title = "No data found", description = "There are no records matching your criteria." }) => {
  return (
    <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
      <Inbox size={48} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
      <h4 style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '4px' }}>{title}</h4>
      <p style={{ fontSize: '13px' }}>{description}</p>
    </div>
  );
};

export default EmptyState;
