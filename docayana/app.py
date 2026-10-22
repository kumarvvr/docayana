from collections.abc import AsyncIterator, Callable
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Any

from fastapi import FastAPI

from docayana.firestore import firestore_client
from docayana.settings import Settings

DatabaseFactory = Callable[[Settings], AbstractContextManager[Any]]


def create_app(
    settings: Settings, database: DatabaseFactory = firestore_client
) -> FastAPI:
    """Build the app; tests pass a fake `database` so no real connection is opened."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        with database(settings) as db:
            app.state.db = db
            yield

    app = FastAPI(title="docayana", lifespan=lifespan)
    app.state.settings = settings

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app
