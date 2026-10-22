import socket

import pytest

from docayana.machine import machine_name


def test_returns_the_hostname(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "gethostname", lambda: "dev-box-2")

    assert machine_name() == "dev-box-2"


def test_matches_the_real_hostname() -> None:
    assert machine_name() == socket.gethostname()
