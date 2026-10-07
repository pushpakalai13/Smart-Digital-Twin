import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useDropzone } from 'react-dropzone';
import Skeleton from '../components/Skeleton';
import EmptyState from '../components/EmptyState';
import ErrorBoundary from '../components/ErrorBoundary';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Trash2, 
  Download, 
  RefreshCw, 
  Cpu, 
  AlertTriangle
} from 'lucide-react';

const DataManagementContent = () => {
  const [datasetType, setDatasetType] = useState('energy');
  const [datasets, setDatasets] = useState([]);
  const [uploadResult, setUploadResult] = useState(null);
  const [mapping, setMapping] = useState({});
  const [importing, setImporting] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [mlStatus, setMlStatus] = useState(null);
  const [retraining, setRetraining] = useState(false);
  const [toast, setToast] = useState(null);
  const [importingId, setImportingId] = useState(null);

  const handleHistoryImport = async (dsId, filename) => {
    setImportingId(dsId);
    try {
      await api.post(`/datasets/${dsId}/import`);
      showToast(`Dataset '${filename || dsId}' imported successfully into MongoDB!`);
      setDatasets(prev => prev.map(d => d.dataset_id === dsId ? { ...d, status: 'imported' } : d));
      fetchHistory();
      fetchMlStatus();
    } catch (err) {
      console.error('History Import Error:', err);
      const detail = err.response?.data?.detail || err.message || 'Import failed';
      showToast(detail, true);
    } finally {
      setImportingId(null);
    }
  };

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const res = await api.get('/datasets');
      setDatasets(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error('Fetch history error:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const fetchMlStatus = async () => {
    try {
      const res = await api.get('/ml/status');
      setMlStatus(res.data);
    } catch (err) {
      console.error('Fetch ML status error:', err);
    }
  };

  useEffect(() => {
    fetchHistory();
    fetchMlStatus();
    const timer = setInterval(fetchMlStatus, 5000);
    return () => clearInterval(timer);
  }, []);

  const formatErrorMessage = (rawDetail) => {
    if (!rawDetail) return 'An unexpected error occurred';
    if (typeof rawDetail === 'string') return rawDetail;
    if (Array.isArray(rawDetail)) {
      return rawDetail
        .map(item => (typeof item === 'object' ? (item.msg || item.detail || JSON.stringify(item)) : String(item)))
        .join('; ');
    }
    if (typeof rawDetail === 'object') {
      return rawDetail.detail || rawDetail.message || JSON.stringify(rawDetail);
    }
    return String(rawDetail);
  };

  const showToast = (msg, isErr = false) => {
    const cleanMsg = formatErrorMessage(msg);
    setToast({ msg: cleanMsg, isErr });
    setTimeout(() => setToast(null), 5000);
  };

  const onDrop = async (acceptedFiles, fileRejections) => {
    let file = (acceptedFiles && acceptedFiles.length > 0) ? acceptedFiles[0] : null;
    
    if (!file && fileRejections && fileRejections.length > 0) {
      const rejFile = fileRejections[0]?.file;
      if (rejFile) {
        const nameLower = rejFile.name.toLowerCase();
        if (nameLower.endsWith('.csv') || nameLower.endsWith('.xlsx') || nameLower.endsWith('.xls')) {
          file = rejFile;
        }
      }
    }

    if (!file) {
      showToast('Please select a valid .csv or .xlsx dataset file.', true);
      return;
    }

    const formData = new FormData();
    formData.append('dataset_type', datasetType);
    formData.append('file', file, file.name);

    try {
      const res = await api.post('/datasets/upload', formData);
      if (!res || !res.data) {
        showToast('Server returned an empty upload response', true);
        return;
      }
      setUploadResult(res.data);

      const detected = res.data.validation?.detected_columns || [];
      const initMap = {};
      if (Array.isArray(detected)) {
        detected.forEach(col => { if (col) initMap[col] = col; });
      }
      setMapping(initMap);
      
      if (res.data.validation?.valid) {
        showToast('File uploaded & validated successfully!');
      } else {
        showToast('File uploaded, but validation issues were found', true);
      }
    } catch (err) {
      console.error('Upload Error:', err);
      const detail = err.response?.data?.detail || err.message || 'Upload failed';
      showToast(detail, true);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 
      'text/csv': ['.csv'], 
      'text/plain': ['.csv'],
      'text/x-csv': ['.csv'],
      'application/csv': ['.csv'],
      'application/x-csv': ['.csv'],
      'application/vnd.ms-excel': ['.csv', '.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxFiles: 1
  });

  const handleImport = async () => {
    if (!uploadResult) return;
    setImporting(true);
    try {
      await api.post(`/datasets/${uploadResult.dataset_id}/import`, { column_mapping: mapping });
      showToast(`Dataset '${uploadResult.filename || 'file'}' imported successfully!`);
      setUploadResult(null);
      fetchHistory();
      fetchMlStatus();
    } catch (err) {
      console.error('Import Error:', err);
      const detail = err.response?.data?.detail || err.message || 'Import failed';
      showToast(detail, true);
    } finally {
      setImporting(false);
    }
  };

  const handleDelete = async (dsId) => {
    if (!window.confirm(`Delete dataset ${dsId} and remove all its imported documents?`)) return;
    try {
      await api.delete(`/datasets/${dsId}`);
      showToast(`Dataset ${dsId} deleted successfully.`);
      fetchHistory();
    } catch (err) {
      console.error('Delete Error:', err);
      const detail = err.response?.data?.detail || err.message || 'Delete failed';
      showToast(detail, true);
    }
  };

  const triggerRetrain = async () => {
    setRetraining(true);
    try {
      await api.post('/ml/retrain?source=uploaded');
      showToast('ML retraining background task started.');
      fetchMlStatus();
    } catch (err) {
      console.error('Retrain Error:', err);
      showToast('Retraining error occurred', true);
    } finally {
      setRetraining(false);
    }
  };

  const downloadTemplate = (type) => {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    window.open(`${baseUrl}/datasets/template/${type}`, '_blank');
  };

  const previewRows = Array.isArray(uploadResult?.preview) ? uploadResult.preview : [];
  const previewHeaders = previewRows.length > 0 && typeof previewRows[0] === 'object' && previewRows[0] !== null
    ? Object.keys(previewRows[0])
    : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Toast Alert */}
      {toast && (
        <div style={{
          position: 'fixed', bottom: '24px', right: '24px', zIndex: 9999,
          padding: '12px 20px', borderRadius: '10px',
          backgroundColor: toast.isErr ? '#ef4444' : '#10b981', color: '#fff',
          fontWeight: '600', fontSize: '13px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
          maxWidth: '450px', wordBreak: 'break-word'
        }}>
          {toast.msg}
        </div>
      )}

      {/* Header & Retrain Controls */}
      <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)' }}>Data Management & ML Retraining</h2>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Upload CSV/XLSX datasets, inspect validation report, commit to database, and retrain ML models</p>
        </div>

        <button 
          onClick={triggerRetrain}
          disabled={retraining || mlStatus?.is_training}
          className="btn btn-primary"
          style={{ fontSize: '13px' }}
        >
          <Cpu size={16} />
          <span>{mlStatus?.is_training ? 'ML Training In Progress...' : 'Retrain ML Models'}</span>
        </button>
      </div>

      {/* ML Performance Metrics Card */}
      {mlStatus?.models && (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)' }}>Active ML Model Metrics (Selected by Best R²)</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
            {['energy', 'water', 'traffic'].map(mName => {
              const info = mlStatus.models[mName];
              return (
                <div key={mName} style={{ padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-primary)' }}>
                  <div style={{ fontSize: '12px', fontWeight: '700', textTransform: 'uppercase', color: 'var(--accent-primary)' }}>{mName} Model</div>
                  {info ? (
                    <div style={{ fontSize: '12px', marginTop: '6px', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                      <div>Selected: <b>{info.selected_model}</b></div>
                      <div>R² Score: <b>{info.metrics?.r2}</b></div>
                      <div>MAE: <b>{info.metrics?.mae}</b> | RMSE: <b>{info.metrics?.rmse}</b></div>
                    </div>
                  ) : <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Not trained yet</div>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Drag and Drop Upload Box */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)' }}>Upload Real Dataset</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '13px', fontWeight: '600' }}>Type:</span>
            <select 
              value={datasetType}
              onChange={(e) => setDatasetType(e.target.value)}
              style={{ padding: '6px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)', fontSize: '13px', fontWeight: '600' }}
            >
              <option value="energy">Energy Data (kWh)</option>
              <option value="water">Water Data (L)</option>
              <option value="traffic">Traffic Data (vehicles)</option>
              <option value="occupancy">Occupancy Data</option>
              <option value="parking">Parking Data</option>
              <option value="buildings">Buildings Metadata</option>
            </select>
            <button onClick={() => downloadTemplate(datasetType)} className="btn btn-secondary" style={{ fontSize: '12px', padding: '6px 10px' }}>
              <Download size={14} /> Template
            </button>
          </div>
        </div>

        <div 
          {...getRootProps()} 
          style={{
            border: '2px dashed var(--border-color)',
            borderRadius: '12px',
            padding: '40px',
            textAlign: 'center',
            backgroundColor: isDragActive ? 'rgba(37, 99, 235, 0.05)' : 'var(--bg-primary)',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          <input {...getInputProps()} />
          <UploadCloud size={40} style={{ margin: '0 auto 12px', color: 'var(--accent-primary)' }} />
          <h4 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)' }}>
            {isDragActive ? 'Drop your CSV or XLSX file here...' : 'Drag & drop CSV or XLSX file here'}
          </h4>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Maximum file size: 50 MB</p>
        </div>
      </div>

      {/* Validation & Preview Panel */}
      {uploadResult && (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px', border: `1px solid ${uploadResult.validation?.valid ? 'var(--accent-primary)' : '#ef4444'}` }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-primary)' }}>
              Validation Summary: {uploadResult.filename || 'Uploaded File'}
            </h3>
            <span className={`badge ${uploadResult.validation?.valid ? 'badge-success' : 'badge-danger'}`}>
              {uploadResult.validation?.valid ? 'Validation Passed (Clean)' : 'Validation Issues Found'}
            </span>
          </div>

          <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Total Rows Detected: <b>{uploadResult.validation?.total_rows ?? uploadResult.row_count ?? 0}</b>
          </div>

          {/* Error & Warning Lists */}
          {uploadResult.validation?.row_errors && uploadResult.validation.row_errors.length > 0 && (
            <div style={{ padding: '12px', borderRadius: '8px', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444' }}>
              <div style={{ fontSize: '13px', fontWeight: '700', color: '#ef4444', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertCircle size={16} /> Validation Errors ({uploadResult.validation.row_errors.length})
              </div>
              <ul style={{ fontSize: '12px', color: 'var(--text-secondary)', paddingLeft: '20px', margin: 0 }}>
                {uploadResult.validation.row_errors.map((err, idx) => (
                  <li key={idx}>{String(err)}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Row Preview Table */}
          {previewRows.length > 0 && (
            <div>
              <h4 style={{ fontSize: '13px', fontWeight: '700', marginBottom: '8px' }}>First 20 Rows Preview</h4>
              <div className="table-container" style={{ maxHeight: '220px' }}>
                <table>
                  <thead>
                    <tr>
                      {previewHeaders.map(k => <th key={k}>{k}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {previewRows.map((r, i) => (
                      <tr key={i}>
                        {previewHeaders.map((h, j) => {
                          const val = r ? r[h] : '';
                          return <td key={j}>{val !== null && val !== undefined ? (typeof val === 'object' ? JSON.stringify(val) : String(val)) : ''}</td>;
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button onClick={() => setUploadResult(null)} className="btn btn-secondary">Discard</button>
            <button onClick={handleImport} disabled={importing || !uploadResult.validation?.valid} className="btn btn-primary">
              {importing ? 'Importing to Atlas...' : 'Commit & Import to Atlas'}
            </button>
          </div>
        </div>
      )}

      {/* Upload History Table */}
      <div className="card">
        <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px' }}>Uploaded Datasets History</h3>
        {loadingHistory ? <Skeleton height="250px" /> : (
          datasets.length === 0 ? <EmptyState title="No uploaded datasets" description="Upload a CSV file above to populate MongoDB Atlas." /> : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Dataset ID</th>
                    <th>Filename</th>
                    <th>Type</th>
                    <th>Row Count</th>
                    <th>Status</th>
                    <th>Uploaded At</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {datasets.map(d => (
                    <tr key={d.dataset_id || d._id}>
                      <td style={{ fontWeight: '600' }}>{d.dataset_id}</td>
                      <td>{d.filename}</td>
                      <td style={{ textTransform: 'capitalize' }}>{d.dataset_type}</td>
                      <td>{d.row_count}</td>
                      <td>
                        <span className={`badge ${d.status === 'imported' ? 'badge-success' : d.status === 'pending_import' ? 'badge-warning' : 'badge-info'}`}>
                          {d.status === 'pending_import' ? 'Pending Import' : d.status === 'imported' ? 'Imported' : d.status}
                        </span>
                      </td>
                      <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{d.created_at ? new Date(d.created_at).toLocaleString() : 'N/A'}</td>
                      <td style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {d.status === 'pending_import' && (
                          <button 
                            onClick={() => handleHistoryImport(d.dataset_id, d.filename)} 
                            disabled={importingId === d.dataset_id}
                            className="btn btn-primary"
                            style={{ fontSize: '11px', padding: '4px 10px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                            title="Import dataset into database"
                          >
                            {importingId === d.dataset_id ? (
                              <>
                                <RefreshCw size={12} style={{ animation: 'spin 1s linear infinite' }} />
                                <span>Importing...</span>
                              </>
                            ) : (
                              <>
                                <UploadCloud size={12} />
                                <span>Import</span>
                              </>
                            )}
                          </button>
                        )}
                        <button onClick={() => handleDelete(d.dataset_id)} style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer' }} title="Delete from Atlas">
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </div>
    </div>
  );
};

const DataManagement = () => {
  return (
    <ErrorBoundary title="Data Management & Upload Module">
      <DataManagementContent />
    </ErrorBoundary>
  );
};

export default DataManagement;
