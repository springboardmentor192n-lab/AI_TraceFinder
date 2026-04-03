import React, { useState } from 'react';
import { Eye, Zap, Image, FileText, RefreshCw } from 'lucide-react';

const Features = ({ triggerToast }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Sample feature analysis data
  const featureData = {
    ela: {
      name: 'Error Level Analysis',
      description: 'Detects variations in compression levels that may indicate tampering',
      score: 72,
      status: 'warning',
      details: 'Inconsistent compression artifacts detected in specific regions',
      findings: [
        'Higher compression in upper right quadrant',
        'Inconsistent ELA patterns in text regions',
        'Possible selective recompression detected'
      ]
    },
    noise: {
      name: 'Noise Pattern Analysis',
      description: 'Analyzes sensor noise patterns for consistency',
      score: 85,
      status: 'good',
      details: 'Consistent noise patterns throughout most of the document',
      findings: [
        'Uniform PRNU patterns detected',
        'Consistent Gaussian noise distribution',
        'Minor variation in edge regions'
      ]
    },
    jpeg: {
      name: 'JPEG Artifacts',
      description: 'Examines compression artifacts and quantization tables',
      score: 68,
      status: 'warning',
      details: 'Unusual JPEG artifact patterns suggest multiple saves',
      findings: [
        'Double compression indicators',
        'Inconsistent quantization tables',
        'DCT coefficient anomalies detected'
      ]
    },
    metadata: {
      name: 'Metadata Analysis',
      description: 'Verifies file metadata for inconsistencies',
      score: 91,
      status: 'good',
      details: 'Metadata appears consistent with document content',
      findings: [
        'Valid EXIF data structure',
        'Consistent creation and modification timestamps',
        'No suspicious software signatures'
      ]
    }
  };

  const runFeatureAnalysis = async () => {
    setIsAnalyzing(true);
    
    // Simulate analysis delay
    await new Promise(resolve => setTimeout(resolve, 2500));
    
    setIsAnalyzing(false);
    triggerToast('Feature analysis complete!', 'success');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'good': return '#28a745';
      case 'warning': return '#ffa726';
      case 'danger': return '#ff4560';
      default: return '#6b6b8a';
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      good: { bg: '#28a74520', color: '#28a745', text: 'Normal' },
      warning: { bg: '#ffa72620', color: '#ffa726', text: 'Suspicious' },
      danger: { bg: '#ff456020', color: '#ff4560', text: 'Critical' }
    };
    return colors[status] || colors.warning;
  };

  const getFeatureIcon = (feature) => {
    const icons = {
      ela: <Eye size={24} />,
      noise: <Zap size={24} />,
      jpeg: <Image size={24} />,
      metadata: <FileText size={24} />
    };
    return icons[feature] || <Eye size={24} />;
  };

  return (
    <div>
      <div className="hero">
        <h1>Feature Analysis</h1>
        <p>Detailed examination of forensic features and artifacts</p>
      </div>

      {/* Feature Analysis Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        {Object.entries(featureData).map(([key, feature]) => {
          const badgeInfo = getStatusBadge(feature.status);
          
          return (
            <div key={key} className="result-card">
              <div className="card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ 
                    width: '48px', 
                    height: '48px', 
                    borderRadius: '12px', 
                    backgroundColor: 'var(--surface-soft)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: getStatusColor(feature.status)
                  }}>
                    {getFeatureIcon(key)}
                  </div>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{feature.name}</h3>
                    <div className="badge" style={{
                      backgroundColor: badgeInfo.bg,
                      color: badgeInfo.color,
                      marginTop: '4px'
                    }}>
                      {badgeInfo.text}
                    </div>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ 
                    fontSize: '2rem', 
                    fontWeight: '700', 
                    color: getStatusColor(feature.status) 
                  }}>
                    {feature.score}
                  </div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>Score</div>
                </div>
              </div>

              <div style={{ marginTop: '16px' }}>
                <p style={{ color: 'var(--muted)', marginBottom: '16px', fontSize: '0.9rem' }}>
                  {feature.description}
                </p>
                
                <div style={{ 
                  backgroundColor: 'var(--surface-soft)', 
                  padding: '12px', 
                  borderRadius: '8px',
                  borderLeft: `4px solid ${getStatusColor(feature.status)}`,
                  marginBottom: '16px'
                }}>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>Analysis Result:</div>
                  <div style={{ fontSize: '0.9rem' }}>{feature.details}</div>
                </div>

                <div>
                  <div style={{ fontWeight: '600', marginBottom: '8px', fontSize: '0.9rem' }}>Key Findings:</div>
                  <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '0.9rem' }}>
                    {feature.findings.map((finding, index) => (
                      <li key={index} style={{ marginBottom: '4px', color: 'var(--text)' }}>
                        {finding}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Progress Bar */}
              <div style={{ marginTop: '16px' }}>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill" 
                    style={{ 
                      width: `${feature.score}%`,
                      backgroundColor: getStatusColor(feature.status)
                    }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Overall Assessment */}
      <div className="result-card">
        <h3>Overall Assessment</h3>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">79</div>
            <div className="metric-label">Overall Score</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">2</div>
            <div className="metric-label">Suspicious Features</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">Medium</div>
            <div className="metric-label">Risk Level</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">4/4</div>
            <div className="metric-label">Features Analyzed</div>
          </div>
        </div>
      </div>

      {/* Detailed Analysis Progress */}
      {isAnalyzing && (
        <div className="result-card" style={{ textAlign: 'center' }}>
          <div className="spinner" style={{ 
            width: '48px', 
            height: '48px', 
            border: '4px solid var(--border)', 
            borderTop: '4px solid var(--primary)', 
            borderRadius: '50%', 
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px'
          }}></div>
          <h3>Running Feature Analysis...</h3>
          <p style={{ color: 'var(--muted)' }}>
            Analyzing document features for tampering indicators
          </p>
          <div style={{ marginTop: '24px', textAlign: 'left' }}>
            {Object.keys(featureData).map((feature, index) => (
              <div key={feature} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '12px 0',
                borderBottom: index < 3 ? '1px solid var(--border)' : 'none'
              }}>
                <span>{featureData[feature].name}</span>
                <span style={{ color: 'var(--muted)' }}>
                  {index === 0 ? 'Analyzing...' : index === 1 ? 'Queued...' : 'Pending...'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Controls */}
      {!isAnalyzing && (
        <div className="result-card">
          <h3>Analysis Controls</h3>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <button className="button primary" onClick={runFeatureAnalysis}>
              <RefreshCw size={18} />
              Re-run Analysis
            </button>
            <button className="button secondary">
              Export Detailed Report
            </button>
            <button className="button outline">
              Compare with Baseline
            </button>
          </div>
        </div>
      )}

      {/* Technical Details */}
      <div className="result-card">
        <h3>Technical Details</h3>
        <div style={{ color: 'var(--muted)', lineHeight: 1.6 }}>
          <h4 style={{ color: 'var(--text)', marginBottom: '12px' }}>Analysis Methodology:</h4>
          <ul style={{ paddingLeft: '20px', margin: '12px 0' }}>
            <li><strong>Error Level Analysis:</strong> Compares compression artifacts at different quality levels to detect tampering</li>
            <li><strong>Noise Pattern Analysis:</strong> Examines Photo Response Non-Uniformity (PRNU) patterns for consistency</li>
            <li><strong>JPEG Artifact Detection:</strong> Analyzes DCT coefficients and quantization table inconsistencies</li>
            <li><strong>Metadata Verification:</strong> Cross-references EXIF data with visual content analysis</li>
          </ul>
          
          <h4 style={{ color: 'var(--text)', marginBottom: '12px', marginTop: '20px' }}>Confidence Scoring:</h4>
          <p>Each feature is scored on a scale of 0-100, where higher scores indicate normal/authentic characteristics. Scores below 70 typically warrant further investigation.</p>
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default Features;
