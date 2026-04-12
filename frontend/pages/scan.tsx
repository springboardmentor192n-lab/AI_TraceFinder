import { useState, useCallback, useEffect, useRef } from 'react'
import Head from 'next/head'
import axios from 'axios'
import { useDropzone } from 'react-dropzone'
import Navbar from '../components/Navbar'
import {
  Upload, Scan, X, Download, AlertTriangle,
  CheckCircle, Loader, FileText, Cpu, Eye, File
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Cell
} from 'recharts'

interface PredictionResult {
  prediction: {
    predicted_scanner: string
    confidence: number
    all_probabilities: Record<string, number>
    model_used: string
    is_mock: boolean
  }
  visualizations: { noise_map: string; fft_map: string }
  feature_stats: {
    prnu: Record<string, number>
    fft_power: number[]
    lbp_histogram: number[]
  }
  meta: { filename: string; size_mb: number; processing_time_s: number; is_mock_model: boolean }
}

const confColor = (c: number) => c >= 0.7 ? '#22c55e' : c >= 0.4 ? '#f59e0b' : '#ef4444'
const confLabel = (c: number) => c >= 0.7 ? 'High' : c >= 0.4 ? 'Medium' : 'Low'
const isPDF = (f: File | null) => f?.name?.toLowerCase().endsWith('.pdf') ?? false
const isTIF = (f: File | null) => f?.name?.toLowerCase().match(/\.tiff?$/) != null

