import React, { useState, useRef, useEffect } from 'react';
import {
  UploadCloud, FileSearch, ScanLine, CheckCircle2, ShieldCheck,
  Download, FileText, Share2, BarChart2
} from 'lucide-react';
import {
  Chart as ChartJS, ArcElement, Tooltip, Legend,
  BarElement, CategoryScale, LinearScale
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const Dashboard = () => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  // Backend URL from environment variable
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

  // Cleanup object URLs to prevent memory leaks
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/jpg",
      "application/pdf"
    ];

    if (!allowedTypes.includes(selectedFile.type)) {
      alert("Unsupported file type. Please upload JPG, PNG, or PDF.");
      return;
    }

    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setResult(null);
  };

  const runAnalysis = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log("Attempting to connect to:", `${API_URL}/predict`);

      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server Error (${response.status}): ${errorText}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setResult(data);
      saveToHistory(data);

    } catch (err) {
      console.error("TraceFinder Connection Error:", err);
      alert(
        `Connection Failed: ${err.message}\n\n` +
        `Please verify that:\n` +
        `1. The backend is deployed and running.\n` +
        `2. VITE_API_URL is set correctly.\n` +
        `3. CORS is enabled on the backend.`
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const saveToHistory = (data) => {
    const history = JSON.parse(localStorage.getItem('tracefinder_history') || '[]');
    history.unshift(data);
    if (history.length > 20) history.pop();
    localStorage.setItem('tracefinder_history', JSON.stringify(history));
  };

  const exportJSON = () => {
    if (!result) return;

    const blob = new Blob(
      [JSON.stringify(result, null, 2)],
      { type: 'application/json' }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `TraceFinder_Report_${result.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const generatePDF = () => {
    if (!result) return;

    try {
      const doc = new jsPDF();
      doc.setFont("helvetica", "bold");
      doc.setFontSize(20);
      doc.setTextColor(79, 70, 229);
      doc.text("TraceFinder Forensic Report", 14, 20);

      doc.setFontSize(10);
      doc.setTextColor(100);
      doc.text("Scanner Identification Analysis", 14, 26);

      autoTable(doc, {
        startY: 35,
        theme: 'striped',
        head: [['Field', 'Value']],
        body: [
          ['Report ID', String(result.id)],
          ['Timestamp', result.timestamp],
          ['Filename', result.filename],
          ['Scanner', result.scanner],
          ['Confidence', `${result.confidence}%`],
        ],
      });

      if (result.predictions) {
        autoTable(doc, {
          startY: doc.lastAutoTable.finalY + 10,
          head: [['Rank', 'Scanner Model', 'Probability']],
          body: result.predictions.map((p, i) => [
            i + 1,
            p.label,
            `${p.value}%`
          ]),
        });
      }

      doc.save(`TraceFinder_Report_${result.id}.pdf`);
    } catch (error) {
      console.error("PDF Error:", error);
      alert("Could not generate PDF.");
    }
  };

  const shareResult = () => {
    if (!result) return;

    const text = `Scanner Analysis Result: ${result.scanner} with ${result.confidence}% confidence.`;

    if (navigator.share) {
      navigator.share({
        title: 'TraceFinder Result',
        text: text
      });
    } else {
      navigator.clipboard.writeText(text);
      alert("Result copied to clipboard!");
    }
  };

  const chartData = result ? {
    labels: result.predictions.map(p => p.label),
    datasets: [
      {
        label: 'Confidence %',
        data: result.predictions.map(p => p.value),
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(139, 92, 246, 0.7)',
          'rgba(168, 85, 247, 0.6)',
          'rgba(192, 132, 252, 0.5)',
          'rgba(221, 214, 254, 0.4)',
        ],
      },
    ],
  } : null;

  return (
    <div className="max-w-7xl mx-auto p-6 lg:p-10 min-h-screen bg-slate-950 text-slate-200">
      {/* Header */}
      <div className="mb-8 bg-gradient-to-r from-slate-900 to-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg">
        <div className="flex items-center gap-4">
          <ShieldCheck className="w-8 h-8 text-indigo-400" />
          <div>
            <h2 className="text-xl font-bold text-white">
              Scanner Identification Dashboard
            </h2>
            <p className="text-sm text-gray-400">
              Upload a forensic document to analyze microscopic noise patterns.
            </p>
          </div>
        </div>
      </div>

      {/* Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Upload Section */}
        <div className="lg:col-span-5 space-y-6">
          <div
            onClick={() => fileInputRef.current.click()}
            className="bg-slate-900 border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all min-h-[320px]"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
              accept="image/*,.pdf"
            />

            {file ? (
              <>
                <CheckCircle2 className="w-12 h-12 text-emerald-500 mb-3" />
                <p className="text-white font-medium text-sm break-all">
                  {file.name}
                </p>
                <p className="text-xs text-slate-500 mt-2">
                  Click to replace file
                </p>
              </>
            ) : (
              <>
                <UploadCloud className="w-12 h-12 text-gray-500 mb-4" />
                <p className="text-gray-300 font-medium">
                  Upload Suspect Document
                </p>
                <p className="text-xs text-slate-500 mt-2">
                  Supports JPG, PNG, PDF
                </p>
              </>
            )}
          </div>

          {/* Preview */}
          {previewUrl && (
            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-inner">
              <div className="p-3 border-b border-slate-800 flex justify-between items-center">
                <span className="text-xs text-gray-500 uppercase font-bold">
                  Preview
                </span>
                <ScanLine className="w-4 h-4 text-slate-500" />
              </div>
              <div className="p-4 bg-slate-950 flex items-center justify-center">
                {file.type === "application/pdf" ? (
                  <embed
                    src={previewUrl}
                    type="application/pdf"
                    className="w-full h-64 rounded"
                  />
                ) : (
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="max-h-64 object-contain rounded"
                  />
                )}
              </div>
            </div>
          )}

          {/* Analyze Button */}
          <button
            onClick={runAnalysis}
            disabled={!file || isAnalyzing}
            className={`w-full px-8 py-4 rounded-lg font-bold text-white flex items-center justify-center gap-2 shadow-lg transition-all ${
              !file
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : isAnalyzing
                ? 'bg-amber-600 cursor-wait'
                : 'bg-indigo-600 hover:bg-indigo-500'
            }`}
          >
            {isAnalyzing ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Analyzing Micro-patterns...
              </>
            ) : (
              <>
                <FileSearch className="w-5 h-5" />
                Run Forensic Analysis
              </>
            )}
          </button>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-7 space-y-6">
          {!result && !isAnalyzing && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl min-h-[500px] flex items-center justify-center text-gray-600">
              <div className="text-center">
                <BarChart2 className="w-16 h-16 mx-auto mb-4 opacity-10" />
                <p className="text-lg">
                  Upload and process a file to see results
                </p>
              </div>
            </div>
          )}

          {isAnalyzing && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl min-h-[500px] flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                <p className="mt-6 text-indigo-400 font-medium animate-pulse">
                  Extracting PRNU Noise Features...
                </p>
              </div>
            </div>
          )}

          {result && (
            <div className="bg-slate-900 border border-emerald-500/30 rounded-xl p-6 shadow-xl">
              <h2 className="text-2xl font-bold text-white">
                {result.scanner}
              </h2>
              <p className="text-emerald-400 font-semibold">
                Confidence: {result.confidence}%
              </p>

              {chartData && (
                <div className="mt-6">
                  <Bar data={chartData} />
                </div>
              )}

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
                <button onClick={generatePDF} className="btn">PDF</button>
                <button onClick={exportJSON} className="btn">JSON</button>
                <button onClick={shareResult} className="btn">Share</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;