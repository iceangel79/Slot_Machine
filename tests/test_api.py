"""Tests for the HTTP endpoints. They need a database (decision 0011)."""

from app import app


def test_index_page_is_served():
    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"Slot Machine Simulator" in response.data


def test_health_reports_database_ok():
    response = app.test_client().get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}