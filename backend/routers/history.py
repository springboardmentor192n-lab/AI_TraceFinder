"""
/api/history — prediction history management
"""

import json
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()

HISTORY_FILE = Path(__file__).parent.parent / "prediction_history.json"


@router.get("/")
def get_history(limit: int = 50):
    """Return recent prediction history."""
    if not HISTORY_FILE.exists():
        return {"history": [], "total": 0}
    try:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
        return {"history": history[:limit], "total": len(history)}
    except Exception as e:
        logger.error(f"Could not read history: {e}")
        return {"history": [], "total": 0}


@router.delete("/")
def clear_history():
    """Clear all prediction history."""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    return {"message": "History cleared"}
