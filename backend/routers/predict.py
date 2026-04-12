"""
/api/predict — accepts an image, extracts features, runs ML model, returns result + viz.
"""

import io
import base64
import uuid
import time
import json
import logging
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.features import extract_all_features, get_noise_map, get_fft_map
from models.service import get_model_service


def pdf_to_image_bytes(pdf_bytes: bytes) -> bytes:
    """
    Convert first page of PDF to PNG image bytes for feature extraction.
    Uses pdf2image (poppler) if available, falls back to pypdf + Pillow rendering.
    """
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(pdf_bytes, dpi=150, first_page=1, last_page=1)
        if images:
            buf = io.BytesIO()
            images[0].save(buf, format="PNG")
            return buf.getvalue()
    except ImportError:
        pass

    try:
        import pypdf
        from PIL import Image as PILImage
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        page = reader.pages[0]
        # Extract embedded images from PDF page
        for img_obj in page.images:
            buf = io.BytesIO(img_obj.data)
            try:
                img = PILImage.open(buf)
                out = io.BytesIO()
                img.save(out, format="PNG")
                return out.getvalue()
            except Exception:
                continue
    except Exception:
        pass

    raise ValueError(
        "Could not render PDF. Install pdf2image + poppler:\n"
        "  pip install pdf2image\n"
        "  Windows: download poppler from https://github.com/oschwartz10612/poppler-windows/releases"
    )

logger = logging.getLogger(__name__)
router = APIRouter()

HISTORY_FILE = Path(__file__).parent.parent / "prediction_history.json"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/tiff", "image/bmp", "image/tif", "application/pdf", "image/x-tiff", "image/x-tif"}
MAX_SIZE_MB = 100  # 300 DPI TIFs can be 50-80MB


def _img_to_base64(img_bgr: np.ndarray) -> str:
    _, buf = cv2.imencode(".png", img_bgr)
    return base64.b64encode(buf).decode("utf-8")


def _save_history(entry: dict):
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                history = json.load(f)
        except Exception:
            history = []
    history.insert(0, entry)
    history = history[:100]  # keep last 100
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


@router.post("/")
async def predict_scanner(
    file: UploadFile = File(...),
    model: str = Form(default="best")
):
    """
    Upload a scanned image → returns:
    - predicted_scanner, confidence, all_probabilities
    - noise_map (base64 PNG), fft_map (base64 PNG)
    - feature stats
    """
    # Validate by extension (MIME types unreliable for TIF/PDF on Windows)
    fname = (file.filename or "").lower()
    allowed_exts = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".pdf")
    if not any(fname.endswith(ext) for ext in allowed_exts):
        raise HTTPException(400, f"Unsupported file type. Allowed: JPG, PNG, TIF, BMP, PDF")

    img_bytes = await file.read()
    size_mb = len(img_bytes) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(413, f"File too large ({size_mb:.1f} MB). Max {MAX_SIZE_MB} MB.")

    t0 = time.time()
    try:
        # Convert PDF to image if needed
        fname_lower = (file.filename or "").lower()
        if fname_lower.endswith(".pdf"):
            img_bytes = pdf_to_image_bytes(img_bytes)

        # Feature extraction
        features = extract_all_features(img_bytes)

        # Prediction
        svc = get_model_service()
        result = svc.predict(features, model_name=model)

        # Visualizations
        noise_map_img = get_noise_map(img_bytes)
        fft_map_img = get_fft_map(img_bytes)

        noise_map_b64 = _img_to_base64(noise_map_img)
        fft_map_b64 = _img_to_base64(fft_map_img)

        # Feature stats for display
        prnu_feats = features[:6].tolist()
        fft_feats = features[6:70].tolist()
        lbp_feats = features[70:].tolist()

        elapsed = round(time.time() - t0, 3)

        # Save to history
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "filename": file.filename,
            "predicted_scanner": result["predicted_scanner"],
            "confidence": result["confidence"],
            "model_used": result["model_used"],
            "processing_time_s": elapsed,
        }
        _save_history(entry)

        return JSONResponse({
            "success": True,
            "prediction": result,
            "visualizations": {
                "noise_map": noise_map_b64,
                "fft_map": fft_map_b64,
            },
            "feature_stats": {
                "prnu": {
                    "mean": round(prnu_feats[0], 6),
                    "std": round(prnu_feats[1], 6),
                    "skewness": round(prnu_feats[2], 4),
                    "kurtosis": round(prnu_feats[3], 4),
                    "energy": round(prnu_feats[4], 4),
                    "entropy": round(prnu_feats[5], 4),
                },
                "fft_power": fft_feats,
                "lbp_histogram": lbp_feats[:32],  # first 32 bins for chart
            },
            "meta": {
                "filename": file.filename,
                "size_mb": round(size_mb, 2),
                "processing_time_s": elapsed,
                "is_mock_model": result["is_mock"],
            }
        })

    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(500, f"Prediction failed: {str(e)}")


@router.get("/labels")
def get_labels():
    """Returns all scanner class labels the model knows."""
    svc = get_model_service()
    return {"labels": svc.get_label_names()}


@router.get("/metrics")
def get_metrics():
    """Returns model training metrics (if trained model is loaded)."""
    svc = get_model_service()
    metrics = svc.get_metrics()
    if not metrics:
        return {"message": "No trained model loaded yet. Run train.py first.", "metrics": {}}
    return {"metrics": metrics}
