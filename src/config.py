"""Centralized configuration for the dynamic pricing API."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = Path(
    os.getenv("MODEL_PATH", str(BASE_DIR / "model" / "pipeline.pkl"))
)

MODEL_VERSION = os.getenv("MODEL_VERSION", "dev")
RETRAIN_TOKEN = os.getenv("RETRAIN_TOKEN", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5000")
GCS_MODEL_BUCKET = os.getenv("GCS_MODEL_BUCKET", "")
LOGSTASH_URL = os.getenv("LOGSTASH_URL", "http://localhost:5080")
