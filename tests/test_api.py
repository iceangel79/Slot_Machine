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


# --- configuration editor (decision 0016) ---


def test_evaluate_returns_theoretical_values():
    response = client.post("/api/configurations/evaluate", json=game.DEFAULT_CONFIG)

    assert response.status_code == 200
    data = response.get_json()
    assert data["rtp"] == pytest.approx(0.9098, abs=0.0001)
    assert len(data["rules"]) == len(game.DEFAULT_CONFIG["paytable"])


def test_evaluate_rejects_invalid_configuration():
    config = {"reel_strips": [["BLANK"] * 31] * 3, "paytable": []}

    response = client.post("/api/configurations/evaluate", json=config)

    assert response.status_code == 400
    assert "30" in response.get_json()["error"]


def test_new_configuration_is_saved():
    config = {
        "reel_strips": [["CHERRY", "BLANK"], ["CHERRY", "BLANK"], ["SEVEN"]],
        "paytable": [{"type": "cherry_count", "count": 2, "payout": 3}],
    }

    response = client.post(
        "/api/configurations", json={"name": "  Test config  ", **config}
    )

    assert response.status_code == 201
    saved = response.get_json()
    assert saved["name"] == "Test config"
    assert saved["reel_strips"] == config["reel_strips"]
    assert saved["paytable"] == config["paytable"]
    ids = [c["id"] for c in client.get("/api/configurations").get_json()]
    assert saved["id"] in ids


@pytest.mark.parametrize("name", [None, "", "   ", "x" * 101])
def test_configuration_without_valid_name_is_rejected(name):
    body = {"name": name, **game.DEFAULT_CONFIG}

    assert client.post("/api/configurations", json=body).status_code == 400


def test_invalid_configuration_is_not_saved():
    body = {"name": "Broken", "reel_strips": [], "paytable": []}

    assert client.post("/api/configurations", json=body).status_code == 400
