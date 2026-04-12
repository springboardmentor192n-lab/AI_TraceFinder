"""
Model loading and inference service.
Loads pre-trained SVM / RF from saved_model/ directory.
Falls back to a mock model if no trained model exists yet
(so the UI works before training is done).
"""

import os
import pickle
import json
import logging
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent.parent / "saved_model"


class MockModel:
    """
    Placeholder model used before real training.
    Returns random predictions with a disclaimer.
    """
    def __init__(self, label_names):
        self.label_names = label_names
        self.classes_ = np.array(label_names)

    def predict(self, X):
        return [np.random.choice(self.label_names)]

    def predict_proba(self, X):
        probs = np.random.dirichlet(np.ones(len(self.label_names)))
        return probs.reshape(1, -1)


# Default mock labels (Supatlantique scanner IDs — update after training)
DEFAULT_LABELS = [
    "Canon_CanoScan_LiDE_200",
    "Epson_Perfection_V39",
    "HP_ScanJet_Pro_2500f1",
    "Fujitsu_ScanSnap_ix1500",
    "Brother_ADS_2700W"
]


class ModelService:
    def __init__(self):
        self.svm = None
        self.rf = None
        self.et = None
        self.best = None
        self.label_names = DEFAULT_LABELS
        self.metrics = {}
        self.is_mock = True
        self._load()

    def _load(self):
        if not MODEL_DIR.exists():
            logger.warning(f"No saved_model dir found at {MODEL_DIR}. Using mock model.")
            self.best = MockModel(self.label_names)
            return

        try:
            with open(MODEL_DIR / "best_model.pkl", "rb") as f:
                self.best = pickle.load(f)
            with open(MODEL_DIR / "svm_model.pkl", "rb") as f:
                self.svm = pickle.load(f)
            with open(MODEL_DIR / "rf_model.pkl", "rb") as f:
                self.rf = pickle.load(f)
            if (MODEL_DIR / "et_model.pkl").exists():
                with open(MODEL_DIR / "et_model.pkl", "rb") as f:
                    self.et = pickle.load(f)
            with open(MODEL_DIR / "label_encoder.pkl", "rb") as f:
                enc = pickle.load(f)
                self.label_names = list(enc.classes_)
            if (MODEL_DIR / "metrics.json").exists():
                with open(MODEL_DIR / "metrics.json") as f:
                    self.metrics = json.load(f)
            self.is_mock = False
            logger.info(f"Loaded trained model | Classes: {self.label_names}")
        except Exception as e:
            logger.error(f"Error loading model: {e}. Using mock model.")
            self.best = MockModel(self.label_names)

    def predict(self, feature_vector: np.ndarray, model_name: str = "best") -> dict:
        """
        Run prediction on a feature vector.
        Returns dict with predicted_scanner, confidence, all_probabilities.
        """
        X = feature_vector.reshape(1, -1)

        model_map = {"svm": self.svm, "rf": self.rf, "et": self.et, "best": self.best}
        model = model_map.get(model_name, self.best)
        if model is None:
            model = self.best

        try:
            pred_idx = model.predict(X)[0]
            proba = model.predict_proba(X)[0]

            # pred_idx may be int (trained) or str (mock)
            if isinstance(pred_idx, (int, np.integer)):
                predicted_scanner = self.label_names[int(pred_idx)]
                confidence = float(proba.max())
            else:
                predicted_scanner = str(pred_idx)
                confidence = float(proba.max())

            all_probs = {
                name: round(float(p), 4)
                for name, p in zip(self.label_names, proba)
            }
            # Sort by probability descending
            all_probs = dict(sorted(all_probs.items(), key=lambda x: x[1], reverse=True))

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            predicted_scanner = self.label_names[0]
            confidence = 0.0
            all_probs = {n: 0.0 for n in self.label_names}

        return {
            "predicted_scanner": predicted_scanner,
            "confidence": round(confidence, 4),
            "all_probabilities": all_probs,
            "model_used": model_name,
            "is_mock": self.is_mock,
        }

    def get_metrics(self) -> dict:
        return self.metrics

    def get_label_names(self) -> list:
        return self.label_names


# Singleton
_service = None

def get_model_service() -> ModelService:
    global _service
    if _service is None:
        _service = ModelService()
    return _service
