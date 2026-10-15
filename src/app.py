
import time

import pandas as pd
from flask import Flask, jsonify, render_template, request

from src.config import RETRAIN_TOKEN
from src.logger import get_logger
from src.model_singleton import model_manager
model_manager.get_model().named_steps["model"].n_jobs = 1

app = Flask(__name__)
logger = get_logger()

NUMERIC_FEATURES = [
    "Base_Price",
    "Competitor_Price",
    "Inventory_Level",
    "Units_Sold_Past_7D",
    "Discount_Pct",
    "Seasonal_Trend",
]
FEATURES = NUMERIC_FEATURES + ["Promotion_Type"]
PROMOTION_TYPES = {"none", "percentage", "bundle", "clearance"}


def _validate_numeric_field(name, value):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric.")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be numeric.") from None

    if not pd.notna(number) or number in (float("inf"), float("-inf")):
        raise ValueError(f"{name} must be finite.")
    return number


def _validate_numeric_constraints(values):
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


def _validate_promotion(promotion):
    if not isinstance(promotion, str):
        raise ValueError("Promotion_Type must be a string.")
    cleaned = promotion.strip().lower()
    if cleaned not in PROMOTION_TYPES:
        raise ValueError(
            f"Promotion_Type must be one of {sorted(PROMOTION_TYPES)}."
        )
    return cleaned


def validate_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")

    missing = sorted(set(FEATURES) - set(payload))
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    values = {name: _validate_numeric_field(name, payload[name]) for name in NUMERIC_FEATURES}
    _validate_numeric_constraints(values)
    values["Promotion_Type"] = _validate_promotion(payload["Promotion_Type"])
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
    return render_template("index.html")


@app.get("/health")
def health():
    loaded = model_manager.is_loaded()
    status = "healthy" if loaded else "unhealthy"
    return jsonify({"status": status, "model_loaded": loaded}), (
        200 if loaded else 503
    )


@app.post("/api/predict")
def predict():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json."}), 415

    try:
        features = validate_payload(request.get_json(silent=True))
        model = model_manager.get_model()
        frame = pd.DataFrame([features], columns=FEATURES)
        predicted_price = float(model.predict(frame)[0])

        logger.info(
            "prediction_complete",
            extra={"predicted_price": round(predicted_price, 2)},
        )
        return jsonify({"predicted_price": round(predicted_price, 2)}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Prediction failed")
        return jsonify({"error": "Prediction failed."}), 500


@app.post("/api/retrain")
def retrain():
    if not RETRAIN_TOKEN:
        return jsonify({
            "error": "Retraining is not configured on this service."
        }), 503

    supplied_token = request.headers.get("Authorization", "")
    if supplied_token != f"Bearer {RETRAIN_TOKEN}":
        return jsonify({"error": "Unauthorized."}), 401

    return jsonify({
        "error": "Retraining is not implemented yet. Use the training script for now."
    }), 501


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
