import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  CheckCircle2,
  ShieldCheck,
  Download,
  FileText,
  Share2,
  BarChart2,
  FileSearch
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
  const [isPDF, setIsPDF] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const fileInputRef = useRef(null);
  const chartRef = useRef(null);

  // Backend URL
  const API_URL =
    import.meta.env.VITE_API_URL ||
    "https://ai-tracefinder-backend-nt5y.onrender.com";

  /* ---------------- File Handling ---------------- */
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setResult(null);

    if (selectedFile.type === "application/pdf") {
      setPreviewUrl(null);
      setIsPDF(true);
    } else {
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setIsPDF(false);
    }
  };

  /* ---------------- Run Analysis ---------------- */
  const runAnalysis = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.error) {
        alert(`Error: ${data.error}`);
      } else {
        setResult(data);
        saveToHistory(data);
      }
    } catch (error) {
      alert("Failed to connect to server.");
      console.error(error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  /* ---------------- History ---------------- */
  const saveToHistory = (data) => {
    const history = JSON.parse(
      localStorage.getItem("tracefinder_history") || "[]"
    );
    history.unshift(data);
    if (history.length > 20) history.pop();
    localStorage.setItem("tracefinder_history", JSON.stringify(history));
  };

  /* ---------------- Export JSON ---------------- */
  const exportJSON = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `TraceFinder_Report_${result.id}.json`;
    a.click();
  };

  /* ---------------- Generate PDF ---------------- */
  const generatePDF = () => {
    if (!result) return;

    const doc = new jsPDF();

    doc.setFontSize(20);
    doc.setTextColor(79, 70, 229);
    doc.text("TraceFinder Forensic Report", 14, 20);

    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text("Scanner Identification Analysis", 14, 27);

    autoTable(doc, {
      startY: 35,
      theme: "plain",
      body: [
        ["Report ID", result.id],
        ["Timestamp", result.timestamp],
        ["Filename", result.filename],
        ["Predicted Scanner", result.scanner],
        ["Confidence", `${result.confidence}%`],
      ],
      styles: { fontSize: 10 },
      columnStyles: { 0: { fontStyle: "bold" } },
    });

    let nextY = doc.lastAutoTable.finalY + 10;

    /* Top Predictions */
    if (result.predictions) {
      autoTable(doc, {
        startY: nextY,
        head: [["Rank", "Scanner", "Confidence (%)"]],
        body: result.predictions.map((p, i) => [
          i + 1,
          p.label,
          p.value,
        ]),
        headStyles: { fillColor: [79, 70, 229] },
      });
      nextY = doc.lastAutoTable.finalY + 10;
    }

    /* Metrics */
    if (result.metrics) {
      autoTable(doc, {
        startY: nextY,
        head: [["Metric", "Value"]],
        body: [
          ["PRNU Quality", result.metrics.prnu_quality],
          ["Noise Intensity", result.metrics.noise_intensity],
          ["Image Quality", result.metrics.image_quality_score],
          [
            "Metadata Status",
            result.metrics.metadata_intact ? "Intact" : "Missing",
          ],
        ],
        headStyles: { fillColor: [16, 185, 129] },
      });
      nextY = doc.lastAutoTable.finalY + 10;
    }

    /* Add Chart Image */
    const chartInstance = chartRef.current;
    if (chartInstance) {
      const chartImage = chartInstance.toBase64Image();
      doc.text("Confidence Distribution", 14, nextY);
      doc.addImage(chartImage, "PNG", 15, nextY + 5, 180, 80);
    }

    doc.save(`TraceFinder_Report_${result.id}.pdf`);
  };

  /* ---------------- Share Result ---------------- */
  const shareResult = () => {
    if (!result) return;
    const text = `Scanner Analysis Result: ${result.scanner} (${result.confidence}% confidence).`;

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

  /* ---------------- Chart Data ---------------- */
  const chartData = result
    ? {
        labels: result.predictions.map((p) => p.label),
        datasets: [
          {
            label: "Confidence %",
            data: result.predictions.map((p) => p.value),
            backgroundColor: [
              "rgba(99,102,241,0.8)",
              "rgba(139,92,246,0.7)",
              "rgba(168,85,247,0.6)",
              "rgba(192,132,252,0.5)",
              "rgba(221,214,254,0.4)",
            ],
          },
        ],
      }
    : null;

  return (
    <div className="max-w-7xl mx-auto p-6 lg:p-10">
      {/* Header */}
      <div className="mb-8 bg-gradient-to-r from-slate-900 to-slate-800 border border-slate-700 rounded-xl p-5">
        <div className="flex items-center gap-4">
          <ShieldCheck className="w-8 h-8 text-indigo-400" />
          <div>
            <h2 className="text-lg font-semibold text-white">
              Scanner Identification Dashboard
            </h2>
            <p className="text-sm text-gray-400">
              Upload a document to analyze scanner noise patterns.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Upload Section */}
        <div className="lg:col-span-5 space-y-6">
          <div
            onClick={() => fileInputRef.current.click()}
            className="bg-slate-900 border-2 border-dashed border-slate-700 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer min-h-[320px]"
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
                <p className="text-white text-sm">{file.name}</p>
              </>
            ) : (
              <>
                <UploadCloud className="w-12 h-12 text-gray-500 mb-4" />
                <p className="text-gray-300 font-medium">
                  Upload Suspect Document
                </p>
              </>
            )}
          </div>

          {/* Preview */}
          {previewUrl && !isPDF && (
            <img
              src={previewUrl}
              alt="Preview"
              className="rounded-lg shadow-lg max-h-64 mx-auto"
            />
          )}

          {isPDF && file && (
            <div className="bg-slate-900 p-6 text-center rounded-lg border border-slate-700">
              <FileSearch className="w-12 h-12 mx-auto text-red-400" />
              <p className="text-gray-300 mt-2">
                PDF uploaded: {file.name}
              </p>
            </div>
          )}

          <button
            onClick={runAnalysis}
            disabled={!file || isAnalyzing}
            className="w-full px-8 py-3 rounded-lg font-bold text-white bg-indigo-600 hover:bg-indigo-500"
          >
            {isAnalyzing ? "Analyzing..." : "Run Analysis"}
          </button>
        </div>

        {/* Results */}
        <div className="lg:col-span-7 space-y-6">
          {result && (
            <>
              {/* Prediction Card */}
              <div className="bg-slate-900 border border-emerald-500/30 rounded-xl p-6">
                <h2 className="text-3xl font-bold text-white">
                  {result.scanner}
                </h2>
                <p className="text-indigo-400 font-bold">
                  Confidence: {result.confidence}%
                </p>
              </div>

              {/* Chart */}
              <div className="bg-slate-900 p-6 rounded-xl">
                <Bar
                  ref={chartRef}
                  data={chartData}
                  options={{
                    responsive: true,
                    plugins: { legend: { display: false } },
                  }}
                />
              </div>

              {/* Metrics */}
              <div className="bg-slate-900 p-6 rounded-xl grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricCard
                  label="PRNU Quality"
                  value={result.metrics?.prnu_quality}
                />
                <MetricCard
                  label="Noise Level"
                  value={result.metrics?.noise_intensity}
                />
                <MetricCard
                  label="Image Quality"
                  value={result.metrics?.image_quality_score}
                />
                <MetricCard
                  label="Metadata"
                  value={
                    result.metrics?.metadata_intact ? "Intact" : "Missing"
                  }
                />
              </div>

              {/* Actions */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button
                  onClick={generatePDF}
                  className="bg-slate-800 p-3 rounded-lg text-white"
                >
                  <FileText className="inline mr-2" /> PDF
                </button>
                <button
                  onClick={exportJSON}
                  className="bg-slate-800 p-3 rounded-lg text-white"
                >
                  <Download className="inline mr-2" /> JSON
                </button>
                <button
                  onClick={shareResult}
                  className="bg-slate-800 p-3 rounded-lg text-white"
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

/* ---------------- Metric Card ---------------- */
const MetricCard = ({ label, value }) => (
  <div className="bg-slate-950 p-3 rounded-lg border border-slate-700 text-center">
    <p className="text-xs text-gray-500">{label}</p>
    <p className="text-lg font-bold text-white">
      {value !== undefined ? value : "N/A"}
    </p>
  </div>
);

export default Dashboard;