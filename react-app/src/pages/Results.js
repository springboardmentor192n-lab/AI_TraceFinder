import React, { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { CheckCircle, AlertTriangle, Download, Share2, BarChart3, Eye, FileText } from 'lucide-react';
import jsPDF from 'jspdf';

const Results = ({ triggerToast }) => {
  const location = useLocation();
  const analysis = location.state?.analysis;

  const [isExporting, setIsExporting] = useState(false);

  if (!analysis) {
    return (
      <div className="hero">
        <h1>No Analysis Results</h1>
        <p>Please upload and analyze a document first.</p>
        <Link to="/" className="button primary">
          Go to Upload
        </Link>
      </div>
    );
  }

  // Extract exact values from analysis
  const scannerBrand = analysis.scanner?.brand || 'Unknown';
  const scannerModel = analysis.scanner?.model || 'Unknown';
  const confidenceScore = analysis.scanner?.confidence || 0;
  const confidenceLevel = confidenceScore >= 90 ? 'Very High (>90%)' : 
                         confidenceScore >= 70 ? 'High (70–90%)' : 
                         confidenceScore >= 50 ? 'Medium (50–70%)' : 'Low (<50%)';
  const detectionMethod = 'Hybrid CNN + PRNU Correlation';
  const resolution = analysis.resolution || '300 dpi';
  const datasetSource = analysis.datasetSource || 'Official';

  // Top-3 candidates
  const top3Candidates = analysis.top3 || [
    { rank: 1, scanner: `${scannerBrand} ${scannerModel}`, confidence: confidenceScore }
  ];

  // Feature quality metrics
  const featureMetrics = {
    prnu: analysis.features?.prnuQuality || 'Good',
    noise: analysis.features?.noisePattern || 'High',
    image: analysis.features?.imageQuality || 'High',
    metadata: analysis.features?.metadataStatus || 'Complete'
  };

  const generatePDFReport = async () => {
    setIsExporting(true);
    
    try {
      const pdf = new jsPDF();
      
      // Header
      pdf.setFontSize(20);
      pdf.setTextColor(91, 95, 199);
      pdf.text('TraceFinder Analysis Report', 20, 30);
      
      // Executive Summary
      pdf.setFontSize(14);
      pdf.setTextColor(31, 31, 65);
      pdf.text('Executive Summary', 20, 50);
      
      pdf.setFontSize(11);
      pdf.setTextColor(107, 107, 138);
      const summaryText = `This document was analyzed using advanced forensic techniques to identify scanner source and detect potential tampering. The analysis revealed ${scannerBrand} ${scannerModel} as most likely scanner with ${confidenceScore}% confidence.`;
      pdf.text(summaryText, 20, 60, { maxWidth: 170 });
      
      // Scanner Detection Results Table
      pdf.setFontSize(14);
      pdf.setTextColor(31, 31, 65);
      pdf.text('Scanner Detection Results', 20, 90);
      
      // Table headers
      pdf.setFontSize(10);
      pdf.setTextColor(91, 95, 199);
      pdf.text('Parameter', 20, 105);
      pdf.text('Value', 80, 105);
      pdf.text('Parameter', 120, 105);
      pdf.text('Value', 160, 105);
      
      // Table data
      pdf.setTextColor(31, 31, 65);
      pdf.text('Analysis Type', 20, 115);
      pdf.text('Scanner Identification', 80, 115);
      pdf.text('Scanner Brand', 120, 115);
      pdf.text(scannerBrand, 160, 115);
      
      pdf.text('Scanner Model', 20, 125);
      pdf.text(scannerModel, 80, 125);
      pdf.text('Confidence Score', 120, 125);
      pdf.text(`${confidenceScore}%`, 160, 125);
      
      pdf.text('Confidence Level', 20, 135);
      pdf.text(confidenceLevel, 80, 135);
      pdf.text('Detection Method', 120, 135);
      pdf.text(detectionMethod, 160, 135);
      
      pdf.text('Resolution (DPI)', 20, 145);
      pdf.text(resolution, 80, 145);
      pdf.text('Dataset Source', 120, 145);
      pdf.text(datasetSource, 160, 145);
      
      pdf.text('Number of Features', 20, 155);
      pdf.text('27', 80, 155);
      pdf.text('Analysis Timestamp', 120, 155);
      pdf.text(new Date().toLocaleString(), 160, 155);
      
      // Tampering Analysis
      if (analysis.tampering) {
        pdf.setFontSize(14);
        pdf.setTextColor(31, 31, 65);
        pdf.text('Tampering Analysis', 20, 175);
        
        pdf.setFontSize(11);
        pdf.setTextColor(107, 107, 138);
        const tamperStatus = analysis.tampering.detected ? 'Tampering Detected' : 'No Tampering Detected';
        const tamperText = `Analysis indicates ${tamperStatus.toLowerCase()} with ${analysis.tampering.confidence}% confidence. Risk level: ${analysis.tampering.riskLevel}.`;
        pdf.text(tamperText, 20, 185, { maxWidth: 170 });
      }
      
      // Save PDF
      pdf.save('TraceFinder_Analysis_Report.pdf');
      
      triggerToast('PDF report generated successfully!', 'success');
    } catch (error) {
      triggerToast('Failed to generate PDF report', 'warning');
    }
    
    setIsExporting(false);
  };

  const exportJSON = () => {
    try {
      const dataStr = JSON.stringify(analysis, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'TraceFinder_Analysis.json';
      link.click();
      URL.revokeObjectURL(url);
      
      triggerToast('JSON data exported successfully!', 'success');
    } catch (error) {
      triggerToast('Failed to export JSON data', 'warning');
    }
  };

  const shareResults = async () => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: 'TraceFinder Analysis Results',
          text: `Scanner: ${scannerBrand} ${scannerModel} (${confidenceScore}% confidence)`,
          url: window.location.href
        });
        triggerToast('Results shared successfully!', 'success');
      } else {
        // Fallback: copy to clipboard
        const shareText = `Scanner: ${scannerBrand} ${scannerModel} (${confidenceScore}% confidence)`;
        await navigator.clipboard.writeText(shareText);
        triggerToast('Results copied to clipboard!', 'success');
      }
    } catch (error) {
      triggerToast('Failed to share results', 'warning');
    }
  };

  return (
    <div>
      <div className="hero">
        <h1>Analysis Results</h1>
        <p>Document forensic analysis completed successfully</p>
      </div>

      {/* Tampering Detection Banner */}
      <div className={`tamper-banner ${analysis.tampering?.detected ? 'likely' : 'clean'}`}>
        <div className="tamper-icon">
          {analysis.tampering?.detected ? <AlertTriangle size={32} /> : <CheckCircle size={32} />}
        </div>
        <div>
          <h3 style={{ margin: '0 0 8px' }}>
            {analysis.tampering?.detected ? 'Tampering Likely ⚠' : 'Authentic ✓'}
          </h3>
          <p style={{ margin: 0, fontSize: '0.9rem' }}>
            Tamper Probability: {analysis.tampering?.confidence || 0}% | 
            Risk Level: {analysis.tampering?.riskLevel || 'Low'} | 
            Detection Confidence: {analysis.tampering?.confidence ? (100 - analysis.tampering.confidence).toFixed(1) : 100}%
          </p>
        </div>
      </div>

      {/* Scanner Identification Results */}
      <div className="result-card">
        <h3>Scanner Identification Results</h3>
        
        {/* Main Result Cards */}
        <div className="scanner-info">
          <div className="scanner-info-item">
            <div className="label">Scanner Brand</div>
            <div className="value">{scannerBrand}</div>
          </div>
          <div className="scanner-info-item">
            <div className="label">Scanner Model</div>
            <div className="value">{scannerModel}</div>
          </div>
          <div className="scanner-info-item">
            <div className="label">Confidence Score</div>
            <div className="value">{confidenceScore}%</div>
            <div className="confidence-bar">
              <div 
                className="confidence-fill" 
                style={{ width: `${confidenceScore}%` }}
              />
            </div>
          </div>
          <div className="scanner-info-item">
            <div className="label">Confidence Level</div>
            <div className="value">
              <span className={`badge ${confidenceScore >= 90 ? 'high' : confidenceScore >= 70 ? 'medium' : 'low'}`}>
                {confidenceLevel}
              </span>
            </div>
          </div>
          <div className="scanner-info-item">
            <div className="label">Detection Method</div>
            <div className="value">{detectionMethod}</div>
          </div>
          <div className="scanner-info-item">
            <div className="label">Resolution (DPI)</div>
            <div className="value">{resolution}</div>
          </div>
          <div className="scanner-info-item">
            <div className="label">Dataset Source</div>
            <div className="value">{datasetSource}</div>
          </div>
        </div>

        {/* Top-3 Candidates Table */}
        <h4 style={{ margin: '24px 0 16px', color: 'var(--text)' }}>Top-3 Candidates</h4>
        <div style={{ overflowX: 'auto' }}>
          <table className="history-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Scanner</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {top3Candidates.map((candidate) => (
                <tr key={candidate.rank}>
                  <td>
                    <span style={{ 
                      fontSize: '1.2rem', 
                      fontWeight: '700',
                      color: candidate.rank === 1 ? '#5b5fc7' : candidate.rank === 2 ? '#4a90d9' : '#6b6b8a'
                    }}>
                      {candidate.rank === 1 ? '①' : candidate.rank === 2 ? '②' : '③'}
                    </span>
                  </td>
                  <td>{candidate.scanner}</td>
                  <td>
                    <span className={`badge ${candidate.confidence >= 90 ? 'high' : candidate.confidence >= 70 ? 'medium' : 'low'}`}>
                      {candidate.confidence.toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Feature Quality Metrics */}
      <div className="result-card">
        <h3>Feature Quality Metrics</h3>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">🔍</div>
            <div className="metric-label">PRNU Quality</div>
            <div style={{ fontSize: '1.1rem', fontWeight: '600', color: '#5b5fc7' }}>
              {featureMetrics.prnu}
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-value">〰️</div>
            <div className="metric-label">Noise Pattern</div>
            <div style={{ fontSize: '1.1rem', fontWeight: '600', color: '#5b5fc7' }}>
              {featureMetrics.noise}
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-value">🖼️</div>
            <div className="metric-label">Image Quality</div>
            <div style={{ fontSize: '1.1rem', fontWeight: '600', color: '#5b5fc7' }}>
              {featureMetrics.image}
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-value">🗄️</div>
            <div className="metric-label">Metadata Status</div>
            <div style={{ fontSize: '1.1rem', fontWeight: '600', color: '#5b5fc7' }}>
              {featureMetrics.metadata}
            </div>
          </div>
        </div>
      </div>

      {/* Export & Share Actions */}
      <div className="result-card">
        <h3>Export & Share</h3>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <button 
            className="button primary" 
            onClick={generatePDFReport}
            disabled={isExporting}
          >
            <Download size={18} />
            {isExporting ? 'Generating...' : 'Generate PDF Report'}
          </button>
          
          <button className="button secondary" onClick={exportJSON}>
            <FileText size={18} />
            Export JSON
          </button>
          
          <button className="button outline" onClick={shareResults}>
            <Share2 size={18} />
            Share Results
          </button>
          
          <Link to="/dashboard" className="button outline">
            <BarChart3 size={18} />
            Analysis Dashboard
          </Link>
          
          <Link to="/features" className="button outline">
            <Eye size={18} />
            Feature Analysis
          </Link>
        </div>
      </div>

      {/* File Information */}
      <div className="result-card">
        <h3>File Information</h3>
        <div className="scanner-info">
          <div className="scanner-info-item">
            <div className="label">File Name</div>
            <div className="value">{analysis.fileName}</div>
          </div>
          <div className="scanner-info-item">
            <div className="label">File Size</div>
            <div className="value">{(analysis.fileSize / 1024 / 1024).toFixed(2)} MB</div>
          </div>
          <div className="scanner-info-item">
            <div className="label">File Type</div>
            <div className="value">{analysis.fileType}</div>
          </div>
        </div>
      </div>

      {/* New Analysis Button */}
      <div style={{ textAlign: 'center', marginTop: '32px' }}>
        <Link to="/" className="button primary">
          New Analysis
        </Link>
      </div>
    </div>
  );
};

export default Results;
