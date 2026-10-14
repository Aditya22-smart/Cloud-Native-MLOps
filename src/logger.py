"""Structured JSON logging to stdout."""
import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for field in (
            "client_ip",
            "http_status",
            "latency_ms",
            "model_version",
            "predicted_price",
        ):
            value = getattr(record, field, None)
            if value is not None:
                event[field] = value

        if record.exc_info:
            event["exception"] = self.formatException(record.exc_info)

        return json.dumps(event, default=str)


def get_logger(name="pricing-api"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not any(
        isinstance(handler, logging.StreamHandler)
        and getattr(handler, "_pricing_json_handler", False)
        for handler in logger.handlers
    ):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        handler._pricing_json_handler = True
        logger.addHandler(handler)

    logger.propagate = False
    return logger
