from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_healthz_reports_ok() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_route_returns_404() -> None:
    assert client.get("/no-such-route").status_code == 404
