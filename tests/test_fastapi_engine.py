"""
Tests for DeltaForge FastAPI Microservice Endpoints
"""

from fastapi.testclient import TestClient
from fastapi_app.main import app

client = TestClient(app)


def test_root_and_health():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ONLINE"

    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "HEALTHY"


def test_strike_calculation_endpoint():
    res = client.get("/api/v1/strikes/calculate", params={"index": "NIFTY", "spot": 25050.0})
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["atm_strike"] == 25050
    assert data["calls"]["itm_1"] == 25000
    assert data["calls"]["otm_1"] == 25100


def test_greeks_calculation_endpoint():
    payload = {
        "spot": 25000,
        "strike": 25000,
        "time_to_expiry_days": 3,
        "iv": 0.14,
        "option_type": "CE",
    }
    res = client.post("/api/v1/greeks/calculate", json=payload)
    assert res.status_code == 200
    greeks = res.json()["greeks"]
    assert "delta" in greeks
    assert "theta_day" in greeks
    assert greeks["delta"] > 0


def test_hard_exit_square_off_endpoint():
    payload = {
        "accounts": [
            {"client_id": "AB1234", "broker_name": "zerodha"},
            {"client_id": "DH9876", "broker_name": "dhan"},
        ]
    }
    res = client.post("/api/v1/risk/square-off-all", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "HARD_EXIT_315PM"
    assert data["accounts_processed"] == 2
