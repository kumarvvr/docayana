---
name: clean-architecture
description: Layering and dependency rules for this service (domain, application, infrastructure, API). Use when adding modules, deciding where code lives, or wiring dependencies.
---

# Clean Architecture

## Layers (dependencies point inward only)

```
src/docayana/
  domain/          # entities, value objects, domain errors. Pure Python, no I/O, no frameworks.
  application/     # use cases + ports (Protocol interfaces). Depends only on domain.
  infrastructure/  # adapters: DynamoDB repos, HTTP clients, settings. Implements ports.
  api/             # FastAPI routers, request/response schemas, DI wiring.
  main.py          # composition root: builds adapters, injects into use cases.
```

- `domain` imports nothing from other layers, and no `fastapi`, `boto3`, `pydantic_settings`.
- `application` defines ports as `typing.Protocol`; it never imports `infrastructure`.
- `infrastructure` and `api` are the outer ring; they may import inward, never each other's internals.
- Wiring happens only in the composition root (`main.py` / `api/dependencies.py`).

## Rules
- One use case = one class or function with a single public entry (`execute` / `__call__`).
- Use cases take and return domain objects or plain DTOs, never HTTP or DynamoDB shapes.
- Map at the boundary: API schema <-> domain in `api/`, DynamoDB item <-> domain in `infrastructure/`.
- Domain errors (`DocumentNotFound`) are raised inside; `api/` translates them to HTTP status codes.
- Prefer constructor injection; no global singletons or module-level clients outside the composition root.

## Example port + adapter

```python
# application/ports.py
class DocumentRepository(Protocol):
    def get(self, doc_id: DocumentId) -> Document | None: ...
    def save(self, doc: Document) -> None: ...

# infrastructure/dynamodb/document_repository.py
class DynamoDocumentRepository:
    def __init__(self, table) -> None:
        self._table = table
```

## Checklist before merging
- Can the use case be unit-tested with an in-memory fake? If not, a dependency leaked inward.
- No framework types in `domain/` or `application/`.
