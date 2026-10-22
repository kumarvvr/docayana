# CLAUDE.md

Guidance for Claude Code working in this repository.

> Items marked **(inferred)** were not found in the repo and are best guesses. Correct or delete them.

## Git workflow
- Commit every code change; don't leave work uncommitted.
- Commit messages are full and descriptive: an imperative subject line under ~72 chars, a blank line, then a body explaining what changed and why.
- Keep the local repo in sync with github.com/kumarvvr/docayana by pushing `main` after each commit; never fetch or pull.
- Never commit secrets: key files, `.env`, or output that dumps `os.environ`.

## Project overview
Docayana is a high-performance REST API for trees of nodes of arbitrary width and depth. Each node has a type that supplies configurable default properties, users can add custom properties, a pre-defined catalog of node types and properties ships as a local settings file, data lives in DynamoDB, and every request is authenticated.
Status: architected skeleton only, no business features yet. Layers, app factory, settings, problem+json error handling, request IDs, `/healthz` + `/readyz`, DynamoDB table adapter and tests exist. No git repo yet.

## Product scope and decisions
- `docs/scope.md` is the product scope: concepts, v1 features, out-of-scope list, DynamoDB access patterns, NFRs and open questions. Load the `product-scope` skill before designing or building a feature, endpoint, data model or auth change.
- `docs/adr/` holds architecture decision records; an accepted ADR overrides the scope. Format is in `docs/adr/README.md`.

## Stack
- Python 3.15 (venv at `env/`, built from `C:\Python\Python315`), Windows dev machine
- FastAPI 0.143 + Uvicorn, Pydantic v2 + pydantic-settings
- AWS DynamoDB via boto3 (single-table design); S3 for large blobs
- OpenTelemetry SDK + OTLP HTTP exporter; Sentry SDK is also installed **(inferred** as intended for error reporting**)**
- Dev tooling (the `dev` extra in `pyproject.toml`): ruff, mypy (strict, configured in `pyproject.toml`), boto3-stubs, pytest, pytest-cov, moto. Install with `pip install -e ".[dev]"`.
- OpenTelemetry is wired in `infrastructure/telemetry.py` and off by default (`DOCAYANA_OTEL_ENABLED`). Sentry is not wired.

## Intended layout
```
pyproject.toml           # deps + ruff/mypy/pytest config
src/docayana/
  domain/  application/  infrastructure/  api/
  main.py                # composition root
tests/
  unit/  integration/  api/  conftest.py
env/                     # local venv, never commit
```
Layer rules are in the `clean-architecture` skill.

## Commands (PowerShell, from the repo root)
```powershell
.\env\Scripts\Activate.ps1                     # activate venv
pip install -e ".[dev]"                        # install app + dev tools into env/
fastapi dev src/docayana/main.py               # run locally with reload
uvicorn docayana.main:app --workers 4          # prod-style run
ruff format . ; ruff check .                   # format + lint
mypy                                           # strict type-check of src + tests (config in pyproject.toml)
pytest -q                                      # tests
pytest --cov=docayana --cov-report=term-missing
```
Config comes from system env vars prefixed `DOCAYANA_` (a `.env` file in the repo root also works; `.env.local` is a template). AWS access:
- Region: `DOCAYANA_AWS_REGION`, else `AWS_REGION`, else `AWS_DEFAULT_REGION`. Required; startup fails without it.
- Endpoint override (DynamoDB Local): `DOCAYANA_DYNAMODB_ENDPOINT_URL` or `AWS_ENDPOINT_URL_DYNAMODB`; blank means real AWS.
- Credentials: boto3's default chain only (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` [+ `AWS_SESSION_TOKEN`], `AWS_PROFILE`, or an IAM role). Never put them in `Settings`. Startup fails with `AwsCredentialsMissing` if none are found.
- Tests scrub every `AWS_*` and `DOCAYANA_*` var (`tests/conftest.py`), so a developer's environment never leaks in. Local DynamoDB for manual runs: DynamoDB Local **(inferred**; the skills only mandate moto/DynamoDB Local for tests**)**.

## Always-apply conventions
- Dependencies point inward: `domain` <- `application` <- `infrastructure` / `api`. Wire everything in the composition root only.
- Full type hints; code must pass `ruff check` and `mypy --strict`.
- Smallest obviously-correct code: short functions, guard clauses, no dead code, comments explain *why*.
- Read config only through the injected `Settings`; never `os.environ` elsewhere.
- No `boto3`/`ClientError`/`Decimal` above `infrastructure/`; no `HTTPException` in use cases.
- Never `scan` DynamoDB in request paths; always paginate.
- **New functionality must ship with unit tests** in `tests/unit/`, in the same commit: every new function, endpoint, tool or bug fix. A change without tests is not done. No real cloud or network calls in tests.
- Add packages to `pyproject.toml`, not ad hoc `pip install`. Never commit `env/` or `.env`.

## Testing
- Framework: pytest (config in `pyproject.toml`), with pytest-cov for coverage and FastAPI's `TestClient` for endpoints.
- Layout: `tests/unit/` mirrors the code (`tests/unit/tools/` for `tools/`); shared fixtures in `tests/conftest.py`, which also scrubs `DOCAYANA_*` and Google credential env vars so tests never reach real services.
- `tools/infra` and `tools/utilities` are on pytest's `pythonpath`, so tests import those scripts by module name (`import node_id`).
- Fake external clients (Firestore, Firebase) with small hand-written classes or `monkeypatch`; never call real services.
- Run before every commit: `pytest` (or `pytest --cov=. ` for coverage). All tests must pass.

## Skills (`.claude/skills/`)
Load the matching skill before working in that area; they hold the detail, this file does not repeat it.
- `product-scope`: what docayana does, v1 scope, access patterns, ADRs
- `clean-architecture`: where code lives, ports/adapters, wiring
- `python-coding`: typing, idioms, errors, logging, tooling
- `compact-clean-code`: function size, naming, review checklist
- `fastapi-service`: app factory, routers, DI, settings, lifespan, observability
- `rest-api-design`: URLs, status codes, problem+json, pagination, ETags
- `dynamodb-coding`: key design, boto3 patterns, error translation
- `python-testing`: test layout, fakes, TestClient, moto
