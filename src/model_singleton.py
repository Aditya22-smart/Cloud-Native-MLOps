"""Thread-safe model loading and validated model replacement."""
import logging
import threading
from pathlib import Path

import joblib

from src.config import MODEL_PATH

logger = logging.getLogger("pricing-api")


class ModelSingleton:
    def __init__(self, model_path=MODEL_PATH):
        self.model_path = Path(model_path)
        self._lock = threading.RLock()
        self._model = None
        self._error = "Trained model artifact is missing or empty."
        self._load_initial_model()

    def _load_initial_model(self):
        try:
            model = self._load_candidate(self.model_path)
            with self._lock:
                self._model = model
                self._error = ""
        except Exception:
            logger.exception("Failed to load initial model")
            with self._lock:
                self._model = None
                self._error = "Trained model could not be loaded."

    @staticmethod
    def _load_candidate(path):
        path = Path(path)
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError("Model artifact is missing or empty.")

        model = joblib.load(path)
        if not callable(getattr(model, "predict", None)):
            raise ValueError("Model artifact does not provide predict().")

        return model

    def get_model(self):
        with self._lock:
            if self._model is None:
                raise RuntimeError(self._error or "Model is unavailable.")
            return self._model

    def is_loaded(self):
        with self._lock:
            return self._model is not None

    def replace_from_path(self, candidate_path):
        """Validate a candidate first, then atomically swap the active model."""
        candidate = self._load_candidate(candidate_path)

        with self._lock:
            self._model = candidate
            self._error = ""

        logger.info("model_replaced")
        return True


model_manager = ModelSingleton()
