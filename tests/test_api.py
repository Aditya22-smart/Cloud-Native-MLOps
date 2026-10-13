import pytest

from src.app import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def valid_payload():
    return {
        "Base_Price": 100,
        "Competitor_Price": 95,
        "Inventory_Level": 250,
        "Units_Sold_Past_7D": 80,
        "Promotion_Type": "percentage",
        "Discount_Pct": 10,
        "Seasonal_Trend": 1.1,
    }


def test_home_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["status"] == "running"


def test_health_reports_model_status(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["model_loaded"] is True


def test_predict_returns_price(client, valid_payload):
    response = client.post("/api/predict", json=valid_payload)
    assert response.status_code == 200
    assert isinstance(response.json["predicted_price"], (int, float))
    assert response.json["predicted_price"] > 0


def test_predict_rejects_missing_fields(client):
    response = client.post(
        "/api/predict",
        json={"Base_Price": 100},
    )
    assert response.status_code == 400
    assert "Missing required fields" in response.json["error"]


def test_predict_rejects_invalid_promotion(client, valid_payload):
    valid_payload["Promotion_Type"] = "invalid"
    response = client.post("/api/predict", json=valid_payload)
    assert response.status_code == 400


def test_predict_rejects_negative_price(client, valid_payload):
    valid_payload["Base_Price"] = -10
    response = client.post("/api/predict", json=valid_payload)
    assert response.status_code == 400


def test_predict_requires_json(client):
    response = client.post("/api/predict", data="not json")
    assert response.status_code == 415
