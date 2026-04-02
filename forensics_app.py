import streamlit as st
import numpy as np
import cv2
import pywt
import pickle
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skimage.feature import local_binary_pattern as sk_lbp
from io import BytesIO
from PIL import Image
import tensorflow as tf

# patch outdated model configs that include quantization metadata
try:
    _dense_init = tf.keras.layers.Dense.__init__
    def _patched_dense_init(self, *args, **kwargs):
        kwargs.pop('quantization_config', None)
        return _dense_init(self, *args, **kwargs)
    tf.keras.layers.Dense.__init__ = _patched_dense_init
except Exception:
    pass

# PAGE CONFIG
st.set_page_config(
    page_title="SUPATLANTIQUE Forensics",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
    --bg:#0b0e14; --surface:#111520; --card:#161c2b; --border:#232b3e;
    --accent:#00d4ff; --accent2:#7b5cfa; --success:#00e5a0;
    --danger:#ff4560; --warning:#ffa726; --text:#e2e8f0; --muted:#64748b;
}
html,body,[class*='css']{ font-family:'DM Sans',sans-serif; background:var(--bg); color:var(--text); }
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1.5rem 2rem 3rem; max-width:1400px;}
.hero{background:linear-gradient(135deg,#0b0e14,#131829,#0b0e14);
  border:1px solid var(--border);border-radius:16px;padding:2.5rem 3rem;
  margin-bottom:2rem;position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 20% 50%,rgba(0,212,255,.07),transparent 60%),
             radial-gradient(ellipse at 80% 50%,rgba(123,92,250,.07),transparent 60%);pointer-events:none;}
.hero-badge{display:inline-block;font-family:'Space Mono',monospace;font-size:.68rem;color:var(--accent);
  border:1px solid var(--accent);border-radius:4px;padding:2px 8px;margin-bottom:1rem;letter-spacing:.1em;}
