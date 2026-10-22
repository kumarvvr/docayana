from dataclasses import dataclass, field
from typing import Any

import firestore_settings as settings
import firestore_setup
import pytest
from firestore_setup import ensure_collection
from google.api_core.exceptions import AlreadyExists


@dataclass
class FakeCollection:
    """Stands in for a Firestore collection reference; records create() calls."""

    existing_docs: int = 0
    lose_create_race: bool = False
    created: dict[str, dict[str, Any]] = field(default_factory=dict)

    def limit(self, count: int) -> "FakeCollection":
        self.existing_docs = min(self.existing_docs, count)
        return self

    def get(self) -> list[object]:
        return [object()] * self.existing_docs

    def document(self, doc_id: str) -> "FakeDocument":
        return FakeDocument(self, doc_id)


@dataclass
class FakeDocument:
    collection: FakeCollection
    doc_id: str

    def create(self, data: dict[str, Any]) -> None:
        if self.collection.lose_create_race:
            raise AlreadyExists("another writer created it first")
        self.collection.created[self.doc_id] = data


@dataclass
class FakeClient:
    collections: dict[str, FakeCollection] = field(default_factory=dict)

    def collection(self, name: str) -> FakeCollection:
        return self.collections.setdefault(name, FakeCollection())


def test_missing_collection_gets_its_marker_document() -> None:
    client = FakeClient()

    assert ensure_collection(client, "nodes") == "created"  # type: ignore[arg-type]
    marker = client.collections["nodes"].created[settings.MARKER_DOC_ID]
    assert marker["created_by"] == "firestore_setup"
    assert marker["created_at"] is firestore_setup.firestore.SERVER_TIMESTAMP


def test_collection_with_documents_is_left_unchanged() -> None:
    client = FakeClient({"nodes": FakeCollection(existing_docs=3)})

    assert ensure_collection(client, "nodes") == "exists, left unchanged"  # type: ignore[arg-type]
    assert client.collections["nodes"].created == {}


def test_losing_a_create_race_counts_as_existing() -> None:
    client = FakeClient({"nodes": FakeCollection(lose_create_race=True)})

    assert ensure_collection(client, "nodes") == "exists, left unchanged"  # type: ignore[arg-type]


def test_main_reports_every_configured_collection(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    first = settings.COLLECTIONS[0]
    client = FakeClient({first: FakeCollection(existing_docs=1)})
    monkeypatch.setattr(firestore_setup, "connect", lambda: client)

    firestore_setup.main()

    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == f"Database: {settings.DATABASE_ID}"
    assert f"{first}: exists, left unchanged" in lines
    for name in settings.COLLECTIONS[1:]:
        assert f"{name}: created" in lines


def test_connect_uses_the_key_file_from_the_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, Any] = {}
    monkeypatch.setenv(settings.CREDS_ENV_VAR, "/keys/service-account.json")
    monkeypatch.setattr(
        firestore_setup.credentials,
        "Certificate",
        lambda path: calls.setdefault("key", path),
    )
    monkeypatch.setattr(
        firestore_setup.firebase_admin,
        "initialize_app",
        lambda cred: calls.setdefault("app", cred),
    )
    monkeypatch.setattr(
        firestore_setup.firestore,
        "client",
        lambda database_id: calls.setdefault("database", database_id),
    )

    firestore_setup.connect()

    assert calls == {
        "key": "/keys/service-account.json",
        "app": "/keys/service-account.json",
        "database": settings.DATABASE_ID,
    }


def test_connect_fails_when_the_env_var_is_missing() -> None:
    with pytest.raises(KeyError, match=settings.CREDS_ENV_VAR):
        firestore_setup.connect()
