import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an exception:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="card" style={{ padding: '32px', textAlign: 'center', margin: '24px 0', border: '1px solid #ef4444' }}>
          <AlertTriangle size={48} style={{ color: '#ef4444', margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '8px' }}>
            {this.props.title || 'Something went wrong rendering this section'}
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto 20px' }}>
            {this.state.error?.message || 'An unexpected rendering error occurred.'}
          </p>
          <button onClick={this.handleReset} className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', margin: '0 auto' }}>
            <RefreshCw size={16} /> Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