export default function ScanPage() {
  const [file, setFile]           = useState<File | null>(null)
  const [preview, setPreview]     = useState<string | null>(null)
  const [model, setModel]         = useState('best')
  const [loading, setLoading]     = useState(false)
  const [result, setResult]       = useState<PredictionResult | null>(null)
  const [error, setError]         = useState<string | null>(null)
  const [activeViz, setActiveViz] = useState<'noise' | 'fft'>('noise')
  const previewUrlRef             = useRef<string | null>(null)

  useEffect(() => {
    return () => { if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current) }
  }, [])

  // Build preview: images get object URL, TIFs get canvas render, PDFs get icon
  const buildPreview = useCallback((f: File) => {
    if (previewUrlRef.current) { URL.revokeObjectURL(previewUrlRef.current); previewUrlRef.current = null }

    if (isPDF(f)) {
      // PDFs show a file icon — no URL needed
      setPreview('pdf')
      return
    }

    if (isTIF(f)) {
      // Use FileReader for TIF files — blob URLs don't render in <img> for TIF
      const reader = new FileReader()
      reader.onload = (e) => {
        const result = e.target?.result
        if (typeof result === 'string') {
          setPreview(result)  // base64 data URL
        }
      }
      reader.readAsDataURL(f)
      return
    }

    // JPG/PNG — use object URL (fastest)
    const url = URL.createObjectURL(f)
    previewUrlRef.current = url
    setPreview(url)
  }, [])

  const onDrop = useCallback((accepted: File[]) => {
    const f = accepted[0]
    if (!f) return
    setFile(f)
    setResult(null)
    setError(null)
    buildPreview(f)
  }, [buildPreview])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*':       ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'],
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    maxSize: 150 * 1024 * 1024,  // 150 MB — 300 DPI TIFs can be 80+ MB
  })

  const clearFile = () => {
    if (previewUrlRef.current) { URL.revokeObjectURL(previewUrlRef.current); previewUrlRef.current = null }
    setFile(null); setPreview(null); setResult(null); setError(null)
  }

  const handlePredict = async () => {
    if (!file) return
    setLoading(true); setError(null)
    const form = new FormData()
    form.append('file', file)
    form.append('model', model)
    try {
      const res = await axios.post<PredictionResult>('/api/predict/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,  // 2 min — large TIFs take longer
      })
      setResult(res.data)
    } catch (e: any) {
      const detail = e?.response?.data?.detail
      setError(detail || e?.message || 'Prediction failed. Is the backend running on port 8000?')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    if (!result) return
    try {
      const res = await axios.post('/api/report/download/', {
        filename: result.meta.filename,
        predicted_scanner: result.prediction.predicted_scanner,
        confidence: result.prediction.confidence,
        all_probabilities: result.prediction.all_probabilities,
        model_used: result.prediction.model_used,
        processing_time_s: result.meta.processing_time_s,
        feature_stats: result.feature_stats,
        is_mock: result.prediction.is_mock,
        noise_map_b64: result.visualizations.noise_map,
        fft_map_b64: result.visualizations.fft_map,
      }, { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `tracefinder_report_${result.meta.filename.split('.')[0]}.html`
      document.body.appendChild(a); a.click(); document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch { alert('Report download failed.') }
  }

  const probData = result
    ? Object.entries(result.prediction.all_probabilities)
        .map(([k, v]) => ({ name: k.replace(/[_-]\d$/, '').slice(-14), full: k, value: Math.round(v * 1000) / 10 }))
        .sort((a, b) => b.value - a.value)
    : []

  const lbpData = result
    ? result.feature_stats.lbp_histogram.slice(0, 32).map((v, i) => ({ bin: i, value: Math.round(v * 10000) / 10000 }))
    : []

  const cc = result ? confColor(result.prediction.confidence) : '#6366f1'
  const fileSizeMB = file ? (file.size / 1024 / 1024).toFixed(1) : '0'

  return (
    <>
      <Head><title>Scan — TraceFinder</title></Head>
      <div className="pg">
        <Navbar />
        <main className="sc-main">
          <div className="sc-hdr">
            <h1 className="sc-h1">Scanner Identification</h1>
            <p className="sc-p">Upload a scanned image or PDF to identify its source scanner device.</p>
          </div>

          <div className="sc-grid">
            {/* ── LEFT ── */}
            <div className="sc-col">

              {/* Dropzone */}
              <div {...getRootProps()} className={`dz${isDragActive ? ' dz-on' : ''}`}>
                <input {...getInputProps()} />
                <div className="dz-ico"><Upload size={22} color="var(--accent)" /></div>
                <p className="dz-t">{isDragActive ? 'Drop it here!' : 'Drag & drop your scanned file'}</p>
                <p className="dz-h">JPG · PNG · TIFF (any DPI) · BMP · <strong>PDF</strong> · up to 150 MB</p>
              </div>

              {/* Preview area */}
              {file && (
                <div className="card pv-card">
                  <div className="pv-top">
                    <div className="pv-fn">
                      {isPDF(file) ? <FileText size={14} color="var(--accent)" /> : <File size={14} color="var(--accent)" />}
                      <span className="pv-name" title={file.name}>{file.name}</span>
                    </div>
                    <button className="ico-btn" onClick={clearFile} aria-label="Remove">
                      <X size={14} />
                    </button>
                  </div>

                  {/* Actual preview */}
                  <div className="pv-wrap">
                    {preview === 'pdf' ? (
                      /* PDF — show icon placeholder */
                      <div className="pv-pdf">
                        <FileText size={48} color="var(--accent)" />
                        <p className="pv-pdf-lbl">PDF Document</p>
                        <p className="pv-pdf-sub">{fileSizeMB} MB · Page 1 will be analysed</p>
                      </div>
                    ) : preview ? (
                      /* Image preview — works for JPG, PNG, and TIF (base64) */
                      <div className="pv-img-wrap">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={preview}
                          alt={`Preview: ${file.name}`}
                          className="pv-img"
                          onError={(e) => {
                            // If <img> can't render (e.g. raw TIF), show fallback
                            const t = e.currentTarget
                            t.style.display = 'none'
                            const fb = t.nextElementSibling as HTMLElement
                            if (fb) fb.style.display = 'flex'
                          }}
                        />
                        <div className="pv-fallback">
                          <File size={40} color="var(--accent)" />
                          <p>{file.name}</p>
                          <p className="pv-pdf-sub">{fileSizeMB} MB · {isTIF(file) ? 'TIFF Image' : 'Image file'}</p>
                        </div>
                        {loading && <div className="sc-line" />}
                      </div>
                    ) : (
                      <div className="pv-loading">Loading preview…</div>
                    )}
                  </div>

                  <div className="pv-info">
                    <span>{fileSizeMB} MB</span>
                    <span>{file.type || (isTIF(file) ? 'image/tiff' : isPDF(file) ? 'application/pdf' : 'image')}</span>
                    {isTIF(file) && <span className="pv-tag">TIFF</span>}
                    {isPDF(file) && <span className="pv-tag">PDF</span>}
                  </div>
                </div>
              )}

              {/* Model selector + predict */}
              <div className="card mdl-card">
                <p className="mdl-lbl">Model</p>
                <div className="mdl-row">
                  {(['best','svm','rf','et'] as const).map(m => (
                    <button key={m} onClick={() => setModel(m)} className={`mb${model===m?' mb-on':''}`}>
                      {m==='best'?'Best':m==='svm'?'SVM':m==='rf'?'Random Forest':'Extra Trees'}
                    </button>
                  ))}
                </div>
                <button className="btn-primary full-w" onClick={handlePredict} disabled={!file || loading}>
                  {loading
                    ? <><Loader size={15} className="spin-it" /> Analyzing…</>
                    : <><Scan size={15} /> Identify Scanner</>}
                </button>
                {loading && (
                  <p className="proc-hint">
                    {isTIF(file) ? 'Processing large TIFF file — this may take 10-30s…' : isPDF(file) ? 'Extracting PDF page and analysing…' : 'Extracting features…'}
                  </p>
                )}
              </div>

              {error && (
                <div className="err" role="alert">
                  <AlertTriangle size={14} color="#ef4444" style={{flexShrink:0,marginTop:2}} />
                  <span className="err-t">{error}</span>
                </div>
              )}
            </div>

            {/* ── RIGHT ── */}
            <div className="sc-col">
              {!result && !loading && (
                <div className="card emp">
                  <div className="emp-ico"><Cpu size={26} color="var(--text-muted)" /></div>
                  <p className="emp-t">Upload a file and click <strong>Identify Scanner</strong> to see results here.</p>
                  <p className="emp-sub">Supports: JPG · PNG · TIFF (150/300 DPI) · BMP · PDF</p>
                </div>
              )}

              {loading && (
                <div className="card emp">
                  <div className="sp-w">
                    <div className="sp-r" />
                    <div className="sp-i" />
                  </div>
                  <p className="sp-l">Extracting features…</p>
                  <p className="sp-s">PRNU · FFT · LBP · Wavelet · GLCM</p>
                </div>
              )}

              {result && (
                <>
                  {result.prediction.is_mock && (
                    <div className="mock">
                      <AlertTriangle size={12} />
                      Mock model active — run <code>python train.py</code> for real predictions.
                    </div>
                  )}

                  {/* Result card */}
                  <div className="res">
                    <div className="res-t">
                      <div>
                        <p className="res-ey">IDENTIFIED SCANNER</p>
                        <p className="res-nm">{result.prediction.predicted_scanner}</p>
                        <span className="badge" style={{background:`${cc}20`,color:cc,border:`1px solid ${cc}40`}}>
                          <CheckCircle size={10} />&nbsp;{confLabel(result.prediction.confidence)} confidence
                        </span>
                      </div>
                      <div className="res-r">
                        <span className="res-pc" style={{color:cc}}>{Math.round(result.prediction.confidence*100)}%</span>
                        <span className="res-mt">{result.meta.processing_time_s}s · {result.prediction.model_used.toUpperCase()}</span>
                      </div>
                    </div>
                    <div className="c-trk"><div className="conf-bar-fill" style={{width:`${result.prediction.confidence*100}%`}} /></div>
                  </div>

                  {/* Probabilities */}
                  <div className="card ch">
                    <p className="ch-t">All Scanner Probabilities</p>
                    <ResponsiveContainer width="100%" height={210}>
                      <BarChart data={probData} layout="vertical" margin={{left:0,right:8}}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false}/>
                        <XAxis type="number" domain={[0,100]} tick={{fill:'var(--text-muted)',fontSize:11}} tickFormatter={v=>`${v}%`}/>
                        <YAxis type="category" dataKey="name" tick={{fill:'var(--text-muted)',fontSize:11}} width={88}/>
                        <Tooltip formatter={(v:number)=>[`${v}%`,'Probability']} labelFormatter={(_,i)=>i?.[0]?.payload?.full||_} contentStyle={{background:'var(--bg-card)',border:'1px solid var(--border)',borderRadius:8,fontSize:12}}/>
                        <Bar dataKey="value" radius={[0,4,4,0]}>
                          {probData.map((e,i)=><Cell key={i} fill={e.full===result.prediction.predicted_scanner?'#6366f1':'rgba(99,102,241,0.25)'}/>)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Visualizations */}
                  <div className="card ch">
                    <div className="vh">
                      <div className="vhl"><Eye size={13} color="var(--accent)"/><span className="ch-t" style={{margin:0}}>Feature Visualization</span></div>
                      <div className="vtbs">
                        {(['noise','fft'] as const).map(v=>(
                          <button key={v} onClick={()=>setActiveViz(v)} className={`vt${activeViz===v?' vt-on':''}`}>
                            {v==='noise'?'PRNU Noise':'FFT Spectrum'}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div className="vi-w">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={`data:image/png;base64,${activeViz==='noise'?result.visualizations.noise_map:result.visualizations.fft_map}`} alt={activeViz==='noise'?'PRNU Noise Map':'FFT Spectrum'} className="vi-img"/>
                    </div>
                    <p className="vi-c">
                      {activeViz==='noise'?'PRNU noise map — sensor non-uniformity fingerprint unique to each scanner model.':'FFT spectrum — periodic frequency artifacts introduced by scanner optics and CCD sensor.'}
                    </p>
                  </div>

                  {/* LBP */}
                  <div className="card ch">
                    <p className="ch-t">LBP Texture Histogram (32 bins)</p>
                    <ResponsiveContainer width="100%" height={100}>
                      <BarChart data={lbpData} margin={{top:0,right:0,left:-30,bottom:0}}>
                        <Bar dataKey="value" fill="#8b5cf6" radius={[2,2,0,0]}/>
                        <XAxis dataKey="bin" tick={{fill:'var(--text-muted)',fontSize:10}}/>
                        <YAxis tick={{fill:'var(--text-muted)',fontSize:10}}/>
                        <Tooltip contentStyle={{background:'var(--bg-card)',border:'1px solid var(--border)',borderRadius:8,fontSize:11}} formatter={(v:number)=>[v.toFixed(5),'Freq']}/>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* PRNU stats */}
                  <div className="card ch">
                    <p className="ch-t">PRNU Feature Statistics</p>
                    <div className="pg-g">
                      {Object.entries(result.feature_stats.prnu).map(([k,v])=>(
                        <div key={k} className="pg-i">
                          <span className="pg-k">{k}</span>
                          <span className="pg-v">{typeof v==='number'?v.toFixed(5):v}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <button className="btn-primary dl" onClick={handleDownload}>
                    <Download size={15}/>&nbsp;Download Forensic Report
                  </button>
                </>
              )}
            </div>
          </div>
        </main>
      </div>

      <style jsx>{`
        .pg{min-height:100vh;background:var(--bg-primary)}
        .sc-main{max-width:1200px;margin:0 auto;padding:36px 24px 80px}
        .sc-hdr{margin-bottom:28px}
        .sc-h1{font-family:var(--font-display);font-size:30px;font-weight:800;letter-spacing:-1px;color:var(--text-primary);margin:0 0 6px}
        .sc-p{color:var(--text-secondary);font-size:14px;margin:0}
        .sc-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
        .sc-col{display:flex;flex-direction:column;gap:14px}

        /* Dropzone */
        .dz{padding:28px 24px;cursor:pointer;text-align:center;border-radius:14px;min-height:160px;display:flex;flex-direction:column;align-items:center;justify-content:center;border:1.5px dashed rgba(99,102,241,0.3);background:var(--bg-card);transition:all .2s}
        .dz:hover,.dz-on{border-color:var(--accent);background:rgba(99,102,241,0.04)}
        .dz-ico{width:52px;height:52px;border-radius:12px;background:rgba(99,102,241,0.12);display:flex;align-items:center;justify-content:center;margin-bottom:14px}
        .dz-t{font-weight:600;font-size:14px;color:var(--text-primary);margin:0 0 5px}
        .dz-h{font-size:12px;color:var(--text-muted);margin:0}

        /* Preview */
        .pv-card{padding:14px}
        .pv-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
        .pv-fn{display:flex;align-items:center;gap:7px;min-width:0}
        .pv-name{font-size:12px;font-weight:600;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px}
        .ico-btn{background:none;border:none;cursor:pointer;color:var(--text-muted);padding:3px;display:flex;align-items:center;border-radius:4px}
        .ico-btn:hover{color:var(--text-primary);background:rgba(255,255,255,0.06)}

        .pv-wrap{border-radius:8px;overflow:hidden;background:#000;min-height:120px}
        .pv-img-wrap{position:relative}
        .pv-img{width:100%;max-height:260px;object-fit:contain;display:block}
        .pv-fallback{display:none;flex-direction:column;align-items:center;justify-content:center;padding:32px;gap:10px;color:var(--text-secondary);font-size:13px;text-align:center}
        .pv-pdf{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:32px;gap:10px;background:rgba(99,102,241,0.05)}
        .pv-pdf-lbl{font-weight:600;font-size:14px;color:var(--text-primary);margin:0}
        .pv-pdf-sub{font-size:12px;color:var(--text-muted);margin:0}
        .pv-loading{padding:32px;text-align:center;font-size:13px;color:var(--text-muted)}
        .sc-line{position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--accent),transparent);animation:scanLine 2s ease-in-out infinite}
        @keyframes scanLine{0%{transform:translateY(0)}100%{transform:translateY(260px)}}

        .pv-info{margin-top:8px;display:flex;gap:12px;font-size:11px;color:var(--text-muted);align-items:center}
        .pv-tag{background:rgba(99,102,241,0.15);color:var(--accent-light);border:1px solid rgba(99,102,241,0.3);border-radius:4px;padding:1px 6px;font-size:10px;font-weight:600}

        /* Model */
        .mdl-card{padding:18px}
        .mdl-lbl{font-size:12px;font-weight:600;color:var(--text-secondary);margin:0 0 8px}
        .mdl-row{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
        .mb{padding:5px 12px;border-radius:7px;font-size:12px;font-weight:500;cursor:pointer;border:1px solid var(--border);background:transparent;color:var(--text-secondary);transition:all .15s}
        .mb:hover{border-color:var(--border-hover);color:var(--text-primary)}
        .mb-on{border-color:var(--accent);background:rgba(99,102,241,0.15);color:var(--accent-light)}
        .full-w{width:100%;justify-content:center;padding:11px}
        .proc-hint{font-size:12px;color:var(--text-muted);margin:8px 0 0;text-align:center}

        .err{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);border-radius:10px;padding:12px 16px;display:flex;align-items:flex-start;gap:9px}
        .err-t{font-size:13px;color:#fca5a5;line-height:1.5}

        /* Empty / loading states */
        .emp{padding:44px 24px;text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:260px;gap:14px}
        .emp-ico{width:64px;height:64px;border-radius:50%;background:rgba(99,102,241,0.08);border:1px solid var(--border);display:flex;align-items:center;justify-content:center}
        .emp-t{color:var(--text-muted);font-size:14px;margin:0}
        .emp-sub{color:var(--text-muted);font-size:12px;margin:0}

        .sp-w{position:relative;width:72px;height:72px}
        .sp-r{position:absolute;inset:0;border-radius:50%;border:2px solid var(--accent);opacity:.25}
        .sp-i{position:absolute;inset:8px;border-radius:50%;border:2px solid var(--accent);border-top-color:transparent;animation:spin 1s linear infinite}
        .sp-l{font-weight:600;color:var(--text-primary);margin:0}
        .sp-s{font-size:12px;color:var(--text-muted);margin:0}
        @keyframes spin{to{transform:rotate(360deg)}}
        .spin-it{animation:spin 1s linear infinite}

        .mock{background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);border-radius:9px;padding:9px 14px;font-size:12px;color:#fcd34d;display:flex;gap:7px;align-items:center}
        .mock code{background:rgba(0,0,0,0.3);padding:1px 5px;border-radius:3px}

        /* Result */
        .res{background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.15));border:1px solid rgba(99,102,241,0.3);border-radius:14px;padding:20px 24px}
        .res-t{display:flex;align-items:flex-start;justify-content:space-between}
        .res-ey{font-size:11px;color:var(--accent-light);font-weight:600;letter-spacing:.08em;margin:0 0 5px}
        .res-nm{font-family:var(--font-display);font-size:18px;font-weight:700;color:var(--text-primary);margin:0 0 10px;line-height:1.2}
        .res-r{text-align:right}
        .res-pc{display:block;font-family:var(--font-display);font-size:32px;font-weight:800;line-height:1}
        .res-mt{font-size:11px;color:var(--text-muted);margin-top:3px;display:block}
        .c-trk{margin-top:14px;height:5px;background:rgba(255,255,255,0.08);border-radius:3px;overflow:hidden}

        /* Charts */
        .ch{padding:18px 20px}
        .ch-t{font-size:12px;font-weight:600;color:var(--text-secondary);margin:0 0 12px}
        .vh{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
        .vhl{display:flex;align-items:center;gap:7px}
        .vtbs{display:flex;gap:5px}
        .vt{padding:3px 10px;border-radius:5px;font-size:11px;font-weight:500;cursor:pointer;border:1px solid var(--border);background:transparent;color:var(--text-muted);transition:all .15s}
        .vt:hover{border-color:var(--border-hover)}
        .vt-on{border-color:var(--accent);background:rgba(99,102,241,0.15);color:var(--accent-light)}
        .vi-w{border-radius:8px;overflow:hidden;background:#000}
        .vi-img{width:100%;display:block;max-height:200px;object-fit:contain}
        .vi-c{font-size:11px;color:var(--text-muted);margin:7px 0 0;line-height:1.5}

        .pg-g{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}
        .pg-i{background:var(--bg-secondary);border-radius:7px;padding:9px 10px}
        .pg-k{display:block;font-size:10px;color:var(--text-muted);margin-bottom:3px;text-transform:capitalize}
        .pg-v{display:block;font-size:12px;font-weight:600;color:var(--text-primary);font-family:var(--font-mono)}

        .dl{width:100%;justify-content:center;padding:11px;background:#7c3aed}
        .dl:hover{background:#6d28d9}

        @media(max-width:768px){.sc-grid{grid-template-columns:1fr}}
      `}</style>
    </>
  )
}
