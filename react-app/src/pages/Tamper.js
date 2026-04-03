import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { AlertTriangle, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';

const Tamper = ({ triggerToast }) => {
  const location = useLocation();
  const analysis = location.state?.analysis;
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Sample tampering analysis data
  const tamperingData = {
    detected: true,
    confidence: 73,
    riskLevel: 'Medium',
    suspiciousIndicators: [
      'Inconsistent compression levels detected',
      'Noise pattern inconsistencies found',
      'Unusual JPEG artifact patterns',
      'Metadata manipulation suspected'
    ],
    analysis: {
      elaScore: 68,
      noiseInconsistency: 75,
      jpegArtifacts: 82,
      metadataAnomaly: 71
    }
  };

  const runTamperAnalysis = async () => {
    setIsAnalyzing(true);
    
    // Simulate analysis delay
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    setIsAnalyzing(false);
    triggerToast('Tampering analysis complete!', 'success');
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'High': return '#ff4560';
      case 'Medium': return '#ffa726';
      case 'Low': return '#28a745';
      default: return '#6b6b8a';
    }
  };

  const getAnalysisScore = (score) => {
    if (score >= 80) return { color: '#28a745', level: 'Low' };
    if (score >= 60) return { color: '#ffa726', level: 'Medium' };
    return { color: '#ff4560', level: 'High' };
  };

  return (
    <div>
      <div className="hero">
        <h1>Tampering Detection</h1>
        <p>Advanced analysis to detect document manipulation and forgery</p>
      </div>

      {/* Main Tampering Verdict */}
      <div className={`tamper-banner ${tamperingData.detected ? 'likely' : 'clean'}`}>
        <div className="tamper-icon">
          {tamperingData.detected ? <AlertTriangle size={40} /> : <CheckCircle size={40} />}
        </div>
        <div style={{ flex: 1 }}>
          <h2 style={{ margin: '0 0 12px', fontSize: '1.8rem' }}>
            {tamperingData.detected ? 'Tampering Likely' : 'Document Appears Authentic'}
          </h2>
          <div style={{ display: 'flex', gap: '24px', alignItems: 'center', flexWrap: 'wrap' }}>
            <div>
              <span style={{ fontSize: '2rem', fontWeight: '700', color: getRiskColor(tamperingData.riskLevel) }}>
                {tamperingData.confidence}%
              </span>
              <span style={{ marginLeft: '8px', color: 'var(--muted)' }}>Confidence</span>
            </div>
            <div>
              <span className="badge" style={{ 
                backgroundColor: `${getRiskColor(tamperingData.riskLevel)}20`, 
                color: getRiskColor(tamperingData.riskLevel),
                padding: '8px 16px',
                fontSize: '1rem'
              }}>
                Risk Level: {tamperingData.riskLevel}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Suspicious Indicators */}
      {tamperingData.detected && (
        <div className="result-card">
          <h3>
            <AlertTriangle style={{ display: 'inline', marginRight: '8px' }} />
            Suspicious Indicators
          </h3>
          <div style={{ marginTop: '20px' }}>
            {tamperingData.suspiciousIndicators.map((indicator, index) => (
              <div key={index} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '16px',
                backgroundColor: 'rgba(255, 69, 96, 0.05)',
                border: '1px solid rgba(255, 69, 96, 0.2)',
                borderRadius: '12px',
                marginBottom: '12px'
              }}>
                <AlertCircle size={20} style={{ color: '#ff4560', flexShrink: 0 }} />
                <span>{indicator}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Analysis Scores */}
      <div className="result-card">
        <h3>Feature Analysis Scores</h3>
        <div className="metrics-grid">
          {Object.entries(tamperingData.analysis).map(([feature, score]) => {
            const scoreInfo = getAnalysisScore(score);
            return (
              <div key={feature} className="metric-card">
                <div className="metric-value" style={{ color: scoreInfo.color }}>
                  {score}
                </div>
                <div className="metric-label">
                  {feature.replace(/([A-Z])/g, ' $1').trim()}
                </div>
                <div className="badge" style={{
                  backgroundColor: `${scoreInfo.color}20`,
                  color: scoreInfo.color,
                  marginTop: '8px'
                }}>
                  {scoreInfo.level} Risk
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Analysis Progress */}
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
          <h3>Analyzing Document...</h3>
          <p style={{ color: 'var(--muted)' }}>
            Running comprehensive tampering detection algorithms
          </p>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
            gap: '16px',
            marginTop: '24px'
          }}>
            <div>
              <div style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>Error Level Analysis</div>
              <div style={{ fontWeight: '600' }}>Processing...</div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>Noise Pattern Analysis</div>
              <div style={{ fontWeight: '600' }}>Processing...</div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>JPEG Artifact Detection</div>
              <div style={{ fontWeight: '600' }}>Processing...</div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>Metadata Verification</div>
              <div style={{ fontWeight: '600' }}>Processing...</div>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Controls */}
      {!isAnalyzing && (
        <div className="result-card">
          <h3>Analysis Controls</h3>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <button className="button primary" onClick={runTamperAnalysis}>
              <RefreshCw size={18} />
              Run Deep Analysis
            </button>
            <button className="button secondary">
              Export Report
            </button>
            <button className="button outline">
              Compare with Original
            </button>
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div className="result-card">
        <h3>Recommendations</h3>
        <div style={{ color: 'var(--muted)', lineHeight: 1.6 }}>
          {tamperingData.detected ? (
            <div>
              <p><strong>Immediate Actions Required:</strong></p>
              <ul style={{ paddingLeft: '20px', margin: '12px 0' }}>
                <li>Verify document authenticity with original source</li>
                <li>Conduct cross-reference analysis with known authentic samples</li>
                <li>Consider forensic expert consultation for legal matters</li>
                <li>Document all findings and maintain chain of custody</li>
              </ul>
              <p><strong>Additional Verification Steps:</strong></p>
              <ul style={{ paddingLeft: '20px', margin: '12px 0' }}>
                <li>Check metadata timestamps and editing software signatures</li>
                <li>Verify pixel-level consistency across document regions</li>
                <li>Analyze compression artifacts and saving history</li>
              </ul>
            </div>
          ) : (
            <div>
              <p><strong>Document appears authentic based on our analysis.</strong></p>
              <ul style={{ paddingLeft: '20px', margin: '12px 0' }}>
                <li>No significant tampering indicators detected</li>
                <li>Consistent noise patterns throughout the document</li>
                <li>Normal compression artifacts for the file type</li>
                <li>Metadata appears consistent with content</li>
              </ul>
              <p>For critical applications, consider additional verification methods or professional forensic analysis.</p>
            </div>
          )}
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

export default Tamper;
