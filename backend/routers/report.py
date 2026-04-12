"""
/api/report — generate downloadable PDF report from a prediction result
"""

import io
import base64
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)
router = APIRouter()


class ReportRequest(BaseModel):
    filename: str
    predicted_scanner: str
    confidence: float
    all_probabilities: Dict[str, float]
    model_used: str
    processing_time_s: float
    feature_stats: Dict[str, Any]
    is_mock: Optional[bool] = False
    noise_map_b64: Optional[str] = None
    fft_map_b64: Optional[str] = None


def _generate_html_report(req: ReportRequest) -> str:
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    conf_pct = round(req.confidence * 100, 1)
    conf_color = "#22c55e" if conf_pct >= 70 else "#f59e0b" if conf_pct >= 40 else "#ef4444"

    prob_rows = ""
    for scanner, prob in req.all_probabilities.items():
        pct = round(prob * 100, 1)
        bar_width = max(2, pct)
        bar_color = "#6366f1" if scanner == req.predicted_scanner else "#d1d5db"
        prob_rows += f"""
        <tr>
            <td style="padding:6px 8px;font-size:13px;color:#374151;">{scanner}</td>
            <td style="padding:6px 8px;">
                <div style="background:#e5e7eb;border-radius:4px;height:10px;width:100%">
                    <div style="background:{bar_color};border-radius:4px;height:10px;width:{bar_width}%"></div>
                </div>
            </td>
            <td style="padding:6px 8px;font-size:13px;font-weight:600;color:#111827;text-align:right">{pct}%</td>
        </tr>"""

    prnu = req.feature_stats.get("prnu", {})
    prnu_rows = "".join(
        f'<tr><td style="padding:4px 8px;color:#6b7280;font-size:12px">{k}</td>'
        f'<td style="padding:4px 8px;font-weight:600;font-size:12px;text-align:right">{v}</td></tr>'
        for k, v in prnu.items()
    )

    mock_banner = ""
    if req.is_mock:
        mock_banner = """
        <div style="background:#fef3c7;border:1px solid #fbbf24;border-radius:8px;padding:12px 16px;margin-bottom:20px">
            <strong>⚠ Mock Model:</strong> Train the model using <code>python train.py</code> with the 
            Supatlantique dataset for real predictions.
        </div>"""

    noise_img_tag = ""
    fft_img_tag = ""
    if req.noise_map_b64:
        noise_img_tag = f'<img src="data:image/png;base64,{req.noise_map_b64}" style="width:100%;border-radius:8px;margin-top:8px"/>'
    if req.fft_map_b64:
        fft_img_tag = f'<img src="data:image/png;base64,{req.fft_map_b64}" style="width:100%;border-radius:8px;margin-top:8px"/>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>TraceFinder Report — {req.filename}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f9fafb; color: #111827; }}
  .page {{ max-width: 900px; margin: 0 auto; background: white; padding: 48px 56px; }}
  .header {{ border-bottom: 3px solid #6366f1; padding-bottom: 24px; margin-bottom: 32px; }}
  .logo {{ font-size: 28px; font-weight: 800; color: #4f46e5; letter-spacing: -1px; }}
  .logo span {{ color: #a5b4fc; }}
  .subtitle {{ font-size: 13px; color: #6b7280; margin-top: 4px; }}
  .section {{ margin-bottom: 32px; }}
  .section-title {{ font-size: 15px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.05em; color: #6b7280; margin-bottom: 16px; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; }}
  .result-card {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    border-radius: 16px; padding: 28px 32px; color: white; margin-bottom: 24px; }}
  .result-scanner {{ font-size: 22px; font-weight: 700; margin-bottom: 8px; }}
  .result-conf {{ font-size: 14px; opacity: 0.9; }}
  .conf-badge {{ display: inline-block; background: rgba(255,255,255,0.2);
    border-radius: 20px; padding: 4px 16px; font-size: 20px; font-weight: 700; margin-top: 8px; color: white; }}
  table {{ width: 100%; border-collapse: collapse; }}
  .meta-table td {{ padding: 8px 4px; font-size: 14px; border-bottom: 1px solid #f3f4f6; }}
  .meta-table td:first-child {{ color: #6b7280; width: 160px; }}
  .meta-table td:last-child {{ font-weight: 600; }}
  .viz-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .viz-box {{ background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; }}
  .viz-title {{ font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 8px; }}
  .footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e7eb;
    font-size: 12px; color: #9ca3af; display: flex; justify-content: space-between; }}
  @media print {{ body {{ background: white; }} .page {{ padding: 24px; }} }}
</style>
</head>
<body>
<div class="page">

<div class="header">
  <div class="logo">Trace<span>Finder</span></div>
  <div class="subtitle">Forensic Scanner Identification Report &nbsp;·&nbsp; Generated {timestamp}</div>
</div>

{mock_banner}

<!-- Result card -->
<div class="result-card">
  <div style="font-size:12px;opacity:0.75;text-transform:uppercase;letter-spacing:0.05em">Identified Scanner</div>
  <div class="result-scanner">{req.predicted_scanner}</div>
  <div class="result-conf">Confidence Score</div>
  <div class="conf-badge" style="color:{conf_color}">{conf_pct}%</div>
</div>

<!-- File & model metadata -->
<div class="section">
  <div class="section-title">Analysis Details</div>
  <table class="meta-table">
    <tr><td>Input file</td><td>{req.filename}</td></tr>
    <tr><td>Model used</td><td>{req.model_used.upper()}</td></tr>
    <tr><td>Processing time</td><td>{req.processing_time_s}s</td></tr>
    <tr><td>Timestamp</td><td>{timestamp}</td></tr>
  </table>
</div>

<!-- Probability table -->
<div class="section">
  <div class="section-title">Scanner Probabilities</div>
  <table>
    <tbody>{prob_rows}</tbody>
  </table>
</div>

<!-- PRNU features -->
<div class="section">
  <div class="section-title">PRNU Feature Statistics</div>
  <table class="meta-table">
    <tbody>{prnu_rows}</tbody>
  </table>
</div>

<!-- Visualizations -->
<div class="section">
  <div class="section-title">Feature Visualizations</div>
  <div class="viz-grid">
    <div class="viz-box">
      <div class="viz-title">PRNU Noise Map</div>
      {noise_img_tag if noise_img_tag else '<div style="text-align:center;padding:40px;color:#9ca3af;font-size:13px">Not available</div>'}
    </div>
    <div class="viz-box">
      <div class="viz-title">FFT Frequency Spectrum</div>
      {fft_img_tag if fft_img_tag else '<div style="text-align:center;padding:40px;color:#9ca3af;font-size:13px">Not available</div>'}
    </div>
  </div>
</div>

<div class="footer">
  <span>TraceFinder v1.0 · Supatlantique Dataset · No-GPU Pipeline</span>
  <span>SVM + Random Forest · PRNU · FFT · LBP Features</span>
</div>

</div>
</body>
</html>"""
    return html


@router.post("/download")
def download_report(req: ReportRequest):
    """Generate and return an HTML report (printable as PDF from browser)."""
    try:
        html = _generate_html_report(req)
        buf = io.BytesIO(html.encode("utf-8"))
        filename = f"tracefinder_report_{req.filename.rsplit('.', 1)[0]}.html"
        return StreamingResponse(
            buf,
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        logger.exception("Report generation failed")
        raise HTTPException(500, f"Report generation failed: {e}")
