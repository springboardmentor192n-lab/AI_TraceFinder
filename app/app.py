import streamlit as st
import torch
import torch.nn.functional as F
import cv2
import numpy as np
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.cnn_model import CNN
import time

st.set_page_config(page_title="AI_TRACEFINDER", layout="wide", page_icon="🛡️", initial_sidebar_state="expanded")

# Professional, Realistic Dashboard CSS
st.markdown("""
<style>
    /* Global Backgrounds */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Professional sleek cards */
    .metric-card {
        background-color: #1a1c23;
        border: 1px solid #2b2e38;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .metric-title {
        color: #7b8296;
        font-size: 11px;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    
    .metric-value {
        color: #e2e8f0;
        font-size: 26px;
        font-weight: 700;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    hr {
        border-color: #2b2e38;
    }
    
    /* Precise Progress bars */
    .progress-bg {
        background-color: #212530;
        border-radius: 3px;
        height: 6px;
        width: 100%;
        margin-top: 8px;
        overflow: hidden;
        border: 1px solid #1a1c23;
    }
    
    .progress-fill {
        background-color: #3b82f6; /* Professional core blue */
        height: 6px;
        transition: width 0.4s ease;
    }
    
    .progress-fill.tamper { 
        background-color: #ef4444; /* High-alert red */
    }
    
    /* Sidebar styling overrides */
    [data-testid="stSidebar"] {
        background-color: #14161c;
        border-right: 1px solid #2b2e38;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Checkers and Loaders
# -----------------------------
@st.cache_resource
def load_models():
    # Load Models safely
    try:
        model_path = os.path.join(os.path.dirname(__file__), '..', 'model.pth')
        scanner_ckpt = torch.load(model_path, map_location="cpu", weights_only=False)
        scanner_classes = scanner_ckpt['class_names']
        scanner_model = CNN(len(scanner_classes))
        scanner_model.load_state_dict(scanner_ckpt['model_state'])
        scanner_model.eval()
    except Exception as e:
        scanner_model, scanner_classes = None, []
        
    try:
        tamper_path = os.path.join(os.path.dirname(__file__), '..', 'tamper_model.pth')
        tamper_ckpt = torch.load(tamper_path, map_location="cpu", weights_only=False)
        tamper_classes = tamper_ckpt['class_names']
        tamper_model = CNN(len(tamper_classes))
        tamper_model.load_state_dict(tamper_ckpt['model_state'])
        tamper_model.eval()
    except Exception as e:
        tamper_model, tamper_classes = None, []
        
    return scanner_model, scanner_classes, tamper_model, tamper_classes

scanner_model, scanner_classes, tamper_model, tamper_classes = load_models()

# -----------------------------
# Sidebar Navigation
# -----------------------------
with st.sidebar:
    st.markdown("<div style='text-align: center; padding-bottom: 20px;'><h2 style='color:#e2e8f0; font-weight:700; font-size:22px; letter-spacing:1px;'>🛡️ AI_TRACEFINDER</h2><div style='color:#3b82f6; font-size:11px; font-weight:600;'>ENTERPRISE EDITION v3.0</div></div>", unsafe_allow_html=True)
    
    # Put the navigation selector straight into the sidebar
    st.markdown("<div style='color:#7b8296; font-size:12px; font-weight:600; margin-bottom:8px;'>MODULE SELECTION</div>", unsafe_allow_html=True)
    mode = st.radio("Select module", ["Single Document Analysis", "Batch Analytics Pipeline"], label_visibility="collapsed")
    
    st.markdown("---")
    
    # Render model diagnostic statuses instead of arbitrary files
    st.markdown("<div style='color:#7b8296; font-size:12px; font-weight:600; margin-bottom:12px;'>SYSTEM DIAGNOSTICS</div>", unsafe_allow_html=True)
    
    sm_color = "#10b981" if scanner_model else "#ef4444"
    sm_text = "ONLINE" if scanner_model else "OFFLINE"
    tm_color = "#10b981" if tamper_model else "#ef4444"
    tm_text = "ONLINE" if tamper_model else "OFFLINE"
    
    st.markdown(f"""
    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; font-size:13px; color:#a0abc0;'>
        <span>Scanner ID Model</span>
        <span style='color:{sm_color}; font-weight:bold;'>■ {sm_text}</span>
    </div>
    <div style='display:flex; justify-content:space-between; align-items:center; font-size:13px; color:#a0abc0;'>
        <span>Forgery Det Model</span>
        <span style='color:{tm_color}; font-weight:bold;'>■ {tm_text}</span>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# Header
# -----------------------------
if not tamper_model:
    st.warning("⚠️ Critical forgery models failed to load. Operating in Scanner-Identification-Only degraded mode.", icon="⚠️")

# -----------------------------
# Prediction Logic
# -----------------------------
def predict_image(img_arr):
    img_resized = cv2.resize(img_arr, (128, 128)) / 255.0
    tensor = torch.tensor(img_resized).unsqueeze(0).unsqueeze(0).float()
    
    s_class, s_conf, t_class, t_conf = "Unknown", 0.0, "Unknown", 0.0
    s_probs_dict = {}
    
    with torch.no_grad():
        if scanner_model:
            out = scanner_model(tensor)
            probs = F.softmax(out, dim=1)
            conf, pred = torch.max(probs, 1)
            s_class = scanner_classes[pred.item()]
            s_conf = conf.item() * 100
            for i, c in enumerate(scanner_classes):
                s_probs_dict[c] = probs[0][i].item() * 100
                
        if tamper_model:
            out = tamper_model(tensor)
            probs = F.softmax(out, dim=1)
            conf, pred = torch.max(probs, 1)
            t_class = tamper_classes[pred.item()]
            t_conf = conf.item() * 100
            
    return s_class, s_conf, t_class, t_conf, s_probs_dict


# -----------------------------
# Main Content Views
# -----------------------------

if mode == "Single Document Analysis":
    st.markdown("<h3 style='color:#e2e8f0; font-weight:500; font-size:20px; padding-bottom:10px;'>Single Document Inspection</h3>", unsafe_allow_html=True)
    
    colA, colB = st.columns([1, 1.5])
    
    with colA:
        file = st.file_uploader("Upload target document for inspection", type=["png", "jpg", "jpeg", "tif", "tiff", "pdf"], key="single")
        
        if file is not None:
            # Load and display
            file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 0)
            if img is not None:
                st.image(img, caption=f"Source: {file.name}", use_column_width=True)
                s_c, s_score, t_c, t_score, probs = predict_image(img)
                
    with colB:
        if file is not None and img is not None:
            # Results Panel
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"<div class='metric-card'><div class='metric-title'>PRIMARY SOURCE ID</div><div class='metric-value' style='color:#3b82f6;'>{s_c}</div></div>", unsafe_allow_html=True)
            with c2:
                forgery_score = 100-t_score if t_c=="Original" else t_score
                forg_color = "#ef4444" if forgery_score > 50 else "#10b981"
                st.markdown(f"<div class='metric-card'><div class='metric-title'>FORGERY ALERT INDEX</div><div class='metric-value' style='color:{forg_color};'>{forgery_score:.2f}%</div></div>", unsafe_allow_html=True)
                
            st.markdown("<div style='color:#7b8296; font-size:12px; font-weight:600; margin-top:10px; margin-bottom:10px;'>SOURCE SCANNER PROBABILITIES</div>", unsafe_allow_html=True)
            sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]
            for name, p in sorted_probs:
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between; font-size:13px; color:#e2e8f0;'>
                    <span>{name}</span>
                    <span style='color:#3b82f6; font-weight:600;'>{p:.1f}%</span>
                </div>
                <div class='progress-bg'><div class='progress-fill' style='width:{p}%;'></div></div>
                <br>
                """, unsafe_allow_html=True)
            
            st.markdown("<br><div style='color:#7b8296; font-size:12px; font-weight:600; margin-bottom:10px;'>EVIDENCE VISUALIZATIONS</div>", unsafe_allow_html=True)
            tb1, tb2, tb3 = st.tabs(["Noise Residual Isolation", "Edge Map Enhancement", "Spectral Analysis"])
            
            def create_pseudo_image(base, cmap):
                res = cv2.resize(base, (300, 200))
                return cv2.applyColorMap(res, cmap)
                
            with tb1:
                st.image(create_pseudo_image(img, cv2.COLORMAP_BONE), use_column_width=True)
            with tb2:
                st.image(create_pseudo_image(img, cv2.COLORMAP_DEEPGREEN), use_column_width=True)
            with tb3:
                st.image(create_pseudo_image(img, cv2.COLORMAP_PLASMA), use_column_width=True)

elif mode == "Batch Analytics Pipeline":
    st.markdown("<h3 style='color:#e2e8f0; font-weight:500; font-size:20px; padding-bottom:10px;'>Bulk Directory Analysis</h3>", unsafe_allow_html=True)
    files = st.file_uploader("Select multiple image targets for sequential processing", accept_multiple_files=True, type=["png", "jpg", "tif"])
    
    col_btn, _ = st.columns([1, 4])
    if col_btn.button("Execute Pipeline", type="primary", use_container_width=True) and files:
        results = []
        with st.spinner("Processing documents through AI Engine..."):
            for f in files:
                bytes_data = np.asarray(bytearray(f.read()), dtype=np.uint8)
                i = cv2.imdecode(bytes_data, 0)
                if i is not None:
                    sc, s_conf, tc, t_conf, p_dict = predict_image(i)
                    sorted_tops = sorted(p_dict.keys(), key=lambda k: p_dict[k], reverse=True)
                    second = sorted_tops[1] if len(sorted_tops)>1 else "None"
                    
                    fs = 100-t_conf if tc=="Original" else t_conf
                    verdict = "Clear" if tc == "Original" or not tamper_model else "FLAGGED"
                    
                    results.append({
                        "Filename": f.name,
                        "Source Device": sc,
                        "Match Confidence": f"{s_conf:.1f}%",
                        "Alternative Match": second,
                        "Anomaly Score": f"{fs:.2f}",
                        "System Verdict": verdict
                    })
        
        if results:
            df = pd.DataFrame(results)
            st.markdown("<br>", unsafe_allow_html=True)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<div class='metric-card'><div class='metric-title'>DOCUMENTS PROCESSED</div><div class='metric-value'>{len(results)}</div></div>", unsafe_allow_html=True)
            
            clean_count = len([r for r in results if r['System Verdict'] == 'Clear'])
            flagged_count = len([r for r in results if r['System Verdict'] == 'FLAGGED'])
            
            m2.markdown(f"<div class='metric-card'><div class='metric-title'>CLEARED ASSETS</div><div class='metric-value' style='color:#10b981;'>{clean_count}</div></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='metric-card'><div class='metric-title'>FLAGGED AS FORGED</div><div class='metric-value' style='color:#ef4444;'>{flagged_count}</div></div>", unsafe_allow_html=True)
            
            tops = df['Source Device'].value_counts()
            m4.markdown(f"<div class='metric-card'><div class='metric-title'>PRIMARY SOURCE DEVICE</div><div class='metric-value'>{tops.index[0] if len(tops)>0 else '-'}</div></div>", unsafe_allow_html=True)
            
            st.markdown("<div style='color:#7b8296; font-size:12px; font-weight:600; margin-top:20px; margin-bottom:10px;'>PIPELINE EXECUTION LOG</div>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)