.hero-title{font-family:'Space Mono',monospace;font-size:1.85rem;font-weight:700;
  background:linear-gradient(90deg,var(--accent),var(--accent2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0 0 .4rem;}
.hero-sub{font-size:.9rem;color:var(--muted);margin:0;}
section[data-testid='stSidebar']{background:var(--surface) !important;border-right:1px solid var(--border);}
.sidebar-label{font-family:'Space Mono',monospace;font-size:.72rem;letter-spacing:.12em;
  color:var(--muted);text-transform:uppercase;border-bottom:1px solid var(--border);
  padding-bottom:.5rem;margin-bottom:.9rem;}
.metric-card{background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:1.2rem 1.4rem;margin-bottom:.8rem;position:relative;overflow:hidden;}
.metric-card::after{content:'';position:absolute;top:0;left:0;width:3px;height:100%;
  background:linear-gradient(180deg,var(--accent),var(--accent2));border-radius:3px 0 0 3px;}
.metric-label{font-family:'Space Mono',monospace;font-size:.65rem;letter-spacing:.1em;
  color:var(--muted);text-transform:uppercase;margin-bottom:.3rem;}
.metric-value{font-family:'Space Mono',monospace;font-size:1.55rem;font-weight:700;color:var(--accent);line-height:1;}
.metric-sub{font-size:.78rem;color:var(--muted);margin-top:.25rem;}
.result-banner{border-radius:12px;padding:1.3rem 1.7rem;margin:1rem 0;
  border:1px solid;display:flex;align-items:center;gap:1rem;}
.result-banner.clean{background:rgba(0,229,160,.08);border-color:var(--success);}
.result-banner.tampered{background:rgba(255,69,96,.08);border-color:var(--danger);}
.result-icon{font-size:1.9rem;}
.result-title{font-family:'Space Mono',monospace;font-size:.95rem;font-weight:700;margin:0;}
.result-detail{font-size:.8rem;color:var(--muted);margin:.2rem 0 0;}
.prog-wrap{margin:.4rem 0;}
.prog-label{display:flex;justify-content:space-between;font-size:.78rem;
  font-family:'Space Mono',monospace;margin-bottom:3px;}
.prog-track{background:var(--border);border-radius:99px;height:7px;overflow:hidden;}
.prog-fill{height:100%;border-radius:99px;}
.sec-hdr{font-family:'Space Mono',monospace;font-size:.7rem;letter-spacing:.14em;
  color:var(--muted);text-transform:uppercase;border-bottom:1px solid var(--border);
  padding-bottom:.4rem;margin:1.5rem 0 1rem;}
.rank-row{display:flex;align-items:center;gap:.9rem;padding:.62rem .9rem;border-radius:8px;
  margin-bottom:.32rem;background:var(--surface);border:1px solid var(--border);}
.rank-num{font-family:'Space Mono',monospace;font-size:.66rem;color:var(--muted);width:18px;}
.rank-name{font-family:'Space Mono',monospace;font-size:.8rem;color:var(--text);flex:1;}
.rank-score{font-family:'Space Mono',monospace;font-size:.8rem;color:var(--accent);}
.info-box{background:rgba(0,212,255,.06);border-left:3px solid var(--accent);
  border-radius:0 8px 8px 0;padding:.7rem 1rem;font-size:.82rem;margin:.7rem 0;}
.warn-box{background:rgba(255,167,38,.08);border-left:3px solid var(--warning);
  border-radius:0 8px 8px 0;padding:.7rem 1rem;font-size:.82rem;margin:.7rem 0;}
.stButton>button{background:linear-gradient(135deg,var(--accent),var(--accent2)) !important;
  color:#000 !important;font-family:'Space Mono',monospace !important;font-size:.78rem !important;
  font-weight:700 !important;border:none !important;border-radius:8px !important;padding:.52rem 1.4rem !important;}
.stTabs [data-baseweb='tab-list']{background:var(--card);border-radius:10px;
  padding:4px;gap:4px;border:1px solid var(--border);}
.stTabs [data-baseweb='tab']{font-family:'Space Mono',monospace !important;font-size:.74rem !important;
  border-radius:7px !important;color:var(--muted) !important;background:transparent !important;}
.stTabs [aria-selected='true']{background:var(--border) !important;color:var(--accent) !important;}
</style>
""", unsafe_allow_html=True)

# CONSTANTS
ART_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artifacts')
PATCH_DIR = f'{ART_DIR}/artifacts_tamper_patch'
IMG_SIZE  = (256, 256)
PSIZ      = 128
STRIDE    = 64
MAX_P     = 16

# FEATURE FUNCTIONS
def load_residual(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY) if img_bgr.ndim == 3 else img_bgr
    gray = cv2.resize(gray, IMG_SIZE, interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    cA, (cH, cV, cD) = pywt.dwt2(gray, 'haar')
    cH.fill(0); cV.fill(0); cD.fill(0)
    return (gray - pywt.idwt2((cA, (cH, cV, cD)), 'haar')).astype(np.float32)

def extract_patches(res):
    H, W = res.shape
    coords = [(y, x) for y in range(0, H-PSIZ+1, STRIDE) for x in range(0, W-PSIZ+1, STRIDE)]
    np.random.RandomState(42).shuffle(coords)
    return [res[y:y+PSIZ, x:x+PSIZ] for y, x in coords[:MAX_P]]

def corr2d(a, b):
    a = a.ravel().astype(np.float32); a -= a.mean()
    b = b.ravel().astype(np.float32); b -= b.mean()
    d = np.linalg.norm(a) * np.linalg.norm(b)
    return float((a @ b) / d) if d > 0 else 0.0

def fft_radial(img, K=6):
    mag = np.abs(np.fft.fftshift(np.fft.fft2(img)))
    h, w = mag.shape; cy, cx = h//2, w//2
    yy = np.arange(h).reshape(-1,1); xx = np.arange(w).reshape(1,-1)
    r = np.sqrt((yy-cy)**2 + (xx-cx)**2)
    bins = np.linspace(0, r.max()+1e-6, K+1)
    return np.array([float(mag[(r>=bins[i])&(r<bins[i+1])].mean()) for i in range(K)], dtype=np.float32)

def lbp_hist(img, P=8, R=1.0):
    rng = float(np.ptp(img))
    g = np.zeros_like(img, np.float32) if rng<1e-12 else (img-float(np.min(img)))/(rng+1e-8)
    codes = sk_lbp((g*255).astype(np.uint8), P=P, R=R, method='uniform')
    hist, _ = np.histogram(codes, bins=np.arange(P+3), density=True)
    return hist.astype(np.float32)

def res_stats(img):
    return np.array([img.mean(), img.std(), np.mean(np.abs(img))], dtype=np.float32)

def fft_resample(img):
    mag = np.abs(np.fft.fftshift(np.fft.fft2(img)))
    h, w = mag.shape; cy, cx = h//2, w//2
    yy = np.arange(h).reshape(-1,1); xx = np.arange(w).reshape(1,-1)
    r = np.sqrt((yy-cy)**2+(xx-cx)**2); rmax = r.max()+1e-6
    e1 = float(mag[(r>=.25*rmax)&(r<.35*rmax)].mean())
    e2 = float(mag[(r>=.35*rmax)&(r<.50*rmax)].mean())
    return np.array([e1, e2, e2/(e1+1e-8)], dtype=np.float32)

def patch_feat(p):
    return np.concatenate([lbp_hist(p,8,1.0), fft_radial(p,6), res_stats(p), fft_resample(p)])

def scanner_feats(res, fps, fp_keys, scaler):
    v = np.array([corr2d(res, fps[k]) for k in fp_keys]
                 + fft_radial(res,6).tolist() + lbp_hist(res,8,1.0).tolist(),
                 dtype=np.float32).reshape(1,-1)
    return scaler.transform(v)

@st.cache_resource(show_spinner=False)
def load_arts():
    required = {
        'model' : f'{ART_DIR}/scanner_hybrid.keras',
        'le'    : f'{ART_DIR}/hybrid_label_encoder.pkl',
        'scaler': f'{ART_DIR}/hybrid_feat_scaler.pkl',
        'fps'   : f'{ART_DIR}/scanner_fingerprints.pkl',
        'fpk'   : f'{ART_DIR}/fp_keys.npy',
    }
    optional = {
        'psvm'  : f'{PATCH_DIR}/patch_svm_sig_calibrated.pkl',
        'psc'   : f'{PATCH_DIR}/patch_scaler.pkl',
        'pthr'  : f'{PATCH_DIR}/thresholds_patch.json',
    }
    missing_required = [k for k,p in required.items() if not os.path.exists(p)]
    if missing_required:
        return None, missing_required

    arts = {
        'model' : tf.keras.models.load_model(required['model']),
        'le'    : pickle.load(open(required['le'],'rb')),
        'scaler': pickle.load(open(required['scaler'],'rb')),
        'fps'   : pickle.load(open(required['fps'],'rb')),
        'fp_keys': np.load(required['fpk'], allow_pickle=True).tolist(),
        'patch_support': False,
    }

    missing_optional = [k for k,p in optional.items() if not os.path.exists(p)]
    if not missing_optional:
        arts['psvm'] = pickle.load(open(optional['psvm'],'rb'))
        arts['psc']  = pickle.load(open(optional['psc'],'rb'))
        arts['pthr'] = json.load(open(optional['pthr']))
        arts['patch_support'] = True
    else:
        arts['psvm'] = None
        arts['psc'] = None
        arts['pthr'] = None

    return arts, missing_optional

def run_inference(img_bgr, arts):
    res   = load_residual(img_bgr)
    x_img = np.expand_dims(res, axis=(0,-1)).astype(np.float32)
    x_ft  = scanner_feats(res, arts['fps'], arts['fp_keys'], arts['scaler'])
    probs = arts['model'].predict([x_img, x_ft], verbose=0).ravel()
    top3  = [(arts['le'].classes_[i], float(probs[i])*100) for i in np.argsort(probs)[::-1][:3]]
    patches = extract_patches(res)
    if patches and arts.get('patch_support', False):
        pf    = np.array([patch_feat(p) for p in patches], dtype=np.float32)
        pp    = arts['psvm'].predict_proba(arts['psc'].transform(pf))[:,1]
        k     = max(1, int(len(pp)*.30))
        score = float(np.mean(np.sort(pp)[::-1][:k]))
        thr   = arts['pthr'].get('overall', arts['pthr'].get('default', 0.5))
        tampered = score >= thr
    else:
        pp, score, thr, tampered = np.array([]), 0.0, 0.0, False
    return {'top3':top3,'res':res,'pp':pp,'score':score,'thr':thr,'tampered':tampered,'patch_support': arts.get('patch_support', False)}

def mc(label, val, sub=''):
    s = f'<div class="metric-sub">{sub}</div>' if sub else ''
    return f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div>{s}</div>'

def prog(label, val, color='var(--accent)'):
    return (f'<div class="prog-wrap"><div class="prog-label"><span>{label}</span><span>{val:.1f}%</span></div>'
            f'<div class="prog-track"><div class="prog-fill" style="width:{min(val,100):.1f}%;background:{color};"></div></div></div>')

def banner(tampered, score, thr, patch_support=True):
    if not patch_support:
        return ('<div class="result-banner clean"><div class="result-icon">ℹ️</div>'
                '<div><p class="result-title">Scanner-only analysis</p>'
                '<p class="result-detail">Patch-level forgery detection unavailable.</p></div></div>')
    cls   = 'tampered' if tampered else 'clean'
    icon  = '🚨' if tampered else '✅'
    title = 'FORGERY DETECTED' if tampered else 'DOCUMENT APPEARS AUTHENTIC'
    word  = 'exceeds' if tampered else 'is below'
    detail = f'Tamper probability {score:.1%} {word} threshold {thr:.1%}'
    return (f'<div class="result-banner {cls}"><div class="result-icon">{icon}</div>'
            f'<div><p class="result-title">{title}</p><p class="result-detail">{detail}</p></div></div>')

def top3_html(top3):
    colors = ['var(--accent)','var(--accent2)','var(--muted)']
    ranks  = ['#1','#2','#3']
    return ''.join(
        f'<div class="rank-row"><span class="rank-num">{ranks[i]}</span>'
        f'<span class="rank-name">{n}</span>'
        f'<span class="rank-score" style="color:{colors[i]}">{s:.1f}%</span></div>'
        for i,(n,s) in enumerate(top3))

def heatmap_fig(res):
    fig, axes = plt.subplots(1, 3, figsize=(13,3.5), facecolor='#0b0e14')
    for ax in axes: ax.set_facecolor('#0b0e14')
    axes[0].imshow(res, cmap='RdBu_r', aspect='auto')
    axes[0].set_title('Noise Residual', color='#e2e8f0', fontsize=9, pad=6); axes[0].axis('off')
    enh = np.clip((res-res.mean())/(res.std()+1e-8)*.5+.5, 0, 1)
    axes[1].imshow(enh, cmap='inferno', aspect='auto')
    axes[1].set_title('Enhanced', color='#e2e8f0', fontsize=9, pad=6); axes[1].axis('off')
    fmag = np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(res))))
    axes[2].imshow(fmag, cmap='plasma', aspect='auto')
    axes[2].set_title('FFT Spectrum', color='#e2e8f0', fontsize=9, pad=6); axes[2].axis('off')
    plt.tight_layout(pad=0.8)
    buf = BytesIO(); plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='#0b0e14')
    plt.close(fig); buf.seek(0); return buf

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="sidebar-label">⚙ Artifact Status</div>', unsafe_allow_html=True)
    checks = {
        'scanner_hybrid.keras'          : f'{ART_DIR}/scanner_hybrid.keras',
        'hybrid_label_encoder.pkl'      : f'{ART_DIR}/hybrid_label_encoder.pkl',
        'hybrid_feat_scaler.pkl'        : f'{ART_DIR}/hybrid_feat_scaler.pkl',
        'scanner_fingerprints.pkl'      : f'{ART_DIR}/scanner_fingerprints.pkl',
        'fp_keys.npy'                   : f'{ART_DIR}/fp_keys.npy',
        'patch_svm_sig_calibrated.pkl'  : f'{PATCH_DIR}/patch_svm_sig_calibrated.pkl',
        'patch_scaler.pkl'              : f'{PATCH_DIR}/patch_scaler.pkl',
        'thresholds_patch.json'         : f'{PATCH_DIR}/thresholds_patch.json',
    }
    for fname, fpath in checks.items():
        icon = '🟢' if os.path.exists(fpath) else '🔴'
        st.markdown(f'`{icon} {fname}`')
    st.markdown('---')
    st.markdown('''<small style="color:#64748b;font-size:.78rem;line-height:1.7">
<b style="color:#e2e8f0">SUPATLANTIQUE</b><br>
Obj 1 → Scanner Source ID<br>
Obj 2 → Forgery Detection<br>
11 scanners · Hybrid CNN + SVM</small>''', unsafe_allow_html=True)

# HERO
st.markdown('''<div class="hero">
  <div class="hero-badge">DOCUMENT FORENSICS · COLAB EDITION</div>
  <h1 class="hero-title">🔬 SUPATLANTIQUE Forensics</h1>
  <p class="hero-sub">Scanner Source Identification &amp; Forgery Detection — Upload a scanned document to identify its scanner and detect tampering.</p>
</div>''', unsafe_allow_html=True)

with st.spinner('Loading model artifacts from Google Drive...'):
    arts, missing = load_arts()

if arts is None:
    st.markdown(f'<div class="warn-box">⚠️ <b>Missing required artifacts:</b> {", ".join(missing)}<br>'
                'Copy the required files into the artifacts folder and restart.</div>', unsafe_allow_html=True)
else:
    if missing:
        st.markdown('<div class="warn-box">⚠️ Patch artifact files are missing. Scanner-only analysis is enabled.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">✓ All artifacts loaded. Ready for inference.</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(['  🔍  Single Image Analysis  ', '  📦  Batch Analysis  '])

# TAB 1 — SINGLE IMAGE
with tab1:
    st.markdown('<div class="sec-hdr">Upload Document Image</div>', unsafe_allow_html=True)
    up = st.file_uploader('Drop a scanned document (TIF, PNG, JPG)',
                           type=['tif','tiff','png','jpg','jpeg'],
                           label_visibility='collapsed')

    if up and arts:
        pil_img = Image.open(up)
        bgr = cv2.cvtColor(np.array(pil_img.convert('RGB')), cv2.COLOR_RGB2BGR)
        with st.spinner('🔬 Running forensic analysis...'):
            r = run_inference(bgr, arts)

        c1, c2 = st.columns([1, 1.6], gap='large')
        with c1:
            st.markdown('<div class="sec-hdr">Input Image</div>', unsafe_allow_html=True)
            st.image(pil_img, use_container_width=True, caption=up.name)
        with c2:
            st.markdown('<div class="sec-hdr">Results</div>', unsafe_allow_html=True)
            st.markdown(banner(r['tampered'], r['score'], r['thr'], r.get('patch_support', False)), unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            with m1: st.markdown(mc('Scanner Identified', r['top3'][0][0], f"{r['top3'][0][1]:.1f}% confidence"), unsafe_allow_html=True)
            with m2: st.markdown(mc('Forgery Score', f"{r['score']:.3f}", f"Threshold: {r['thr']:.3f}"), unsafe_allow_html=True)
            st.markdown('<div class="sec-hdr">Top-3 Scanner Candidates</div>', unsafe_allow_html=True)
            st.markdown(top3_html(r['top3']), unsafe_allow_html=True)
            bar_c = ['var(--accent)','var(--accent2)','var(--muted)']
            for i,(n,s) in enumerate(r['top3']):
                st.markdown(prog(n, s, bar_c[i]), unsafe_allow_html=True)
            st.markdown('<div class="sec-hdr">Forgery Probability</div>', unsafe_allow_html=True)
            dc = 'var(--danger)' if r['tampered'] else 'var(--success)'
            st.markdown(prog('Tamper probability', r['score']*100, dc), unsafe_allow_html=True)
            if len(r['pp']) > 0:
                fig2, ax2 = plt.subplots(figsize=(5,1.6), facecolor='#161c2b'); ax2.set_facecolor('#161c2b')
                ax2.bar(range(len(r['pp'])), r['pp'],
                        color=['#ff4560' if p>=r['thr'] else '#00d4ff' for p in r['pp']],
                        width=0.7, edgecolor='none')
                ax2.axhline(r['thr'], color='#ffa726', lw=1.2, ls='--', label=f"Thr {r['thr']:.2f}")
                ax2.set_xlabel('Patch', color='#64748b', fontsize=7)
                ax2.set_ylabel('P(tamper)', color='#64748b', fontsize=7)
                ax2.tick_params(colors='#64748b', labelsize=6)
                for sp in ax2.spines.values(): sp.set_edgecolor('#232b3e')
                ax2.legend(fontsize=7, facecolor='#161c2b', edgecolor='#232b3e', labelcolor='#e2e8f0')
                plt.tight_layout(pad=0.6)
                st.pyplot(fig2, use_container_width=True); plt.close(fig2)

        st.markdown('<div class="sec-hdr">Noise Residual Analysis</div>', unsafe_allow_html=True)
        st.image(heatmap_fig(r['res']), use_container_width=True,
                 caption='Left: Raw residual (RdBu) · Center: Enhanced (Inferno) · Right: FFT Spectrum (Plasma)')

    elif up and not arts:
        st.markdown('<div class="warn-box">⚠️ Model artifacts not loaded. Check sidebar.</div>', unsafe_allow_html=True)
    else:
        st.markdown('''<div style="text-align:center;padding:3rem 1rem;color:#64748b;">
  <div style="font-size:3rem;margin-bottom:1rem">📂</div>
  <div style="font-family:Space Mono,monospace;font-size:.82rem">Upload a scanned document to begin analysis</div>
</div>''', unsafe_allow_html=True)

# TAB 2 — BATCH
with tab2:
    st.markdown('<div class="sec-hdr">Batch Upload</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Upload multiple images — get a summary table with expandable per-image detail cards.</div>', unsafe_allow_html=True)
    bups = st.file_uploader('Drop multiple images', type=['tif','tiff','png','jpg','jpeg'],
                             accept_multiple_files=True, label_visibility='collapsed', key='batch')

    if bups and arts:
        if st.button('▶  Run Batch Analysis'):
            results = []
            pb = st.progress(0, 'Analysing...')
            for i, f in enumerate(bups):
                try:
                    pil = Image.open(f)
                    bgr = cv2.cvtColor(np.array(pil.convert('RGB')), cv2.COLOR_RGB2BGR)
                    r = run_inference(bgr, arts)
                    results.append({'file':f.name,'pil':pil,'result':r,'ok':True})
                except Exception as e:
                    results.append({'file':f.name,'pil':None,'result':None,'ok':False,'err':str(e)})
                pb.progress((i+1)/len(bups), f'Analysed {i+1}/{len(bups)}: {f.name}')
            pb.empty()

            import pandas as pd
            st.markdown('<div class="sec-hdr">Summary Table</div>', unsafe_allow_html=True)
            rows = []
            for x in results:
                if x['ok']:
                    r = x['result']
                    rows.append({'File':x['file'],'Scanner':r['top3'][0][0],
                                 'Conf (%)':f"{r['top3'][0][1]:.1f}",'2nd':r['top3'][1][0],
                                 'Tamper Score':f"{r['score']:.3f}",'Threshold':f"{r['thr']:.3f}",
                                 'Verdict':'🚨 TAMPERED' if r['tampered'] else '✅ CLEAN'})
                else:
                    rows.append({'File':x['file'],'Scanner':'ERROR','Conf (%)':'—','2nd':'—',
                                 'Tamper Score':'—','Threshold':'—','Verdict':f"❌ {x['err'][:35]}"})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            ok_r   = [x for x in results if x['ok']]
            n_t    = sum(1 for x in ok_r if x['result']['tampered'])
            scs    = [x['result']['top3'][0][0] for x in ok_r]
            top_sc = max(set(scs), key=scs.count) if scs else '—'
            s1, s2, s3, s4 = st.columns(4)
            with s1: st.markdown(mc('Total Images', str(len(results))), unsafe_allow_html=True)
            with s2: st.markdown(mc('Clean', str(len(ok_r)-n_t), 'passed check'), unsafe_allow_html=True)
            with s3: st.markdown(mc('Tampered', str(n_t), 'forgery detected'), unsafe_allow_html=True)
            with s4: st.markdown(mc('Top Scanner', top_sc), unsafe_allow_html=True)

            st.markdown('<div class="sec-hdr">Per-Image Details</div>', unsafe_allow_html=True)
            for x in results:
                icon = '🚨' if (x['ok'] and x['result']['tampered']) else ('❌' if not x['ok'] else '✅')
                with st.expander(f'{icon}  {x["file"]}', expanded=False):
                    if x['ok']:
                        r = x['result']
                        ca, cb, cc = st.columns([1, 1.2, 1.4])
                        with ca: st.image(x['pil'], use_container_width=True)
                        with cb:
                            st.markdown(mc('Scanner', r['top3'][0][0], f"{r['top3'][0][1]:.1f}%"), unsafe_allow_html=True)
                            st.markdown(mc('Tamper Score', f"{r['score']:.3f}", f"Thr: {r['thr']:.3f}"), unsafe_allow_html=True)
                            st.markdown(banner(r['tampered'], r['score'], r['thr'], r.get('patch_support', False)), unsafe_allow_html=True)
                        with cc:
                            st.image(heatmap_fig(r['res']), use_container_width=True, caption='Noise residuals')
                    else:
                        st.error(f"Error: {x['err']}")
    elif not arts:
        st.markdown('<div class="warn-box">⚠️ Model artifacts not loaded. Check sidebar.</div>', unsafe_allow_html=True)
    else:
        st.markdown('''<div style="text-align:center;padding:3rem 1rem;color:#64748b;">
  <div style="font-size:3rem;margin-bottom:1rem">📦</div>
  <div style="font-family:Space Mono,monospace;font-size:.82rem">Upload multiple images for batch analysis</div>
</div>''', unsafe_allow_html=True)
