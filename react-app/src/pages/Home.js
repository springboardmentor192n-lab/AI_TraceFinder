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
    const validTypes = ['image/jpeg', 'image/png', 'image/tiff', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
      triggerToast('Please upload a valid file (JPG, PNG, TIFF, PDF)', 'warning');
      return;
    }

    if (file.size > 16 * 1024 * 1024) {
      triggerToast('File size must be less than 16MB', 'warning');
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

  const simulateAnalysis = async () => {
    setIsAnalyzing(true);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Create deterministic analysis based on file hash
    const fileHash = await createFileHash(selectedFile);
    
    // Deterministic scanner selection based on file hash
    const scanners = [
      { brand: 'Canon', model: 'LiDE 120' },
      { brand: 'Canon', model: 'CanoScan 9000F' },
      { brand: 'HP', model: 'ScanJet Pro 2500' },
      { brand: 'Epson', model: 'Perfection V39' },
      { brand: 'Epson', model: 'Perfection V550' }
    ];
    
    // Use file hash to consistently select the same scanner for the same file
    const scannerIndex = Math.abs(hashCode(fileHash)) % scanners.length;
    const selectedScanner = scanners[scannerIndex];
    
    // Generate consistent confidence based on file characteristics
    let confidence = 75 + (fileHash.length % 20); // 75-95% range
    
    const analysis = {
      type: 'scanner',
      scanner: {
        brand: selectedScanner.brand,
        model: selectedScanner.model,
        confidence: confidence,
        confidenceLevel: confidence >= 95 ? 'Very High' : confidence >= 85 ? 'High' : 'Medium'
      },
      fileName: selectedFile.name,
      fileSize: selectedFile.size,
      fileType: selectedFile.type,
      tampering: {
        detected: Math.abs(hashCode(fileHash)) % 3 === 0, // 1 in 3 chance
        confidence: Math.abs(hashCode(fileHash)) % 40 + 10, // 10-49%
        riskLevel: Math.abs(hashCode(fileHash)) % 3 === 0 ? 'Medium' : 'Low'
      },
      features: {
        prnuQuality: confidence >= 85 ? 'Excellent' : confidence >= 70 ? 'Good' : 'Fair',
        noisePattern: confidence >= 80 ? 'Very High' : 'High',
        imageQuality: confidence >= 85 ? 'Excellent' : 'High',
        metadataStatus: 'Complete'
      },
      resolution: selectedFile.name.includes('300') ? '300 dpi' : '150 dpi',
      datasetSource: Math.abs(hashCode(fileHash)) % 2 === 0 ? 'Official' : 'Wikipedia'
    };

    onAnalysis(analysis);
    setIsAnalyzing(false);
    triggerToast('Analysis complete!', 'success');
    
    // Navigate to results page
    navigate('/results', { state: { analysis } });
  };

  // Helper function to create simple hash from file
  const createFileHash = async (file) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const arrayBuffer = e.target.result;
        const uint8Array = new Uint8Array(arrayBuffer);
        let hash = 0;
        for (let i = 0; i < uint8Array.length; i++) {
          hash = ((hash << 5) - hash) + uint8Array[i];
          hash = hash & hash;
        }
        resolve(hash.toString());
      };
      reader.readAsArrayBuffer(file.slice(0, 1024)); // Only read first 1KB for speed
    });
  };

  // Helper function to convert string to hash code
  const hashCode = (str) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash;
  };

  const handleAnalyze = () => {
    if (selectedFile) {
      simulateAnalysis();
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
            Supported formats: JPG, PNG, TIFF, PDF (Max 16MB)
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.tiff,.tif,.pdf"
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
