from pathlib import Path
from typing import Any

import pytest

from docayana import firestore as module
from docayana.settings import Settings


def test_opens_named_app_on_configured_database_and_deletes_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, Any]] = []
    app, client = object(), object()
    monkeypatch.setattr(module.credentials, "Certificate", lambda path: ("cert", path))
    monkeypatch.setattr(
        module.firebase_admin,
        "initialize_app",
        lambda cred, name: calls.append(("init", (cred, name))) or app,
    )
    monkeypatch.setattr(
        module.firestore,
        "client",
        lambda app, database_id: calls.append(("client", (app, database_id))) or client,
    )
    monkeypatch.setattr(
        module.firebase_admin, "delete_app", lambda a: calls.append(("delete", a))
    )
    settings = Settings(
        gcp_creds=Path("key.json"), firestore_database="staging", _env_file=None
    )

    with module.firestore_client(settings) as db:
        assert db is client
        assert ("delete", app) not in calls

    assert calls == [
        ("init", (("cert", Path("key.json")), "docayana")),
        ("client", (app, "staging")),
        ("delete", app),
    ]
