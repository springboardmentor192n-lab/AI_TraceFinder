import React, { useState, useRef } from 'react';
import { UploadCloud, FileSearch, ScanLine, CheckCircle2, ShieldCheck, Download, FileText, Share2, BarChart2 } from 'lucide-react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
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

  // API URL Configuration
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setResult(null);
    }
  };

  const runAnalysis = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();

      if (data.error) {
        alert("Error: " + data.error);
      } else {
        setResult(data);
        saveToHistory(data);
      }
    } catch (err) {
      alert("Failed to connect to server. Check if backend is running.");
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
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${result.id}.json`;
    a.click();
  };

  const generatePDF = () => {
    if (!result) return;
    try {
      const doc = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' });

      doc.setFont("helvetica", "bold");
      doc.setFontSize(22);
      doc.setTextColor(79, 70, 229);
      doc.text("TraceFinder Forensic Report", 15, 20);

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(100);
      doc.text("Forensic Scanner Identification Analysis", 15, 27);

      doc.setFont("helvetica", "bold");
      doc.setFontSize(14);
      doc.setTextColor(0);
      doc.text("File Information", 15, 40);

      autoTable(doc, {
        startY: 43, head: [], body: [
          ['Report ID:', String(result.id)],
          ['Timestamp:', result.timestamp],
          ['Filename:', result.filename],
          ['Status:', result.status || 'Analyzed']
        ], theme: 'plain', styles: { fontSize: 10 }, columnStyles: { 0: { fontStyle: 'bold', cellWidth: 40 } }
      });

      let nextY = doc.lastAutoTable.finalY + 12;
      doc.setFont("helvetica", "bold"); doc.setFontSize(14); doc.text("Prediction Result", 15, nextY);
      autoTable(doc, {
        startY: nextY + 3, head: [['Predicted Scanner', 'Confidence Score']], body: [[result.scanner, `${result.confidence}%`]],
        headStyles: { fillColor: [79, 70, 229] }, theme: 'striped',
      });

      if (result.predictions && result.predictions.length > 0) {
        nextY = doc.lastAutoTable.finalY + 12;
        doc.setFont("helvetica", "bold"); doc.setFontSize(14); doc.text("Confidence Distribution (Top 5)", 15, nextY);
        const predictionRows = result.predictions.slice(0, 5).map((p, i) => [i + 1, p.label, `${p.value}%`]);
        autoTable(doc, {
          startY: nextY + 3, head: [['Rank', 'Scanner Model', 'Probability']], body: predictionRows,
          headStyles: { fillColor: [71, 85, 105] }, theme: 'grid',
        });
      }

      if (result.metrics) {
        nextY = doc.lastAutoTable.finalY + 12;
        doc.setFont("helvetica", "bold"); doc.setFontSize(14); doc.text("Feature Quality Metrics", 15, nextY);
        const metrics = result.metrics;
        autoTable(doc, {
          startY: nextY + 3, head: [['Metric', 'Value', 'Status']], body: [
            ['PRNU Quality Score', metrics.prnu_quality || 'N/A', parseFloat(metrics.prnu_quality) > 0.7 ? 'High' : 'Low'],
            ['Noise Intensity', metrics.noise_intensity || 'N/A', 'Detected'],
            ['Image Quality Score', metrics.image_quality_score || 'N/A', parseFloat(metrics.image_quality_score) > 80 ? 'Good' : 'Poor'],
            ['Metadata Status', metrics.metadata_intact ? 'Intact' : 'Missing', metrics.metadata_intact ? 'Verified' : 'Suspicious']
          ], headStyles: { fillColor: [16, 185, 129] }, theme: 'striped',
        });
      }

      doc.save(`TraceFinder_Report_${result.id}.pdf`);
    } catch (error) {
      console.error("PDF Error:", error);
      alert("Could not generate PDF.");
    }
  };

  const shareResult = () => {
    const text = `Scanner Analysis Result: ${result.scanner} with ${result.confidence}% confidence.`;
    if (navigator.share) navigator.share({ title: 'TraceFinder Result', text: text });
    else { navigator.clipboard.writeText(text); alert("Result copied to clipboard!"); }
  };

  const chartData = result ? {
    labels: result.predictions.map(p => p.label),
    datasets: [{
      label: 'Confidence %', data: result.predictions.map(p => p.value),
      backgroundColor: ['rgba(99, 102, 241, 0.8)', 'rgba(139, 92, 246, 0.7)', 'rgba(168, 85, 247, 0.6)', 'rgba(192, 132, 252, 0.5)', 'rgba(221, 214, 254, 0.4)'],
    }]
  } : null;

  return (
    <div className="max-w-7xl mx-auto p-6 lg:p-10">
      {/* Header Banner */}
      <div className="mb-8 bg-gradient-to-r from-slate-900 to-slate-800 border border-slate-700 rounded-xl p-5">
        <div className="flex items-center gap-4">
          <ShieldCheck className="w-8 h-8 text-indigo-400" />
          <div>
            <h2 className="text-lg font-semibold text-white">Scanner Identification Dashboard</h2>
            <p className="text-sm text-gray-400">Upload a document to analyze scanner noise patterns.</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column */}
        <div className="lg:col-span-5 space-y-6">
          <div onClick={() => fileInputRef.current.click()} className={`bg-slate-900 border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all min-h-[320px] ${ file ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-slate-700 hover:border-indigo-500' }`}>
            <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept="image/*,.pdf" />
            {file ? (
              <div className="text-center">
                <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
                <p className="text-white font-medium text-sm">{file.name}</p>
              </div>
            ) : (
              <>
                <UploadCloud className="w-12 h-12 text-gray-500 mb-4" />
                <p className="text-gray-300 font-medium">Upload Suspect Document</p>
              </>
            )}
          </div>

          {previewUrl && (
            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
              <div className="p-3 border-b border-slate-800"><span className="text-xs text-gray-500 uppercase font-bold">Preview</span></div>
              <div className="p-4 bg-slate-950 flex items-center justify-center">
                <img src={previewUrl} alt="Preview" className="max-h-64 object-contain rounded shadow-2xl" />
              </div>
            </div>
          )}

          <button onClick={runAnalysis} disabled={!file || isAnalyzing} className={`w-full px-8 py-3 rounded-lg font-bold text-white flex items-center justify-center gap-2 transition-all ${ !file ? 'bg-gray-700' : isAnalyzing ? 'bg-yellow-600' : 'bg-indigo-600 hover:bg-indigo-500' }`}>
            {isAnalyzing ? "Analyzing..." : "Run Analysis"}
          </button>
        </div>

        {/* Right Column */}
        <div className="lg:col-span-7 space-y-6">
          {!result && !isAnalyzing && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl min-h-[600px] flex items-center justify-center text-gray-600">
              <div className="text-center">
                <BarChart2 className="w-16 h-16 mx-auto mb-4 opacity-20" />
                <p>Analysis data will appear here</p>
              </div>
            </div>
          )}

          {isAnalyzing && (
             <div className="bg-slate-900 border border-slate-800 rounded-xl min-h-[600px] flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                    <p className="mt-4">Extracting Features...</p>
                </div>
             </div>
          )}

          {result && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-900 border border-emerald-500/30 rounded-xl p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <CheckCircle2 className="text-emerald-500 w-5 h-5" />
                    <h3 className="font-bold text-white">Predicted Device</h3>
                  </div>
                  <h2 className="text-3xl font-bold text-white mb-2">{result.scanner}</h2>
                  <div className="mt-4">
                    <div className="flex justify-between text-xs mb-1">
                      <span>Confidence Score</span>
                      <span className="text-indigo-400 font-bold">{result.confidence}%</span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-3">
                      <div className="bg-gradient-to-r from-indigo-600 to-emerald-500 h-3 rounded-full" style={{ width: `${result.confidence}%` }}></div>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                  <h3 className="font-bold text-white mb-4 text-sm">Confidence Distribution</h3>
                  <div className="h-40">
                     {chartData && <Bar data={chartData} options={{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />}
                  </div>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                <h3 className="font-bold text-white mb-4 text-sm">Feature Quality Metrics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <MetricCard label="PRNU Quality" value={result.metrics?.prnu_quality} max="1.0" color="indigo" />
                  <MetricCard label="Noise Level" value={result.metrics?.noise_intensity} max="100" color="red" />
                  <MetricCard label="Image Quality" value={result.metrics?.image_quality_score} max="100" color="emerald" />
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-700">
                    <p className="text-xs text-gray-500 mb-1">Metadata Status</p>
                    <p className={`text-sm font-bold ${result.metrics?.metadata_intact ? 'text-emerald-400' : 'text-red-400'}`}>
                      {result.metrics?.metadata_intact ? 'Intact' : 'Missing'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                 <button onClick={generatePDF} className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-4 py-3 rounded-lg text-sm font-medium transition-colors">
                    <FileText className="w-4 h-4 text-red-400" /> PDF Report
                 </button>
                 <button onClick={exportJSON} className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-4 py-3 rounded-lg text-sm font-medium transition-colors">
                    <Download className="w-4 h-4 text-blue-400" /> Export JSON
                 </button>
                 <button onClick={shareResult} className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-4 py-3 rounded-lg text-sm font-medium transition-colors">
                    <Share2 className="w-4 h-4 text-green-400" /> Share
                 </button>
                 <button onClick={exportJSON} className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-3 rounded-lg text-sm font-medium transition-colors">
                    <Download className="w-4 h-4" /> Save Result
                 </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ label, value, max, color }) => {
  const val = value || 0;
  const percent = (val / parseFloat(max)) * 100;
  const colors = { indigo: 'bg-indigo-500', red: 'bg-red-500', emerald: 'bg-emerald-500' };
  return (
    <div className="bg-slate-950 p-3 rounded-lg border border-slate-700">
      <p className="text-xs text-gray-500 mb-2">{label}</p>
      <div className="w-full bg-slate-800 rounded-full h-1.5 mb-2">
        <div className={`${colors[color]} h-1.5 rounded-full`} style={{ width: `${percent}%` }}></div>
      </div>
      <p className="text-sm font-bold text-white">{val}</p>
    </div>
  )
};

export default Dashboard;