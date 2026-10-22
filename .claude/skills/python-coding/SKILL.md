---
name: python-coding
description: Python style and idioms for this project (modern typed Python, Pydantic v2, project layout, tooling). Use whenever writing or reviewing Python code here.
---

# Python Coding

## Baseline
- Target the Python version in `env/` (3.12+ syntax is fine): `X | None`, `list[str]`, `match`, `type` aliases.
- Full type hints on every public function and method; code must pass `mypy --strict` (or `pyright`).
- Format and lint with `ruff format` + `ruff check` (rules: E, F, I, B, UP, SIM, RUF).
- Use a `src/` layout with absolute imports (`from docayana.domain import ...`).

## Idioms
- Data: `@dataclass(frozen=True, slots=True)` for domain objects; Pydantic `BaseModel` only at boundaries (API, config).
- Config: one `Settings(BaseSettings)` class from `pydantic-settings`, loaded once, injected. Never read `os.environ` elsewhere.
- Paths: `pathlib.Path`, not string joins. Time: timezone-aware `datetime.now(UTC)`.
- Enums: `StrEnum` for values that are serialized.
- Errors: define a small hierarchy per layer (`DomainError` -> `DocumentNotFound`). Never `except Exception: pass`; catch the narrowest type, re-raise with `raise ... from err`.
- Logging: `logger = logging.getLogger(__name__)`; structured, no f-strings in log calls (`logger.info("saved %s", doc_id)`); never log secrets or full documents.
- No mutable default args, no wildcard imports, no `print` in library code.
- Async: in `async def` code use async clients (`httpx.AsyncClient`, `aioboto3`) or offload blocking calls with `anyio.to_thread.run_sync`.

## Dependencies
- Add packages to `pyproject.toml` (pinned with a lock file), not ad hoc `pip install` into `env/`.
- `env/` is the local venv; never commit it.
