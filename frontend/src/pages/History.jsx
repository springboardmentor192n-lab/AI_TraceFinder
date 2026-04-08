import React, { useState, useEffect } from 'react';
import { Trash2, Eye, X, Download, FileText } from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

const History = () => {
  const [history, setHistory] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    const saved = localStorage.getItem('tracefinder_history');
    if (saved) setHistory(JSON.parse(saved));
  }, []);

  const deleteItem = (id) => {
    const updated = history.filter(item => item.id !== id);
    setHistory(updated);
    localStorage.setItem('tracefinder_history', JSON.stringify(updated));
  };

  const downloadPdf = (item) => {
    const doc = new jsPDF();
    doc.setFontSize(20); doc.text("TraceFinder Report", 15, 20);
    doc.setFontSize(12); doc.text(`Scanner: ${item.scanner}`, 15, 35);
    doc.text(`Confidence: ${item.confidence}%`, 15, 45);
    doc.save(`Report_${item.id}.pdf`);
  };

  return (
    <div className="max-w-7xl mx-auto p-6 lg:p-10">
      <h2 className="text-2xl font-bold text-white mb-6">Analysis History</h2>

      {history.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-10 text-center text-gray-500">
          No history found. Run an analysis on the Dashboard.
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800 text-gray-400 uppercase tracking-wider">
              <tr>
                <th className="p-4">Scanner</th>
                <th className="p-4">File</th>
                <th className="p-4">Date</th>
                <th className="p-4">Confidence</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {history.map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="p-4 font-medium text-white">{item.scanner}</td>
                  <td className="p-4 text-gray-400">{item.filename}</td>
                  <td className="p-4 text-gray-400">{item.timestamp}</td>
                  <td className="p-4"><span className="text-indigo-400 font-bold">{item.confidence}%</span></td>
                  <td className="p-4 flex gap-2 justify-end">
                    <button onClick={() => setSelectedItem(item)} className="p-2 bg-slate-700 rounded-lg hover:bg-slate-600 text-gray-300"><Eye className="w-4 h-4" /></button>
                    <button onClick={() => downloadPdf(item)} className="p-2 bg-indigo-900/30 rounded-lg hover:bg-indigo-800 text-indigo-400 border border-indigo-800"><FileText className="w-4 h-4" /></button>
                    <button onClick={() => deleteItem(item.id)} className="p-2 bg-red-900/20 rounded-lg hover:bg-red-800 text-red-400 border border-red-800"><Trash2 className="w-4 h-4" /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedItem && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-lg shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-slate-700 bg-slate-800">
              <h3 className="text-lg font-bold text-white">Analysis Details</h3>
              <button onClick={() => setSelectedItem(null)} className="text-gray-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div><p className="text-xs text-gray-500 uppercase">Scanner</p><p className="text-white font-medium">{selectedItem.scanner}</p></div>
                <div><p className="text-xs text-gray-500 uppercase">Confidence</p><p className="text-indigo-400 font-bold">{selectedItem.confidence}%</p></div>
              </div>
              <div><p className="text-xs text-gray-500 uppercase">Filename</p><p className="text-white">{selectedItem.filename}</p></div>
              <div>
                <p className="text-xs text-gray-500 uppercase mb-2">Top Predictions</p>
                <div className="bg-slate-950 rounded-lg p-3 space-y-1">
                   {selectedItem.predictions ? selectedItem.predictions.map((p, i) => (
                     <div key={i} className="flex justify-between text-sm">
                       <span className="text-gray-400">{p.label}</span>
                       <span className="text-white font-medium">{p.value}%</span>
                     </div>
                   )) : <p className="text-gray-600 text-sm">No data</p>}
                </div>
              </div>
            </div>
            <div className="p-4 border-t border-slate-700 bg-slate-800/50 flex justify-end gap-2">
               <button onClick={() => downloadPdf(selectedItem)} className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm"><Download className="w-4 h-4" /> Download PDF</button>
               <button onClick={() => setSelectedItem(null)} className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg text-sm">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default History;