import { useEffect, useState } from 'react'
import Head from 'next/head'
import axios from 'axios'
import Navbar from '../components/Navbar'
import { History, Trash2, CheckCircle, Clock, Cpu, File } from 'lucide-react'

interface HistoryEntry {
  id: string
  timestamp: string
  filename: string
  predicted_scanner: string
  confidence: number
  model_used: string
  processing_time_s: number
}

const confColor = (c: number) => c >= 0.7 ? '#22c55e' : c >= 0.4 ? '#f59e0b' : '#ef4444'

function formatTime(iso: string) {
  const d = new Date(iso + 'Z')
  return d.toLocaleString()
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const fetchHistory = () => {
    setLoading(true)
    axios.get('/api/history/')
      .then(r => { setHistory(r.data.history); setTotal(r.data.total) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchHistory() }, [])

  const clearHistory = async () => {
    if (!confirm('Clear all prediction history?')) return
    await axios.delete('/api/history/')
    setHistory([])
    setTotal(0)
  }

  return (
    <>
      <Head><title>History — TraceFinder</title></Head>
      <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
        <Navbar />
        <main style={{ maxWidth: 900, margin: '0 auto', padding: '40px 24px 80px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 32 }}>
            <div>
              <h1 style={{
                fontFamily: 'var(--font-display)', fontSize: 32, fontWeight: 800,
                letterSpacing: '-1px', color: 'var(--text-primary)', marginBottom: 8
              }}>
                Prediction History
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: 15 }}>
                {total} total prediction{total !== 1 ? 's' : ''} logged.
              </p>
            </div>
            {history.length > 0 && (
              <button className="btn-ghost" onClick={clearHistory} style={{ color: '#ef4444', borderColor: 'rgba(239,68,68,0.3)' }}>
                <Trash2 size={15} />
                Clear All
              </button>
            )}
          </div>

          {loading && (
            <div style={{ textAlign: 'center', padding: 80, color: 'var(--text-muted)' }}>
              Loading history…
            </div>
          )}

          {!loading && history.length === 0 && (
            <div className="card" style={{ padding: 64, textAlign: 'center' }}>
              <History size={40} color="var(--text-muted)" style={{ margin: '0 auto 16px' }} />
              <p style={{ color: 'var(--text-secondary)', fontWeight: 600, marginBottom: 6 }}>No predictions yet</p>
              <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
                Go to the Scan page and upload a scanned image to get started.
              </p>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {history.map((entry, i) => (
              <div key={entry.id} className="card" style={{ padding: '18px 24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    {/* Index badge */}
                    <div style={{
                      width: 32, height: 32, borderRadius: 8,
                      background: 'rgba(99,102,241,0.12)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent-light)' }}>{i + 1}</span>
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)', marginBottom: 3 }}>
                        {entry.predicted_scanner}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: 'var(--text-muted)' }}>
                          <File size={11} /> {entry.filename}
                        </span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: 'var(--text-muted)' }}>
                          <Clock size={11} /> {formatTime(entry.timestamp)}
                        </span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: 'var(--text-muted)' }}>
                          <Cpu size={11} /> {entry.model_used?.toUpperCase()}
                        </span>
                        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                          {entry.processing_time_s}s
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Confidence */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 80, height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' }}>
                      <div style={{
                        height: '100%', borderRadius: 3,
                        width: `${Math.round(entry.confidence * 100)}%`,
                        background: confColor(entry.confidence),
                        transition: 'width 0.6s ease',
                      }} />
                    </div>
                    <span style={{ fontSize: 14, fontWeight: 700, color: confColor(entry.confidence), minWidth: 40, textAlign: 'right' }}>
                      {Math.round(entry.confidence * 100)}%
                    </span>
                    <CheckCircle size={15} color={confColor(entry.confidence)} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </>
  )
}
