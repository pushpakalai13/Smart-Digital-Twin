import React from 'react';

export const Skeleton = ({ height = '20px', width = '100%', borderRadius = '8px' }) => {
  return (
    <div 
      style={{
        height,
        width,
        borderRadius,
        backgroundColor: 'var(--border-color)',
        opacity: 0.6,
        animation: 'pulse 1.5s infinite ease-in-out'
      }}
    />
  );
};

export default Skeleton;
