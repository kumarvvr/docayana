---
name: fastapi-service
description: FastAPI patterns for this service (app factory, routers, dependency injection, Pydantic schemas, error handlers, settings, lifespan, OpenTelemetry). Use when adding endpoints or touching app startup.
---

# FastAPI Service

## Structure
- `create_app(settings: Settings) -> FastAPI` app factory in `api/app.py`; `main.py` calls it. No app built at import time in tests.
- One `APIRouter` per resource in `api/routers/<resource>.py`, mounted with `prefix="/v1/<resource>"` and `tags`.
- Lifespan (`@asynccontextmanager`) creates shared clients (boto3 table, httpx client) and stores them on `app.state`; close them on shutdown.

## Endpoints
- Thin handlers: validate input -> call use case -> map result to response schema. No business logic or DB calls in routers.
- Inject use cases with `Depends`; use `Annotated[DocService, Depends(get_doc_service)]` aliases to keep signatures short.
- Declare `response_model`, `status_code`, and `responses={404: {...}}` on every route.
- Pydantic v2 schemas: `model_config = ConfigDict(extra="forbid")` for requests; use `Field` constraints instead of manual checks.
- Use `def` handlers for blocking code (boto3) so FastAPI runs them in the threadpool; use `async def` only with async I/O throughout.

## Errors
- Register exception handlers that map domain errors to problem+json responses (see `rest-api-design`); don't raise `HTTPException` from use cases.

## Config and observability
- `Settings(BaseSettings)` with `env_prefix="DOCAYANA_"` and `.env` support; provide via a cached `get_settings` dependency, overridable in tests.
- Instrument with OpenTelemetry (FastAPI + botocore instrumentation); add request IDs to logs.
- Health endpoint `GET /healthz` with no dependencies on external services; `GET /readyz` may check them.

## Running
- Dev: `fastapi dev src/docayana/main.py`; prod: `uvicorn docayana.main:app --workers N`.
