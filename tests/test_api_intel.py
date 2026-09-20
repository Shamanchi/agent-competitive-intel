"""API-тесты без сети: TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.watch import get_store

BASE = {"competitor": "Acme", "price": 99, "features": ["sso"], "news_count": 3}


@pytest.fixture()
def client() -> TestClient:
    get_store().clear()
    with TestClient(create_app()) as test_client:
        yield test_client
    get_store().clear()


def test_health(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_watch_check_digest_flow(client: TestClient) -> None:
    assert client.post("/api/v1/watch", json=BASE).status_code == 200
    moved = dict(BASE, price=79, features=["sso", "audit-log"], news_count=9)
    check = client.post("/api/v1/check", json=moved)
    assert check.status_code == 200
    assert {change["kind"] for change in check.json()["changes"]} == {
        "price_drop",
        "feature_added",
        "news_spike",
    }
    digest = client.get("/api/v1/digest")
    assert digest.status_code == 200
    assert "## Acme" in digest.json()["digest_md"]


def test_check_without_baseline(client: TestClient) -> None:
    resp = client.post("/api/v1/check", json=BASE)
    assert resp.status_code == 404


@pytest.mark.integration()
def test_competitors_shape(client: TestClient) -> None:
    """Интеграционный по маркеру: список конкурентов, без сети."""
    client.post("/api/v1/watch", json=BASE)
    resp = client.get("/api/v1/competitors")
    assert resp.status_code == 200
    assert resp.json() == {"competitors": ["Acme"]}
