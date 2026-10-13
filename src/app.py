import logging
import os
import time
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "pipeline.pkl"

NUMERIC_FEATURES = [
    "Base_Price",
    "Competitor_Price",
    "Inventory_Level",
    "Units_Sold_Past_7D",
    "Discount_Pct",
    "Seasonal_Trend",
]
CATEGORICAL_FEATURES = ["Promotion_Type"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

PROMOTION_TYPES = {"none", "percentage", "bundle", "clearance"}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pricing-api")

app = Flask(__name__)

_model = None
_model_error = None

try:
    if MODEL_PATH.is_file() and MODEL_PATH.stat().st_size > 0:
        _model = joblib.load(MODEL_PATH)
    else:
        _model_error = "Trained model artifact is missing or empty."
except Exception:
    logger.exception("Failed to load model")
    _model_error = "Trained model could not be loaded."


def get_model():
    """Return the loaded model or raise if unavailable."""
    if _model is None:
        raise RuntimeError(_model_error or "Model is unavailable.")
    return _model


def validate_payload(payload):
    """Validate and normalize the seven model input fields."""
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")

    missing = sorted(set(FEATURES) - set(payload))
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    values = {}
    for name in NUMERIC_FEATURES:
        value = payload[name]
        if isinstance(value, bool):
            raise ValueError(f"{name} must be numeric.")
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{name} must be numeric.") from None

        if not pd.notna(number) or number in (float("inf"), float("-inf")):
            raise ValueError(f"{name} must be finite.")

        values[name] = number

    for name in ("Inventory_Level", "Units_Sold_Past_7D"):
        if not values[name].is_integer() or values[name] < 0:
            raise ValueError(f"{name} must be a non-negative integer.")
        values[name] = int(values[name])

    for name in ("Base_Price", "Competitor_Price"):
        if values[name] <= 0:
            raise ValueError(f"{name} must be greater than zero.")

    if not 0 <= values["Discount_Pct"] <= 100:
        raise ValueError("Discount_Pct must be between 0 and 100.")

    if values["Seasonal_Trend"] <= 0:
        raise ValueError("Seasonal_Trend must be greater than zero.")

    promotion = payload["Promotion_Type"]
    if not isinstance(promotion, str):
        raise ValueError("Promotion_Type must be a string.")
    promotion = promotion.strip().lower()
    if promotion not in PROMOTION_TYPES:
        raise ValueError(
            f"Promotion_Type must be one of {sorted(PROMOTION_TYPES)}."
        )
    values["Promotion_Type"] = promotion

    return values


@app.before_request
def start_timer():
    request.start_time = time.perf_counter()


@app.after_request
def log_request(response):
    elapsed_ms = (
        time.perf_counter() - getattr(request, "start_time", time.perf_counter())
    ) * 1000
    logger.info(
        "request_complete",
        extra={
            "client_ip": request.remote_addr,
            "http_status": response.status_code,
            "latency_ms": round(elapsed_ms, 2),
        },
    )
    return response


@app.get("/")
def index():
    return jsonify({
        "service": "Cloud-Native MLOps Dynamic Pricing API",
        "status": "running",
        "endpoints": ["/health", "/api/predict", "/api/retrain"],
    })


@app.get("/health")
def health():
    if _model is None:
        return jsonify({
            "status": "unhealthy",
            "model_loaded": False,
            "error": _model_error or "Model unavailable.",
        }), 503

    return jsonify({"status": "healthy", "model_loaded": True}), 200


@app.post("/api/predict")
def predict():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json."}), 415

    try:
        features = validate_payload(request.get_json(silent=True))
        model = get_model()
        frame = pd.DataFrame([features], columns=FEATURES)
        predicted_price = float(model.predict(frame)[0])

        logger.info(
            "prediction_complete",
            extra={
                "client_ip": request.remote_addr,
                "input_features": features,
                "predicted_price": round(predicted_price, 2),
            },
        )

        return jsonify({"predicted_price": round(predicted_price, 2)}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Prediction failed")
        return jsonify({"error": "Prediction failed."}), 500


@app.post("/api/retrain")
def retrain():
    expected_token = os.environ.get("RETRAIN_TOKEN")
    supplied_token = request.headers.get("X-Retrain-Token")

    if not expected_token:
        return jsonify({
            "error": "Retraining is not configured on this service."
        }), 503

    if supplied_token != expected_token:
        return jsonify({"error": "Unauthorized."}), 401

    return jsonify({
        "error": "Retraining is not implemented yet. "
                 "Use the training script for now."
    }), 501


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
