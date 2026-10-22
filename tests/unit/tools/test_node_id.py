import re
import sys

import node_id
import pytest
from node_id import DEFAULT_LENGTH, MAX_LENGTH, MIN_LENGTH, new_node_id

HEX = re.compile(r"[0-9a-f]+")


def run_cli(monkeypatch: pytest.MonkeyPatch, *args: str) -> None:
    monkeypatch.setattr(sys, "argv", ["node_id.py", *args])
    node_id.main()


def test_default_id_is_40_lowercase_hex_characters_like_a_git_commit() -> None:
    generated = new_node_id()

    assert len(generated) == DEFAULT_LENGTH == 40
    assert HEX.fullmatch(generated)


@pytest.mark.parametrize("length", [MIN_LENGTH, 17, 20, 39, MAX_LENGTH])
def test_id_has_requested_length_including_odd_lengths(length: int) -> None:
    generated = new_node_id(length)

    assert len(generated) == length
    assert HEX.fullmatch(generated)


@pytest.mark.parametrize("length", [-1, 0, 7, MIN_LENGTH - 1, MAX_LENGTH + 1])
def test_rejects_lengths_outside_the_allowed_range(length: int) -> None:
    with pytest.raises(ValueError, match=f"got {length}"):
        new_node_id(length)


def test_ids_do_not_repeat() -> None:
    generated = {new_node_id(MIN_LENGTH) for _ in range(10_000)}

    assert len(generated) == 10_000


def test_cli_prints_one_id_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run_cli(monkeypatch)

    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1
    assert HEX.fullmatch(lines[0])
    assert len(lines[0]) == DEFAULT_LENGTH


def test_cli_prints_count_ids_of_requested_length(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run_cli(monkeypatch, "-n", "5", "--length", "20")

    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 5
    assert all(len(line) == 20 for line in lines)


def test_cli_prints_nothing_for_zero_count(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run_cli(monkeypatch, "-n", "0")

    assert capsys.readouterr().out == ""


def test_cli_exits_with_message_for_bad_length(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(SystemExit, match="length must be between"):
        run_cli(monkeypatch, "--length", "7")
