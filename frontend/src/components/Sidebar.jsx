import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  Map, 
  Zap, 
  Droplet, 
  Car, 
  Building2, 
  AlertTriangle, 
  BarChart3, 
  Database, 
  ChevronLeft, 
  ChevronRight,
  ShieldCheck,
  Cpu
} from 'lucide-react';

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { user, isAdmin } = useAuth();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/digital-twin', label: 'Digital Twin', icon: Map },
    { path: '/energy', label: 'Energy Management', icon: Zap },
    { path: '/water', label: 'Water Management', icon: Droplet },
    { path: '/traffic', label: 'Traffic & Parking', icon: Car },
    { path: '/facilities', label: 'Facilities & Occupancy', icon: Building2 },
    { path: '/alerts', label: 'Alerts & Anomalies', icon: AlertTriangle },
    { path: '/analytics', label: 'Analytics & Insights', icon: BarChart3 },
  ];

  if (isAdmin) {
    navItems.push({ path: '/data-management', label: 'Data Management', icon: Database });
  }

  return (
    <aside 
      style={{
        width: collapsed ? '72px' : '260px',
        backgroundColor: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border-color)',
        transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 50
      }}
    >
      {/* Brand Header */}
      <div style={{ padding: '20px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', overflow: 'hidden' }}>
          <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'linear-gradient(135deg, #2563eb, #0891b2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', flexShrink: 0 }}>
            <Cpu size={22} />
          </div>
          {!collapsed && (
            <div>
              <div style={{ fontWeight: '700', fontSize: '15px', whiteSpace: 'nowrap', color: 'var(--text-primary)' }}>SmartTwin AI</div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>Campus Intelligence</div>
            </div>
          )}
        </div>
        <button 
          onClick={() => setCollapsed(!collapsed)}
          style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '4px', borderRadius: '6px' }}
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Navigation Items */}
      <nav style={{ padding: '16px 8px', flex: 1, display: 'flex', flexDirection: 'column', gap: '4px', overflowY: 'auto' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 14px',
                borderRadius: '8px',
                textDecoration: 'none',
                fontSize: '14px',
                fontWeight: isActive ? '600' : '500',
                color: isActive ? '#ffffff' : 'var(--text-secondary)',
                backgroundColor: isActive ? 'var(--accent-primary)' : 'transparent',
                transition: 'all 0.2s ease',
                whiteSpace: 'nowrap'
              })}
              title={collapsed ? item.label : ''}
            >
              <Icon size={20} style={{ flexShrink: 0 }} />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* User Footer */}
      {!collapsed && (
        <div style={{ padding: '16px', borderTop: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '13px', fontWeight: 'bold' }}>
            {user?.name?.[0] || 'U'}
          </div>
          <div style={{ overflow: 'hidden' }}>
            <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{user?.name || 'Operator'}</div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{user?.role || 'Staff'}</div>
          </div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
