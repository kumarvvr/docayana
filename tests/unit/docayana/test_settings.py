from pathlib import Path

import pytest
from pydantic import ValidationError

from docayana.settings import Settings


def test_reads_docayana_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCAYANA_GCP_CREDS", "C:/keys/key.json")
    monkeypatch.setenv("DOCAYANA_FIRESTORE_DATABASE", "staging")

    settings = Settings(_env_file=None)

    assert settings.gcp_creds == Path("C:/keys/key.json")
    assert settings.firestore_database == "staging"


def test_database_defaults_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCAYANA_GCP_CREDS", "key.json")

    assert Settings(_env_file=None).firestore_database == "(default)"


def test_missing_creds_fails_fast() -> None:
    with pytest.raises(ValidationError, match="gcp_creds"):
        Settings(_env_file=None)
