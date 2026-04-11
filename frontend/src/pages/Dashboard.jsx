import React, { useState, useRef } from 'react';
import {
  UploadCloud, FileSearch, ScanLine, CheckCircle2,
  ShieldCheck, Download, FileText, Share2, BarChart2
} from 'lucide-react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

const Dashboard = () => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const API_URL =
    import.meta.env.VITE_API_URL || "http://localhost:5000";

  // Handle File Selection
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setResult(null);
    }
  };

  // Run Analysis
  const runAnalysis = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      console.log("Connecting to:", `${API_URL}/predict`);

      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server Error: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        alert("Server Error: " + data.error);
      } else {
        console.log("Backend Response:", data);

        // Ensure metrics exist
        data.metrics = data.metrics || {
          prnu_quality: 0,
          noise_intensity: 0,
          image_quality_score: 0,
          metadata_intact: false,
        };

        setResult(data);
        saveToHistory(data);
      }
    } catch (err) {
      console.error("TraceFinder Connection Error:", err);
      alert(`Connection Failed: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Save to Local Storage
  const saveToHistory = (data) => {
    const history = JSON.parse(
      localStorage.getItem("tracefinder_history") || "[]"
    );
    history.unshift(data);
    if (history.length > 20) history.pop();
    localStorage.setItem(
      "tracefinder_history",
      JSON.stringify(history)
    );
  };

  // Export JSON
  const exportJSON = () => {
    if (!result) return;
    const blob = new Blob(
      [JSON.stringify(result, null, 2)],
      { type: "application/json" }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report_${result.id}.json`;
    a.click();
  };

  // Generate PDF Report
  const generatePDF = () => {
    if (!result) return;

    const metrics = result.metrics || {};

    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text("TraceFinder Forensic Report", 14, 20);

    autoTable(doc, {
      startY: 30,
      head: [["Field", "Value"]],
      body: [
        ["Report ID", result.id],
        ["Filename", result.filename],
        ["Timestamp", result.timestamp],
        ["Predicted Scanner", result.scanner],
        ["Confidence", `${result.confidence}%`],
      ],
    });

    autoTable(doc, {
      startY: doc.lastAutoTable.finalY + 10,
      head: [["Metric", "Value"]],
      body: [
        ["PRNU Quality", metrics.prnu_quality ?? "N/A"],
        ["Noise Intensity", metrics.noise_intensity ?? "N/A"],
        ["Image Quality Score", metrics.image_quality_score ?? "N/A"],
        [
          "Metadata Status",
          metrics.metadata_intact ? "Intact" : "Missing",
        ],
      ],
    });

    doc.save(`TraceFinder_Report_${result.id}.pdf`);
  };

  // Share Result
  const shareResult = () => {
    if (!result) return;
    const text = `Scanner Analysis Result: ${result.scanner} with ${result.confidence}% confidence.`;

    if (navigator.share) {
      navigator.share({
        title: "TraceFinder Result",
        text,
      });
    } else {
      navigator.clipboard.writeText(text);
      alert("Result copied to clipboard!");
    }
  };

  // Chart Data
  const chartData = result
    ? {
        labels: result.predictions.map((p) => p.label),
        datasets: [
          {
            label: "Confidence %",
            data: result.predictions.map((p) => p.value),
            backgroundColor: [
              "#6366F1",
              "#8B5CF6",
              "#A855F7",
              "#C084FC",
              "#DDD6FE",
            ],
          },
        ],
      }
    : null;

  return (
    <div className="max-w-7xl mx-auto p-6 lg:p-10 min-h-screen bg-slate-950 text-slate-200">
      {/* Header */}
      <div className="mb-8 bg-slate-900 border border-slate-700 rounded-xl p-5">
        <div className="flex items-center gap-4">
          <ShieldCheck className="w-8 h-8 text-indigo-400" />
          <div>
            <h2 className="text-xl font-bold text-white">
              Scanner Identification Dashboard
            </h2>
            <p className="text-sm text-gray-400">
              Upload a document to analyze microscopic noise patterns.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Upload Section */}
        <div className="lg:col-span-5 space-y-6">
          <div
            onClick={() => fileInputRef.current.click()}
            className="bg-slate-900 border-2 border-dashed border-slate-700 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer min-h-[300px]"
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
                <p className="text-white">{file.name}</p>
              </>
            ) : (
              <>
                <UploadCloud className="w-12 h-12 text-gray-500 mb-4" />
                <p>Upload Image or PDF</p>
              </>
            )}
          </div>

          <button
            onClick={runAnalysis}
            disabled={!file || isAnalyzing}
            className="w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-lg font-bold"
          >
            {isAnalyzing ? "Analyzing..." : "Run Forensic Analysis"}
          </button>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-7 space-y-6">
          {!result && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl min-h-[400px] flex items-center justify-center">
              <BarChart2 className="w-16 h-16 opacity-20" />
            </div>
          )}

          {result && (
            <>
              {/* Prediction */}
              <div className="bg-slate-900 p-6 rounded-xl">
                <h2 className="text-2xl font-bold">
                  {result.scanner}
                </h2>
                <p className="text-emerald-400">
                  Confidence: {result.confidence}%
                </p>
              </div>

              {/* Chart */}
              <div className="bg-slate-900 p-6 rounded-xl h-64">
                {chartData && (
                  <Bar
                    data={chartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: { legend: { display: false } },
                    }}
                  />
                )}
              </div>

              {/* Metrics */}
              <div className="bg-slate-900 p-6 rounded-xl">
                <h3 className="font-bold mb-4">
                  Feature Quality Metrics
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <MetricCard
                    label="PRNU Quality"
                    value={result.metrics.prnu_quality}
                    max="1.0"
                    color="indigo"
                  />
                  <MetricCard
                    label="Noise Level"
                    value={result.metrics.noise_intensity}
                    max="100"
                    color="red"
                  />
                  <MetricCard
                    label="Image Quality"
                    value={result.metrics.image_quality_score}
                    max="100"
                    color="emerald"
                  />
                  <div className="bg-slate-800 p-4 rounded-lg">
                    <p className="text-xs text-gray-400">
                      Metadata Status
                    </p>
                    <p className="font-bold">
                      {result.metrics.metadata_intact
                        ? "Intact"
                        : "Missing"}
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button
                  onClick={generatePDF}
                  className="bg-slate-800 p-3 rounded-lg"
                >
                  <FileText className="inline mr-2" /> PDF
                </button>
                <button
                  onClick={exportJSON}
                  className="bg-slate-800 p-3 rounded-lg"
                >
                  <Download className="inline mr-2" /> JSON
                </button>
                <button
                  onClick={shareResult}
                  className="bg-slate-800 p-3 rounded-lg"
                >
                  <Share2 className="inline mr-2" /> Share
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// Metric Card Component
const MetricCard = ({ label, value, max, color }) => {
  const val = value || 0;
  const percent = (val / parseFloat(max)) * 100;

  const colors = {
    indigo: "bg-indigo-500",
    red: "bg-red-500",
    emerald: "bg-emerald-500",
  };

  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <p className="text-xs text-gray-400">{label}</p>
      <div className="w-full bg-slate-700 rounded-full h-2 my-2">
        <div
          className={`${colors[color]} h-2 rounded-full`}
          style={{ width: `${percent}%` }}
        ></div>
      </div>
      <p className="text-white font-bold">{val}</p>
    </div>
  );
};

export default Dashboard;