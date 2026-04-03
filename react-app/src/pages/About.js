import React from 'react';
import { Shield, Users, FileText, Search, Award, BookOpen, Target, Zap } from 'lucide-react';

const About = () => {
  const applications = [
    {
      icon: <Shield size={24} />,
      title: 'Digital Forensic Investigations',
      description: 'Assist law enforcement and legal professionals in authenticating digital documents and detecting potential forgeries.',
      color: '#5b5fc7'
    },
    {
      icon: <FileText size={24} />,
      title: 'Document Authenticity Verification',
      description: 'Verify the authenticity of scanned documents in business, legal, and academic settings with AI-powered analysis.',
      color: '#4a90d9'
    },
    {
      icon: <Award size={24} />,
      title: 'Copyright & IP Protection',
      description: 'Protect intellectual property by verifying document provenance and detecting unauthorized modifications.',
      color: '#28a745'
    },
    {
      icon: <Users size={24} />,
      title: 'Law Enforcement',
      description: 'Provide forensic evidence for criminal investigations involving document fraud and tampering cases.',
      color: '#ff4560'
    },
    {
      icon: <BookOpen size={24} />,
      title: 'Academic Research',
      description: 'Support academic research in document forensics, machine learning, and digital authentication methodologies.',
      color: '#ffa726'
    },
    {
      icon: <Search size={24} />,
      title: 'Security Auditing',
      description: 'Conduct comprehensive security audits of document workflows and verify document integrity in organizations.',
      color: '#7b5cfa'
    }
  ];

  const features = [
    {
      icon: <Target size={20} />,
      title: 'Scanner Source Identification',
      description: 'Identify the specific scanner model used to create a document with 95%+ accuracy.'
    },
    {
      icon: <Zap size={20} />,
      title: 'Tampering Detection',
      description: 'Advanced algorithms detect document manipulation and digital forgery attempts.'
    },
    {
      icon: <Shield size={20} />,
      title: 'Multi-Layer Analysis',
      description: 'Combines PRNU analysis, noise pattern detection, and metadata verification.'
    },
    {
      icon: <FileText size={20} />,
      title: 'Comprehensive Reporting',
      description: 'Generate detailed forensic reports suitable for legal and professional use.'
    }
  ];

  const stats = [
    { number: '11+', label: 'Supported Scanners' },
    { number: '95%+', label: 'Accuracy Rate' },
    { number: '2M+', label: 'Analysis Parameters' },
    { number: '24/7', label: 'Available' }
  ];

  return (
    <div>
      <div className="hero">
        <h1>About TraceFinder</h1>
        <p>Advanced AI-powered document forensics for the modern digital world</p>
      </div>

      {/* Mission Statement */}
      <div className="result-card">
        <h3>Our Mission</h3>
        <p style={{ fontSize: '1.1rem', lineHeight: 1.6, color: 'var(--text)' }}>
          TraceFinder represents the cutting edge in document forensic analysis, combining state-of-the-art 
          machine learning algorithms with traditional forensic techniques to provide unprecedented accuracy 
          in scanner source identification and tampering detection. Our system analyzes millions of data points 
          from each document to deliver reliable, court-admissible results.
        </p>
      </div>

      {/* Key Statistics */}
      <div className="metrics-grid">
        {stats.map((stat, index) => (
          <div key={index} className="metric-card">
            <div className="metric-value" style={{ fontSize: '2.5rem' }}>{stat.number}</div>
            <div className="metric-label">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Key Features */}
      <div className="result-card">
        <h3>Key Features</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px' }}>
          {features.map((feature, index) => (
            <div key={index} style={{ display: 'flex', gap: '16px' }}>
              <div style={{ 
                width: '48px', 
                height: '48px', 
                borderRadius: '12px', 
                backgroundColor: 'var(--surface-soft)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--primary)',
                flexShrink: 0
              }}>
                {feature.icon}
              </div>
              <div>
                <h4 style={{ margin: '0 0 8px', color: 'var(--text)' }}>{feature.title}</h4>
                <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--muted)', lineHeight: 1.4 }}>
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Applications */}
      <div className="result-card">
        <h3>Key Applications</h3>
        <p style={{ color: 'var(--muted)', marginBottom: '24px' }}>
          TraceFinder serves diverse industries and use cases where document authenticity is critical:
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
          {applications.map((app, index) => (
            <div key={index} className="card" style={{ borderLeft: `4px solid ${app.color}` }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
                <div style={{ 
                  color: app.color, 
                  flexShrink: 0,
                  marginTop: '4px'
                }}>
                  {app.icon}
                </div>
                <div>
                  <h4 style={{ margin: '0 0 12px', color: 'var(--text)' }}>{app.title}</h4>
                  <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--muted)', lineHeight: 1.5 }}>
                    {app.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Technology Stack */}
      <div className="result-card">
        <h3>Technology & Methodology</h3>
        <div style={{ lineHeight: 1.6, color: 'var(--text)' }}>
          <h4 style={{ marginBottom: '12px', color: 'var(--primary)' }}>Hybrid CNN + SVM Architecture</h4>
          <p style={{ marginBottom: '20px' }}>
            Our system employs a sophisticated hybrid architecture combining Convolutional Neural Networks 
            for feature extraction with Support Vector Machines for classification. This approach provides 
            both the pattern recognition capabilities of deep learning and the statistical rigor of 
            traditional machine learning.
          </p>

          <h4 style={{ marginBottom: '12px', color: 'var(--primary)' }}>Multi-Scale Analysis</h4>
          <p style={{ marginBottom: '20px' }}>
            TraceFinder analyzes documents at multiple scales - from pixel-level noise patterns to 
            document-wide metadata consistency. This comprehensive approach ensures that no evidence 
            of tampering goes unnoticed, regardless of the sophistication of the forgery attempt.
          </p>

          <h4 style={{ marginBottom: '12px', color: 'var(--primary)' }}>PRNU-Based Fingerprinting</h4>
          <p>
            Photo Response Non-Uniformity (PRNU) patterns serve as unique fingerprints for each scanner, 
            allowing us to identify the exact device used to create a document. Our proprietary PRNU 
            extraction algorithms achieve industry-leading accuracy rates across multiple scanner manufacturers.
          </p>
        </div>
      </div>

      {/* Supported Scanners */}
      <div className="result-card">
        <h3>Supported Scanner Models</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          {[
            'Canon LiDE 120', 'Canon CanoScan 9000F', 'HP ScanJet Pro 2500', 
            'Epson Perfection V39', 'Epson Perfection V550', 'Canon PIXMA',
            'Brother MFC', 'Xerox WorkCentre', 'Fujitsu ScanSnap',
            'Kodak ScanMate', 'Unknown/Detect'
          ].map((scanner, index) => (
            <div key={index} style={{
              backgroundColor: 'var(--surface-soft)',
              padding: '12px 16px',
              borderRadius: '8px',
              border: '1px solid var(--border)',
              fontSize: '0.9rem',
              textAlign: 'center'
            }}>
              {scanner}
            </div>
          ))}
        </div>
      </div>

      {/* Contact/Support */}
      <div className="result-card" style={{ textAlign: 'center' }}>
        <h3>Get Started with TraceFinder</h3>
        <p style={{ color: 'var(--muted)', marginBottom: '24px' }}>
          Ready to enhance your document forensics capabilities? Start analyzing documents today with our 
          user-friendly interface and powerful AI-driven analysis.
        </p>
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <a href="/" className="button primary">
            Start Analysis
          </a>
          <a href="/dashboard" className="button secondary">
            View Dashboard
          </a>
          <button className="button outline">
            Documentation
          </button>
        </div>
      </div>
    </div>
  );
};

export default About;
