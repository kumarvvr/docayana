from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from fastapi.testclient import TestClient

from docayana.app import create_app
from docayana.settings import Settings

SETTINGS = Settings(gcp_creds=Path("unused.json"), _env_file=None)


class FakeDatabase:
    def __init__(self) -> None:
        self.opened_with: Settings | None = None
        self.closed = False
        self.client = object()

    @contextmanager
    def __call__(self, settings: Settings) -> Iterator[object]:
        self.opened_with = settings
        yield self.client
        self.closed = True


def test_healthz_reports_ok() -> None:
    with TestClient(create_app(SETTINGS, FakeDatabase())) as client:
        response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_route_returns_404() -> None:
    with TestClient(create_app(SETTINGS, FakeDatabase())) as client:
        assert client.get("/no-such-route").status_code == 404


def test_lifespan_opens_database_on_startup_and_closes_it_on_shutdown() -> None:
    database = FakeDatabase()
    app = create_app(SETTINGS, database)

    with TestClient(app):
        assert database.opened_with is SETTINGS
        assert app.state.db is database.client
        assert not database.closed

    assert database.closed
