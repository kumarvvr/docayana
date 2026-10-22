"""Shared fixtures for every test."""

import os
from collections.abc import Iterator

import pytest

# Variables that could point a test at real credentials or a real project.
SCRUBBED_PREFIXES = ("DOCAYANA_", "GOOGLE_", "FIREBASE_", "FIRESTORE_")


@pytest.fixture(autouse=True)
def scrubbed_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Keep a developer's real cloud settings out of every test."""
    for name in list(os.environ):
        if name.startswith(SCRUBBED_PREFIXES):
            monkeypatch.delenv(name)
    yield
