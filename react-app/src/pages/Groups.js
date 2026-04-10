import React, { useMemo } from 'react';
import { Users, Activity, Clock } from 'lucide-react';

const Groups = ({ history, triggerToast }) => {
  const getScannerColor = (brand) => {
    const colors = {
      'Canon': '#ff6b6b',
      'HP': '#4dabf7',
      'Epson': '#69db7c',
      'Unknown': '#868e96',
      'Brother': '#ff922b',
      'Xerox': '#7950f2'
    };
    return colors[brand] || '#868e96';
  };

  // Group history by scanner
  const scannerGroups = useMemo(() => {
    const groups = {};
    
    history.forEach(item => {
      if (item.scanner) {
        const key = `${item.scanner.brand} ${item.scanner.model}`;
        if (!groups[key]) {
          groups[key] = {
            name: key,
            brand: item.scanner.brand,
            model: item.scanner.model,
            files: [],
            avgConfidence: 0,
            totalConfidence: 0,
            tamperingCount: 0,
            lastAnalysis: null,
            color: getScannerColor(item.scanner.brand)
          };
        }
        
        groups[key].files.push(item);
        groups[key].totalConfidence += item.scanner.confidence;
        
        if (item.tampering?.detected) {
          groups[key].tamperingCount++;
        }
        
        const itemDate = new Date(item.timestamp);
        if (!groups[key].lastAnalysis || itemDate > new Date(groups[key].lastAnalysis)) {
          groups[key].lastAnalysis = item.timestamp;
        }
      }
    });
    
    // Calculate average confidence
    Object.keys(groups).forEach(key => {
      const group = groups[key];
      group.avgConfidence = Math.round(group.totalConfidence / group.files.length);
    });
    
    return Object.values(groups);
  }, [history]);

  const generateWaveform = (confidence) => {
    const points = [];
    const baseY = 30;
    const amplitude = (confidence / 100) * 20;
    
    for (let i = 0; i <= 100; i += 5) {
      const y = baseY + Math.sin(i * 0.1) * amplitude + Math.random() * 5 - 2.5;
      points.push(`${i},${y}`);
    }
    
    return points.join(' ');
  };

  
  const getRiskLevel = (tamperingCount, totalFiles) => {
    const percentage = (tamperingCount / totalFiles) * 100;
    if (percentage >= 50) return { level: 'High', color: '#ff4560' };
    if (percentage >= 25) return { level: 'Medium', color: '#ffa726' };
    return { level: 'Low', color: '#28a745' };
  };

  return (
    <div>
      <div className="hero">
        <h1>Scanner Groups</h1>
        <p>Document analysis grouped by scanner source</p>
      </div>

      {scannerGroups.length > 0 ? (
        <>
          {/* Overview Stats */}
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-value">{scannerGroups.length}</div>
              <div className="metric-label">Unique Scanners</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">
                {Math.max(...scannerGroups.map(g => g.files.length))}
              </div>
              <div className="metric-label">Max Files per Scanner</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">
                {Math.round(scannerGroups.reduce((acc, g) => acc + g.avgConfidence, 0) / scannerGroups.length)}%
              </div>
              <div className="metric-label">Average Confidence</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">
                {scannerGroups.reduce((acc, g) => acc + g.tamperingCount, 0)}
              </div>
              <div className="metric-label">Total Tampering Cases</div>
            </div>
          </div>

          {/* Scanner Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '24px' }}>
            {scannerGroups.map((group) => {
              const risk = getRiskLevel(group.tamperingCount, group.files.length);
              
              return (
                <div key={group.name} className="scanner-card">
                  <div className="scanner-card-header">
                    <div>
                      <div className="scanner-name" style={{ color: group.color }}>
                        {group.name}
                      </div>
                      <div style={{ fontSize: '0.9rem', color: 'var(--muted)', marginTop: '4px' }}>
                        {group.brand} • {group.model}
                      </div>
                    </div>
                    <div className="scanner-confidence">
                      {group.avgConfidence}%
                    </div>
                  </div>

                  {/* Waveform Visualization */}
                  <div className="waveform">
                    <svg width="100%" height="60" style={{ overflow: 'visible' }}>
                      <polyline
                        points={generateWaveform(group.avgConfidence)}
                        fill="none"
                        stroke={group.color}
                        strokeWidth="2"
                      />
                    </svg>
                  </div>

                  {/* Pattern Analysis Info */}
                  <div style={{ 
                    backgroundColor: 'var(--surface-soft)', 
                    padding: '12px', 
                    borderRadius: '8px',
                    marginBottom: '16px'
                  }}>
                    <div style={{ fontSize: '0.9rem', fontWeight: '600', marginBottom: '8px' }}>
                      Pattern Analysis
                    </div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--muted)', lineHeight: 1.4 }}>
                      Consistent noise patterns detected across {group.files.length} documents. 
                      PRNU analysis shows {group.avgConfidence >= 90 ? 'strong' : group.avgConfidence >= 70 ? 'moderate' : 'weak'} correlation.
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="metrics-grid" style={{ marginBottom: '16px' }}>
                    <div className="metric-card" style={{ padding: '12px' }}>
                      <div className="metric-value" style={{ fontSize: '1.2rem' }}>
                        {group.files.length}
                      </div>
                      <div className="metric-label">Documents</div>
                    </div>
                    <div className="metric-card" style={{ padding: '12px' }}>
                      <div className="metric-value" style={{ fontSize: '1.2rem' }}>
                        {group.tamperingCount}
                      </div>
                      <div className="metric-label">Tampering</div>
                    </div>
                    <div className="metric-card" style={{ padding: '12px' }}>
                      <div className="metric-value" style={{ fontSize: '1.2rem', color: risk.color }}>
                        {risk.level}
                      </div>
                      <div className="metric-label">Risk Level</div>
                    </div>
                  </div>

                  {/* Recent Files */}
                  <div>
                    <div style={{ fontSize: '0.9rem', fontWeight: '600', marginBottom: '8px' }}>
                      Recent Files
                    </div>
                    <div style={{ maxHeight: '120px', overflowY: 'auto' }}>
                      {group.files.slice(0, 3).map((file, index) => (
                        <div key={file.id} style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '8px 0',
                          borderBottom: index < 2 ? '1px solid var(--border)' : 'none'
                        }}>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ 
                              fontSize: '0.85rem', 
                              fontWeight: '500',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap'
                            }}>
                              {file.fileName}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>
                              {file.scanner.confidence}% confidence
                            </div>
                          </div>
                          <div style={{ marginLeft: '8px' }}>
                            {file.tampering?.detected && (
                              <span className="badge tampering" style={{ fontSize: '0.7rem' }}>
                                Tampering
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                      {group.files.length > 3 && (
                        <div style={{ 
                          fontSize: '0.8rem', 
                          color: 'var(--muted)', 
                          textAlign: 'center',
                          paddingTop: '8px'
                        }}>
                          +{group.files.length - 3} more files
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Timestamp */}
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '8px',
                    marginTop: '16px',
                    fontSize: '0.85rem',
                    color: 'var(--muted)'
                  }}>
                    <Clock size={14} />
                    Last analysis: {group.lastAnalysis ? new Date(group.lastAnalysis).toLocaleDateString() : 'Never'}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Detailed Analysis Section */}
          <div className="result-card">
            <h3>Group Analysis Summary</h3>
            <div style={{ overflowX: 'auto' }}>
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Scanner</th>
                    <th>Documents</th>
                    <th>Avg Confidence</th>
                    <th>Tampering Cases</th>
                    <th>Risk Level</th>
                    <th>Last Activity</th>
                  </tr>
                </thead>
                <tbody>
                  {scannerGroups.map((group) => {
                    const risk = getRiskLevel(group.tamperingCount, group.files.length);
                    
                    return (
                      <tr key={group.name}>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{ 
                              width: '12px', 
                              height: '12px', 
                              borderRadius: '50%', 
                              backgroundColor: group.color 
                            }}></div>
                            {group.name}
                          </div>
                        </td>
                        <td>{group.files.length}</td>
                        <td>
                          <span className={`badge ${group.avgConfidence >= 90 ? 'high' : group.avgConfidence >= 70 ? 'medium' : 'low'}`}>
                            {group.avgConfidence}%
                          </span>
                        </td>
                        <td>
                          {group.tamperingCount > 0 ? (
                            <span className="badge tampering">{group.tamperingCount}</span>
                          ) : (
                            '0'
                          )}
                        </td>
                        <td>
                          <span className="badge" style={{
                            backgroundColor: `${risk.color}20`,
                            color: risk.color
                          }}>
                            {risk.level}
                          </span>
                        </td>
                        <td>
                          {group.lastAnalysis ? new Date(group.lastAnalysis).toLocaleDateString() : 'Never'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <div className="result-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <Users size={48} style={{ color: 'var(--muted)', marginBottom: '16px' }} />
          <h3>No Scanner Groups Found</h3>
          <p style={{ color: 'var(--muted)', marginBottom: '24px' }}>
            Start analyzing documents to see them grouped by scanner source.
          </p>
          <a href="/" className="button primary">
            Start First Analysis
          </a>
        </div>
      )}
    </div>
  );
};

export default Groups;
