"""Tests for the HTTP endpoints. They need the test database (decision 0015).

random.org is never called: the tests replace rng.random_org_stop_positions
with monkeypatch (decision 0014).
"""

import pytest

from app import game, rng
from app.main import app

client = app.test_client()


def default_configuration_id():
    configurations = client.get("/api/configurations").get_json()
    return next(
        c["id"] for c in configurations if c["name"] == game.DEFAULT_CONFIG_NAME
    )


def post_spins(**body):
    return client.post("/api/spins", json=body)


def failing_random_org(strip_lengths):
    raise OSError("random.org not reachable")


# --- basics ---


def test_index_page_is_served():
    response = client.get("/")

    assert response.status_code == 200
    assert b"Slot Machine Simulator" in response.data


def test_health_reports_database_ok():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}


# --- configurations ---


def test_default_configuration_is_stored():
    response = client.get(f"/api/configurations/{default_configuration_id()}")

    assert response.status_code == 200
    configuration = response.get_json()
    assert configuration["reel_strips"] == game.DEFAULT_CONFIG["reel_strips"]
    assert configuration["paytable"] == game.DEFAULT_CONFIG["paytable"]


def test_unknown_configuration_returns_404():
    assert client.get("/api/configurations/999999").status_code == 404


# --- spins ---


def test_manual_spin_uses_random_org(monkeypatch):
    monkeypatch.setattr(rng, "random_org_stop_positions", lambda lengths: [9, 9, 9])

    response = post_spins(configuration_id=default_configuration_id(), mode="manual")

    assert response.status_code == 201
    data = response.get_json()
    assert data["rng_source"] == "random.org"
    assert data["spins"][0]["symbols"] == ["SEVEN", "SEVEN", "SEVEN"]
    assert data["total_payout"] == 200


def test_manual_spin_falls_back_to_python(monkeypatch):
    monkeypatch.setattr(rng, "random_org_stop_positions", failing_random_org)

    response = post_spins(configuration_id=default_configuration_id(), mode="manual")

    assert response.status_code == 201
    assert response.get_json()["rng_source"] == "python"


def test_auto_spins_use_python():
    response = post_spins(
        configuration_id=default_configuration_id(), mode="auto", count=50
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["rng_source"] == "python"
    assert data["count"] == 50
    assert len(data["spins"]) == 50
    assert data["total_bet"] == 50
    assert data["total_payout"] == sum(spin["payout"] for spin in data["spins"])


@pytest.mark.parametrize(
    "body",
    [
        {"mode": "auto"},
        {"configuration_id": "1", "mode": "auto"},
        {"configuration_id": 1, "mode": "turbo"},
        {"configuration_id": 1, "mode": "manual", "count": 2},
        {"configuration_id": 1, "mode": "auto", "count": 0},
        {"configuration_id": 1, "mode": "auto", "count": 10_001},
        {"configuration_id": 1, "mode": "auto", "count": True},
    ],
)
def test_invalid_spin_request_returns_400(body):
    assert client.post("/api/spins", json=body).status_code == 400


def test_spin_with_unknown_configuration_returns_404():
    response = post_spins(configuration_id=999999, mode="auto")

    assert response.status_code == 404