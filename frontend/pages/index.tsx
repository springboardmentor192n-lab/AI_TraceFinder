import Head from 'next/head'
import Link from 'next/link'
import Navbar from '../components/Navbar'
import { Scan, Shield, Cpu, FileSearch, ArrowRight, Zap, Eye, Download } from 'lucide-react'

const features = [
  { icon: Cpu, title: 'No GPU Required', desc: 'CPU-friendly SVM + Random Forest pipeline. Runs on any laptop.', color: '#6366f1' },
  { icon: Zap, title: 'Fast Inference', desc: 'Feature extraction in under 2 seconds. Instant scanner identification.', color: '#8b5cf6' },
  { icon: Eye, title: 'Visual Explainability', desc: 'PRNU noise maps and FFT spectra reveal scanner fingerprints.', color: '#a78bfa' },
  { icon: Shield, title: 'Forensic-Grade', desc: 'PRNU + LBP + FFT features used in academic scanner forensics research.', color: '#818cf8' },
  { icon: FileSearch, title: 'Supatlantique Dataset', desc: 'Trained on the Supatlantique scanner benchmark dataset from Kaggle.', color: '#6366f1' },
  { icon: Download, title: 'PDF Reports', desc: 'Download full forensic analysis reports with confidence scores.', color: '#7c3aed' },
]

const pipeline = [
  { step: '01', label: 'Upload', desc: 'Drag & drop scanned image (PNG, JPEG, TIFF)' },
  { step: '02', label: 'Preprocess', desc: 'Resize, grayscale, normalize to 256×256' },
  { step: '03', label: 'Features', desc: 'Extract PRNU noise, FFT spectrum, LBP texture' },
  { step: '04', label: 'Classify', desc: 'SVM + Random Forest predict scanner model' },
  { step: '05', label: 'Report', desc: 'Download full forensic PDF with visualizations' },
]

export default function Home() {
  return (
    <>
      <Head>
        <title>TraceFinder — Forensic Scanner Identification</title>
        <meta name="description" content="Identify the scanner device used to produce any scanned document using AI forensics." />
      </Head>
      <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
        <Navbar />

        {/* Hero */}
        <section style={{ maxWidth: 1200, margin: '0 auto', padding: '80px 24px 60px', textAlign: 'center' }}>
          {/* Badge */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)',
            borderRadius: 20, padding: '6px 16px', marginBottom: 32,
          }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e' }} />
            <span style={{ fontSize: 13, color: 'var(--accent-light)', fontWeight: 500 }}>
              Supatlantique Dataset · No GPU Required
            </span>
          </div>

          <h1 style={{
            fontFamily: 'var(--font-display)', fontSize: 'clamp(40px, 6vw, 72px)',
            fontWeight: 800, lineHeight: 1.05, letterSpacing: '-2px',
            color: 'var(--text-primary)', marginBottom: 24,
          }}>
            Find the Scanner
            <br />
            <span style={{
              background: 'linear-gradient(135deg, #6366f1 0%, #a78bfa 50%, #818cf8 100%)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            }}>
              Behind Every Scan
            </span>
          </h1>

          <p style={{
            fontSize: 18, color: 'var(--text-secondary)', maxWidth: 560,
            margin: '0 auto 40px', lineHeight: 1.7, fontWeight: 300,
          }}>
            Forensic scanner identification using PRNU noise patterns, FFT frequency analysis,
            and LBP texture descriptors. No GPU needed.
          </p>

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/scan" style={{ textDecoration: 'none' }}>
              <button className="btn-primary" style={{ fontSize: 15, padding: '12px 28px' }}>
                <Scan size={16} />
                Start Scanning
                <ArrowRight size={14} />
              </button>
            </Link>
            <Link href="/dashboard" style={{ textDecoration: 'none' }}>
              <button className="btn-ghost" style={{ fontSize: 15, padding: '12px 28px' }}>
                View Dashboard
              </button>
            </Link>
          </div>
        </section>

        {/* Pipeline steps */}
        <section style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px 80px' }}>
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)',
            gap: 0, position: 'relative',
          }}>
            {pipeline.map((item, i) => (
              <div key={i} style={{ padding: '24px 20px', position: 'relative' }}>
                {i < pipeline.length - 1 && (
                  <div style={{
                    position: 'absolute', top: 36, right: 0,
                    width: '50%', height: 1, background: 'var(--border)', zIndex: 0
                  }} />
                )}
                <div style={{
                  fontFamily: 'var(--font-display)', fontSize: 11, fontWeight: 700,
                  color: 'var(--accent)', letterSpacing: '0.1em', marginBottom: 8,
                }}>
                  {item.step}
                </div>
                <div style={{ fontWeight: 600, fontSize: 15, color: 'var(--text-primary)', marginBottom: 6 }}>
                  {item.label}
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                  {item.desc}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Features grid */}
        <section style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px 100px' }}>
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16
          }}>
            {features.map(({ icon: Icon, title, desc, color }, i) => (
              <div key={i} className="card" style={{ padding: '24px 28px' }}>
                <div style={{
                  width: 40, height: 40, borderRadius: 10,
                  background: `${color}18`, display: 'flex',
                  alignItems: 'center', justifyContent: 'center', marginBottom: 16,
                }}>
                  <Icon size={18} color={color} />
                </div>
                <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 8, color: 'var(--text-primary)' }}>
                  {title}
                </div>
                <div style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {desc}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Footer */}
        <footer style={{
          borderTop: '1px solid var(--border)', padding: '24px',
          textAlign: 'center', color: 'var(--text-muted)', fontSize: 13
        }}>
          TraceFinder · Forensic Scanner Identification · Built with Next.js + FastAPI + Scikit-learn
        </footer>
      </div>
    </>
  )
}
