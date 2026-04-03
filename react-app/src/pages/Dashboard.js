import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, Tooltip } from 'recharts';

const Dashboard = ({ history }) => {
  // Calculate statistics from history
  const totalAnalyses = history.length;
  const scannerAnalyses = history.filter(h => h.type === 'scanner').length;
  const tamperingChecks = history.filter(h => h.tampering?.detected).length;
  const tamperingRate = totalAnalyses > 0 ? ((tamperingChecks / totalAnalyses) * 100).toFixed(2) : '0.00';

  // Donut chart data - Confidence Distribution
  const confidenceData = [
    { name: 'Very High (95-100%)', value: history.filter(h => h.scanner?.confidence >= 95).length, color: '#28a745' },
    { name: 'High (85-94%)', value: history.filter(h => h.scanner?.confidence >= 85 && h.scanner?.confidence < 95).length, color: '#5b5fc7' },
    { name: 'Medium (70-84%)', value: history.filter(h => h.scanner?.confidence >= 70 && h.scanner?.confidence < 85).length, color: '#f07a6a' },
    { name: 'Low (<70%)', value: history.filter(h => h.scanner?.confidence < 70).length, color: '#6b6b8a' },
  ].filter(item => item.value > 0);

  // Radar chart data - Feature Quality Metrics
  const radarData = [
    { feature: 'PRNU', value: 85, fullMark: 100 },
    { feature: 'Texture', value: 92, fullMark: 100 },
    { feature: 'Noise', value: 78, fullMark: 100 },
    { feature: 'Frequency', value: 88, fullMark: 100 },
    { feature: 'Metadata', value: 95, fullMark: 100 },
  ];

  // Scanner frequency data
  const scannerFrequency = history.reduce((acc, item) => {
    const scanner = item.scanner ? `${item.scanner.brand} ${item.scanner.model}` : 'Unknown';
    acc[scanner] = (acc[scanner] || 0) + 1;
    return acc;
  }, {});

  const topScanner = Object.entries(scannerFrequency).length > 0 
    ? Object.entries(scannerFrequency).sort((a, b) => b[1] - a[1])[0][0]
    : 'No data';

  return (
    <div>
      <div className="hero">
        <h1>Analysis Dashboard</h1>
        <p>Comprehensive overview of your forensic analysis results</p>
      </div>

      {/* Stats Bar */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-value">{totalAnalyses}</div>
          <div className="metric-label">Total Analyses</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{scannerAnalyses}</div>
          <div className="metric-label">Scanner Identifications</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{tamperingChecks}</div>
          <div className="metric-label">Tampering Checks</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{tamperingRate}%</div>
          <div className="metric-label">Tampering Rate</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
        {/* Confidence Distribution Donut Chart */}
        <div className="chart-container">
          <h3 className="chart-title">Confidence Distribution</h3>
          {confidenceData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={confidenceData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {confidenceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)' }}>
              No data available yet
            </div>
          )}
        </div>

        {/* Feature Quality Radar Chart */}
        <div className="chart-container">
          <h3 className="chart-title">Feature Quality Metrics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#dfe0f5" />
              <PolarAngleAxis dataKey="feature" tick={{ fill: '#6b6b8a' }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#6b6b8a' }} />
              <Radar
                name="Quality Score"
                dataKey="value"
                stroke="#5b5fc7"
                fill="#5b5fc7"
                fillOpacity={0.6}
              />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="result-card">
        <h3>Analysis Insights</h3>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value" style={{ fontSize: '1.2rem' }}>{topScanner}</div>
            <div className="metric-label">Most Detected Scanner</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">
              {totalAnalyses > 0 ? Math.round(history.filter(h => h.scanner?.confidence >= 90).length / totalAnalyses * 100) : 0}%
            </div>
            <div className="metric-label">High Confidence Rate</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">
              {totalAnalyses > 0 ? (history.filter(h => new Date(h.timestamp) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)).length) : 0}
            </div>
            <div className="metric-label">This Week</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">
              {Object.keys(scannerFrequency).length}
            </div>
            <div className="metric-label">Unique Scanners</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      {history.length > 0 && (
        <div className="result-card">
          <h3>Recent Activity</h3>
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {history.slice(0, 5).map((item, index) => (
              <div key={item.id} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '12px 0',
                borderBottom: index < 4 ? '1px solid var(--border)' : 'none'
              }}>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>
                    {item.scanner ? `${item.scanner.brand} ${item.scanner.model}` : 'Unknown Scanner'}
                  </div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>
                    {item.fileName} • {new Date(item.timestamp).toLocaleDateString()}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className={`badge ${item.scanner?.confidence >= 90 ? 'high' : item.scanner?.confidence >= 70 ? 'medium' : 'low'}`}>
                    {item.scanner?.confidence}% confidence
                  </div>
                  {item.tampering?.detected && (
                    <div className="badge tampering" style={{ marginTop: '4px' }}>
                      Tampering Detected
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {history.length === 0 && (
        <div className="result-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <h3>No Analysis Data Yet</h3>
          <p style={{ color: 'var(--muted)', marginBottom: '24px' }}>
            Start analyzing documents to see your dashboard populate with insights and statistics.
          </p>
          <a href="/" className="button primary">
            Start First Analysis
          </a>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
