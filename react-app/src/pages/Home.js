import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, AlertCircle } from 'lucide-react';

const Home = ({ onAnalysis, triggerToast }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (file) => {
    const validTypes = ['image/jpeg', 'image/png', 'image/tiff', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      triggerToast('Please upload a valid file (JPG, PNG, TIFF)', 'warning');
      return;
    }

    if (file.size > 200 * 1024 * 1024) {
      triggerToast('File size must be less than 200MB', 'warning');
      return;
    }

    setSelectedFile(file);
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const analyzeDocument = async () => {
    setIsAnalyzing(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Analysis failed');
      }

      const data = await response.json();
      const analysis = data.analysis;

      onAnalysis(analysis);
      triggerToast('Analysis complete!', 'success');
      navigate('/results', { state: { analysis } });
    } catch (error) {
      triggerToast(error.message || 'Analysis failed', 'warning');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAnalyze = () => {
    if (selectedFile) {
      analyzeDocument();
    }
  };

  return (
    <div>
      <div className="hero">
        <h1>Document Forensic Intelligence</h1>
        <p>Upload a scanned document to identify its scanner source and detect potential tampering</p>
        <div className="nav-pill">
          <AlertCircle size={16} />
          AI-Powered Analysis
        </div>
      </div>

      <div className="section-card">
        <div className="card-header">
          <h2>Upload Document</h2>
        </div>

        <div
          className={`upload-zone ${isDragOver ? 'dragover' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="upload-icon" />
          <div className="upload-text">
            {selectedFile ? selectedFile.name : 'Drop your document here or click to browse'}
          </div>
          <div className="upload-subtext">
            Supported formats: JPG, PNG, TIFF (Max 200MB)
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.tiff,.tif"
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />
        </div>

        {selectedFile && (
          <div style={{ marginTop: '24px', textAlign: 'center' }}>
            <button
              className="button primary"
              onClick={handleAnalyze}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                <>
                  <div className="spinner" style={{ width: '16px', height: '16px', border: '2px solid #fff', borderTop: '2px solid transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
                  Analyzing Document...
                </>
              ) : (
                <>
                  <FileText size={18} />
                  Analyze Document
                </>
              )}
            </button>
          </div>
        )}

        {isAnalyzing && (
          <div style={{ marginTop: '24px', textAlign: 'center', color: 'var(--muted)' }}>
            <div>Running forensic analysis...</div>
            <div style={{ fontSize: '0.9rem', marginTop: '8px' }}>This may take a few seconds</div>
          </div>
        )}
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

export default Home;
