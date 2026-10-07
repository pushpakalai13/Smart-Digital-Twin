import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../services/api';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Building2, Zap, Droplet, Users, AlertTriangle, ShieldCheck, Lightbulb } from 'lucide-react';
import Skeleton from '../components/Skeleton';

// Custom colored map pins
const createCustomIcon = (status) => {
  const color = status === 'critical' ? '#ef4444' : (status === 'warning' ? '#f59e0b' : '#10b981');
  return L.divIcon({
    className: 'custom-map-pin',
    html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center;"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });
};

const DigitalTwin = () => {
  const [twinData, setTwinData] = useState(null);
  const [selectedBuilding, setSelectedBuilding] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();
  const searchQueryParam = searchParams.get('search') || searchParams.get('building');

  useEffect(() => {
    const fetchTwinState = async () => {
      try {
        const res = await api.get('/digital-twin');
        setTwinData(res.data);
        const bList = res.data.buildings || [];
        if (bList.length > 0) {
          if (searchQueryParam) {
            const qLower = searchQueryParam.toLowerCase();
            const match = bList.find(b => 
              b.name?.toLowerCase().includes(qLower) || 
              b.building_id?.toLowerCase().includes(qLower) || 
              b.category?.toLowerCase().includes(qLower)
            );
            setSelectedBuilding(match || bList[0]);
          } else {
            setSelectedBuilding(bList[0]);
          }
        }
      } catch (err) {
        console.error('Digital twin fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTwinState();
  }, [searchQueryParam]);

  if (loading) {
    return <Skeleton height="600px" />;
  }

  const buildings = twinData?.buildings || [];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '20px', height: 'calc(100vh - 120px)' }}>
      {/* Map View Container */}
      <div className="card" style={{ padding: 0, overflow: 'hidden', position: 'relative' }}>
        <MapContainer 
          center={[12.9722, 77.5940]} 
          zoom={17} 
          style={{ width: '100%', height: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {buildings.map((b) => (
            <Marker
              key={b.building_id}
              position={[b.coordinates?.lat || b.lat || 12.9720, b.coordinates?.lng || b.lng || 77.5940]}
              icon={createCustomIcon(b.status)}
              eventHandlers={{
                click: () => setSelectedBuilding(b),
              }}
            >
              <Popup>
                <div style={{ minWidth: '180px', padding: '4px' }}>
                  <div style={{ fontWeight: '700', fontSize: '14px', marginBottom: '6px' }}>{b.name}</div>
                  <div style={{ fontSize: '12px', color: '#475569', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div>⚡ Energy: <b>{b.metrics?.energy_kwh || 0} kWh</b></div>
                    <div>💧 Water: <b>{b.metrics?.water_litres || 0} L</b></div>
                    <div>👥 Occupancy: <b>{b.metrics?.occupancy_rate || 0}% ({b.metrics?.occupancy_count || 0} people)</b></div>
                    <div>Status: <b style={{ color: b.status === 'critical' ? '#ef4444' : (b.status === 'warning' ? '#f59e0b' : '#10b981') }}>{b.status?.toUpperCase()}</b></div>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* Legend Overlay */}
        <div 
          style={{
            position: 'absolute',
            bottom: '20px',
            left: '20px',
            backgroundColor: 'var(--bg-secondary)',
            padding: '12px 16px',
            borderRadius: '10px',
            border: '1px solid var(--border-color)',
            zIndex: 1000,
            display: 'flex',
            gap: '16px',
            fontSize: '12px',
            fontWeight: '600'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#10b981' }}></span>
            <span>Normal</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#f59e0b' }}></span>
            <span>Warning</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#ef4444' }}></span>
            <span>Critical</span>
          </div>
        </div>
      </div>

      {/* Building Detail Side Panel */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px', overflowY: 'auto' }}>
        {selectedBuilding ? (
          <>
            <div>
              <span className={`badge ${selectedBuilding.status === 'critical' ? 'badge-danger' : (selectedBuilding.status === 'warning' ? 'badge-warning' : 'badge-success')}`}>
                {selectedBuilding.status?.toUpperCase()}
              </span>
              <h3 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)', marginTop: '8px' }}>
                {selectedBuilding.name}
              </h3>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>ID: {selectedBuilding.building_id} • {selectedBuilding.category}</p>
              <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                Coordinates: {selectedBuilding.coordinates?.lat || selectedBuilding.lat}, {selectedBuilding.coordinates?.lng || selectedBuilding.lng}
              </p>
            </div>

            {selectedBuilding.status !== 'normal' && selectedBuilding.status_reasons && selectedBuilding.status_reasons.length > 0 && (
              <div style={{ padding: '10px 12px', borderRadius: '8px', backgroundColor: selectedBuilding.status === 'critical' ? 'rgba(239,68,68,0.1)' : 'rgba(245,158,11,0.1)', border: `1px solid ${selectedBuilding.status === 'critical' ? 'rgba(239,68,68,0.3)' : 'rgba(245,158,11,0.3)'}`, fontSize: '12px' }}>
                <span style={{ fontWeight: '700', color: selectedBuilding.status === 'critical' ? '#ef4444' : '#f59e0b', display: 'block', marginBottom: '4px' }}>Status Trigger Reason:</span>
                <ul style={{ paddingLeft: '16px', margin: 0, color: 'var(--text-primary)' }}>
                  {selectedBuilding.status_reasons.map((r, idx) => (
                    <li key={idx}>{r}</li>
                  ))}
                </ul>
              </div>
            )}

            {selectedBuilding.status !== 'normal' && selectedBuilding.recommended_actions && selectedBuilding.recommended_actions.length > 0 && (
              <div style={{ padding: '10px 12px', borderRadius: '8px', backgroundColor: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.3)', fontSize: '12px' }}>
                <span style={{ fontWeight: '700', color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                  <Lightbulb size={15} /> Recommended Action:
                </span>
                <ul style={{ paddingLeft: '16px', margin: 0, color: 'var(--text-primary)' }}>
                  {selectedBuilding.recommended_actions.map((act, idx) => (
                    <li key={idx} style={{ marginBottom: '2px' }}>{act}</li>
                  ))}
                </ul>
              </div>
            )}

            {selectedBuilding.status === 'normal' && (
              <div style={{ padding: '10px 12px', borderRadius: '8px', backgroundColor: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', fontSize: '12px', color: '#10b981', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShieldCheck size={16} />
                <span style={{ fontWeight: '600' }}>All systems operating within normal parameters.</span>
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div style={{ padding: '10px', background: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Area (sqft)</span>
                <div style={{ fontSize: '16px', fontWeight: '700' }}>{selectedBuilding.area_sqft?.toLocaleString()}</div>
              </div>
              <div style={{ padding: '10px', background: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Capacity</span>
                <div style={{ fontSize: '16px', fontWeight: '700' }}>{selectedBuilding.capacity}</div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '8px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-secondary)' }}>Live Sensor Telemetry</h4>
              
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Zap size={18} className="text-blue-500" />
                  <span style={{ fontSize: '13px', fontWeight: '500' }}>Energy Load</span>
                </div>
                <span style={{ fontWeight: '700', fontSize: '14px' }}>{selectedBuilding.metrics?.energy_kwh} kWh</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Droplet size={18} className="text-cyan-500" />
                  <span style={{ fontSize: '13px', fontWeight: '500' }}>Water Flow</span>
                </div>
                <span style={{ fontWeight: '700', fontSize: '14px' }}>{selectedBuilding.metrics?.water_litres} L</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Users size={18} className="text-emerald-500" />
                  <span style={{ fontSize: '13px', fontWeight: '500' }}>Occupancy Rate</span>
                </div>
                <span style={{ fontWeight: '700', fontSize: '14px' }}>{selectedBuilding.metrics?.occupancy_rate}%</span>
              </div>
            </div>

            {selectedBuilding.active_alerts_count > 0 && (
              <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <AlertTriangle size={18} />
                <span style={{ fontSize: '13px', fontWeight: '600' }}>{selectedBuilding.active_alerts_count} active anomaly alert(s) detected!</span>
              </div>
            )}
          </>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', paddingTop: '40px' }}>Select a building on the campus map to inspect details</div>
        )}
      </div>
    </div>
  );
};

export default DigitalTwin;
