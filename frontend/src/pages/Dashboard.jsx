import React, { useState, useRef } from "react";
import {
  UploadCloud,
  FileSearch,
  CheckCircle2,
  ShieldCheck,
  Download,
  FileText,
  Share2,
  BarChart2
} from "lucide-react";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from "chart.js";
import { Bar } from "react-chartjs-2";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

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
    formData.append("file", file);

    try {
      console.log(`Connecting to: ${API_URL}/predict`);

      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        alert(data.error);
      } else {
        setResult(data);
        saveToHistory(data);
      }
    } catch (err) {
      console.error("Connection Error:", err);
      alert("Connection Failed. Check backend.");
    } finally {
      setIsAnalyzing(false);
    }
  };

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

  const exportJSON = () => {
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

  const generatePDF = () => {
    if (!result) return;

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
        ["Confidence", `${result.confidence.toFixed(4)}%`]
      ]
    });

    autoTable(doc, {
      startY: doc.lastAutoTable.finalY + 10,
      head: [["Metric", "Value"]],
      body: [
        ["PRNU Quality", result.metrics.prnu_quality],
        ["Noise Intensity", result.metrics.noise_intensity],
        ["Image Quality Score", result.metrics.image_quality_score],
        [
          "Metadata Status",
          result.metrics.metadata_intact ? "Intact" : "Missing"
        ]
      ]
    });

    if (previewUrl) {
      const img = new Image();
      img.src = previewUrl;
      doc.addImage(img, "JPEG", 130, 30, 60, 60);
    }

    doc.save(`TraceFinder_Report_${result.id}.pdf`);
  };

  const chartData = result && {
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
          "#DDD6FE"
        ]
      }
    ]
  };

  return (
    <div className="max-w-7xl mx-auto p-6 text-white">
      <div className="mb-6 flex items-center gap-3">
        <ShieldCheck className="text-indigo-400" />
        <h1 className="text-2xl font-bold">
          TraceFinder Dashboard
        </h1>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept="image/*,.pdf"
      />

      <button
        onClick={() => fileInputRef.current.click()}
        className="bg-indigo-600 px-4 py-2 rounded"
      >
        <UploadCloud className="inline mr-2" />
        Upload File
      </button>

      {file && <p className="mt-2">{file.name}</p>}

      <button
        onClick={runAnalysis}
        disabled={!file || isAnalyzing}
        className="ml-4 bg-green-600 px-4 py-2 rounded"
      >
        <FileSearch className="inline mr-2" />
        {isAnalyzing ? "Analyzing..." : "Run Analysis"}
      </button>

      {result && (
        <div className="mt-6 space-y-6">
          <div className="bg-gray-900 p-4 rounded">
            <h2 className="text-xl font-bold">
              {result.scanner}
            </h2>
            <p className="text-emerald-400">
              Confidence: {result.confidence.toFixed(4)}%
            </p>
          </div>

          <div className="bg-gray-900 p-4 rounded h-64">
            <Bar data={chartData} />
          </div>

          <div className="bg-gray-900 p-4 rounded">
            <h3 className="font-bold mb-2">
              Feature Quality Metrics
            </h3>
            <p>PRNU Quality: {result.metrics.prnu_quality}</p>
            <p>Noise Intensity: {result.metrics.noise_intensity}</p>
            <p>
              Image Quality Score:{" "}
              {result.metrics.image_quality_score}
            </p>
            <p>
              Metadata:{" "}
              {result.metrics.metadata_intact
                ? "Intact"
                : "Missing"}
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={generatePDF}
              className="bg-red-600 px-4 py-2 rounded"
            >
              <FileText className="inline mr-2" />
              PDF
            </button>
            <button
              onClick={exportJSON}
              className="bg-blue-600 px-4 py-2 rounded"
            >
              <Download className="inline mr-2" />
              JSON
            </button>
            <button
              onClick={() =>
                navigator.clipboard.writeText(
                  JSON.stringify(result)
                )
              }
              className="bg-purple-600 px-4 py-2 rounded"
            >
              <Share2 className="inline mr-2" />
              Share
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;