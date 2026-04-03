import React, { useState, useMemo } from 'react';
import { Search, Filter, Download, Trash2, Edit, FileText, AlertTriangle } from 'lucide-react';
import jsPDF from 'jspdf';

const History = ({ history, setHistory, triggerToast }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterConfidence, setFilterConfidence] = useState('all');
  const [filterTimeRange, setFilterTimeRange] = useState('all');

  // Calculate statistics
  const stats = useMemo(() => {
    const totalAnalyses = history.length;
    const comparisons = history.filter(h => h.type === 'comparison').length;
    const tamperingChecks = history.filter(h => h.tampering?.detected).length;
    const tamperingRate = totalAnalyses > 0 ? ((tamperingChecks / totalAnalyses) * 100).toFixed(2) : '0.00';

    return {
      totalAnalyses,
      comparisons,
      tamperingChecks,
      tamperingRate
    };
  }, [history]);

  // Filter history based on search and filters
  const filteredHistory = useMemo(() => {
    return history.filter(item => {
      // Search filter
      const searchMatch = searchTerm === '' || 
        item.fileName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.scanner && `${item.scanner.brand} ${item.scanner.model}`.toLowerCase().includes(searchTerm.toLowerCase()));

      // Type filter
      const typeMatch = filterType === 'all' || item.type === filterType;

      // Confidence filter
      let confidenceMatch = true;
      if (filterConfidence !== 'all' && item.scanner) {
        const conf = item.scanner.confidence;
        if (filterConfidence === 'high') confidenceMatch = conf >= 90;
        else if (filterConfidence === 'medium') confidenceMatch = conf >= 70 && conf < 90;
        else if (filterConfidence === 'low') confidenceMatch = conf < 70;
      }

      // Time range filter
      let timeMatch = true;
      if (filterTimeRange !== 'all') {
        const itemDate = new Date(item.timestamp);
        const now = new Date();
        
        if (filterTimeRange === 'today') {
          timeMatch = itemDate.toDateString() === now.toDateString();
        } else if (filterTimeRange === 'week') {
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          timeMatch = itemDate >= weekAgo;
        } else if (filterTimeRange === 'month') {
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          timeMatch = itemDate >= monthAgo;
        }
      }

      return searchMatch && typeMatch && confidenceMatch && timeMatch;
    });
  }, [history, searchTerm, filterType, filterConfidence, filterTimeRange]);

  const handleDelete = (id) => {
    setHistory(prev => prev.filter(item => item.id !== id));
    triggerToast('Analysis deleted successfully', 'success');
  };

  const handleEdit = (item) => {
    triggerToast('Edit functionality coming soon', 'warning');
  };

  const generatePDF = (item) => {
    try {
      const pdf = new jsPDF();
      
      // Header
      pdf.setFontSize(16);
      pdf.setTextColor(91, 95, 199);
      pdf.text('TraceFinder Analysis Report', 20, 30);
      
      // Basic info
      pdf.setFontSize(12);
      pdf.setTextColor(31, 31, 65);
      pdf.text(`File: ${item.fileName}`, 20, 50);
      pdf.text(`Date: ${new Date(item.timestamp).toLocaleString()}`, 20, 60);
      
      if (item.scanner) {
        pdf.text(`Scanner: ${item.scanner.brand} ${item.scanner.model}`, 20, 70);
        pdf.text(`Confidence: ${item.scanner.confidence}%`, 20, 80);
      }
      
      if (item.tampering) {
        pdf.text(`Tampering: ${item.tampering.detected ? 'Detected' : 'Not Detected'}`, 20, 90);
      }
      
      pdf.save(`TraceFinder_${item.fileName}_${item.id}.pdf`);
      triggerToast('PDF report generated successfully', 'success');
    } catch (error) {
      triggerToast('Failed to generate PDF', 'warning');
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'tampering': return <AlertTriangle size={16} style={{ color: '#ff4560' }} />;
      case 'scanner': return <FileText size={16} style={{ color: '#5b5fc7' }} />;
      case 'comparison': return <Filter size={16} style={{ color: '#4a90d9' }} />;
      default: return <FileText size={16} />;
    }
  };

  const getConfidenceBadge = (confidence) => {
    if (!confidence) return null;
    
    let className = '';
    if (confidence >= 90) className = 'high';
    else if (confidence >= 70) className = 'medium';
    else className = 'low';
    
    return <span className={`badge ${className}`}>{confidence}%</span>;
  };

  return (
    <div>
      <div className="hero">
        <h1>Analysis History</h1>
        <p>View and manage your forensic analysis results</p>
      </div>

      {/* Statistics Bar */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-value">{stats.totalAnalyses}</div>
          <div className="metric-label">Total Analyses</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{stats.comparisons}</div>
          <div className="metric-label">Comparisons</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{stats.tamperingChecks}</div>
          <div className="metric-label">Tampering Checks</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{stats.tamperingRate}%</div>
          <div className="metric-label">Tampering Rate</div>
        </div>
      </div>

      {/* Search and Filter Bar */}
      <div className="result-card">
        <div className="card-header">
          <h3>Search & Filter</h3>
        </div>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '16px',
          marginBottom: '16px'
        }}>
          <div style={{ position: 'relative' }}>
            <Search size={18} style={{ 
              position: 'absolute', 
              left: '12px', 
              top: '50%', 
              transform: 'translateY(-50%)',
              color: 'var(--muted)'
            }} />
            <input
              type="text"
              placeholder="Search files or scanners..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 12px 12px 44px',
                border: '1px solid var(--border)',
                borderRadius: '12px',
                fontSize: '0.9rem',
                backgroundColor: 'var(--surface-soft)'
              }}
            />
          </div>
          
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            style={{
              padding: '12px',
              border: '1px solid var(--border)',
              borderRadius: '12px',
              fontSize: '0.9rem',
              backgroundColor: 'var(--surface-soft)',
              color: 'var(--text)'
            }}
          >
            <option value="all">All Types</option>
            <option value="scanner">Scanner</option>
            <option value="tampering">Tampering</option>
            <option value="comparison">Comparison</option>
          </select>
          
          <select
            value={filterConfidence}
            onChange={(e) => setFilterConfidence(e.target.value)}
            style={{
              padding: '12px',
              border: '1px solid var(--border)',
              borderRadius: '12px',
              fontSize: '0.9rem',
              backgroundColor: 'var(--surface-soft)',
              color: 'var(--text)'
            }}
          >
            <option value="all">All Confidence</option>
            <option value="high">High (90%+)</option>
            <option value="medium">Medium (70-89%)</option>
            <option value="low">Low (&lt;70%)</option>
          </select>
          
          <select
            value={filterTimeRange}
            onChange={(e) => setFilterTimeRange(e.target.value)}
            style={{
              padding: '12px',
              border: '1px solid var(--border)',
              borderRadius: '12px',
              fontSize: '0.9rem',
              backgroundColor: 'var(--surface-soft)',
              color: 'var(--text)'
            }}
          >
            <option value="all">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
        </div>
        
        <div style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>
          Showing {filteredHistory.length} of {history.length} results
        </div>
      </div>

      {/* History Table */}
      <div className="result-card">
        <div className="card-header">
          <h3>Analysis History</h3>
        </div>
        
        {filteredHistory.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="history-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Scanner/Details</th>
                  <th>Confidence</th>
                  <th>Date/Time</th>
                  <th>Notes</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredHistory.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {getTypeIcon(item.type)}
                        <span style={{ textTransform: 'capitalize' }}>{item.type}</span>
                      </div>
                    </td>
                    <td>
                      <div>
                        <div style={{ fontWeight: '600', marginBottom: '4px' }}>
                          {item.scanner ? `${item.scanner.brand} ${item.scanner.model}` : 'Unknown Scanner'}
                        </div>
                        <div style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>
                          {item.fileName}
                        </div>
                        {item.type === 'comparison' && (
                          <div style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>
                            Comparison analysis
                          </div>
                        )}
                      </div>
                    </td>
                    <td>
                      {getConfidenceBadge(item.scanner?.confidence)}
                      {item.tampering?.detected && (
                        <div className="badge tampering" style={{ marginTop: '4px' }}>
                          Tampering
                        </div>
                      )}
                    </td>
                    <td>
                      <div>
                        <div>{new Date(item.timestamp).toLocaleDateString()}</div>
                        <div style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>
                          {new Date(item.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    </td>
                    <td>
                      <div style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>
                        {item.tampering?.detected ? 'Tampering detected' : 'Normal analysis'}
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          className="button small-button outline"
                          onClick={() => handleEdit(item)}
                          title="Edit"
                        >
                          <Edit size={14} />
                        </button>
                        <button
                          className="button small-button outline"
                          onClick={() => generatePDF(item)}
                          title="Generate PDF"
                        >
                          <Download size={14} />
                        </button>
                        <button
                          className="button small-button danger"
                          onClick={() => handleDelete(item.id)}
                          title="Delete"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ 
            textAlign: 'center', 
            padding: '60px 20px', 
            color: 'var(--muted)' 
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📋</div>
            <h3>No Analysis History Found</h3>
            <p>
              {history.length === 0 
                ? 'Start analyzing documents to build your history.' 
                : 'No results match your current filters.'
              }
            </p>
            {history.length === 0 && (
              <a href="/" className="button primary" style={{ display: 'inline-block', marginTop: '16px' }}>
                Start First Analysis
              </a>
            )}
            {filteredHistory.length === 0 && history.length > 0 && (
              <button 
                className="button outline" 
                onClick={() => {
                  setSearchTerm('');
                  setFilterType('all');
                  setFilterConfidence('all');
                  setFilterTimeRange('all');
                }}
                style={{ display: 'inline-block', marginTop: '16px' }}
              >
                Clear Filters
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
