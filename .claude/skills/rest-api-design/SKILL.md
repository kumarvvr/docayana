---
name: rest-api-design
description: REST API conventions for this service (resource naming, methods, status codes, errors, pagination, versioning, idempotency). Use when designing or changing HTTP endpoints.
---

# REST API Design

## Resources and URLs
- Plural nouns, kebab-case, no verbs: `/v1/documents`, `/v1/documents/{document_id}/versions`.
- Nest at most one level; use query filters beyond that (`/v1/versions?document_id=...`).
- Version in the path (`/v1`); breaking changes require a new version.
- JSON fields in `snake_case`; timestamps ISO-8601 UTC; IDs are opaque strings.

## Methods and status codes
| Action | Method | Success |
|---|---|---|
| List | GET /documents | 200 |
| Read | GET /documents/{id} | 200 |
| Create | POST /documents | 201 + `Location` header |
| Replace | PUT /documents/{id} | 200 |
| Partial update | PATCH /documents/{id} | 200 |
| Delete | DELETE /documents/{id} | 204 |
| Async work | POST /documents/{id}/exports | 202 + status URL |

Errors: 400 malformed, 401 unauthenticated, 403 forbidden, 404 not found, 409 conflict / failed precondition, 422 validation, 429 rate limited, 500 unexpected.

## Error body (RFC 9457 problem details)
```json
{"type": "https://docayana/errors/not-found", "title": "Document not found",
 "status": 404, "detail": "Document abc123 does not exist", "instance": "/v1/documents/abc123"}
```
Return `application/problem+json`. Never leak stack traces or internal exception text.

## Collections
- Cursor pagination: `?limit=50&cursor=<opaque>`; response `{"items": [...], "next_cursor": "..." | null}`. Cap `limit`.
- Filtering via query params; sorting via `?sort=created_at` / `-created_at`.

## Safety and concurrency
- GET/PUT/DELETE are idempotent; support `Idempotency-Key` header on POST that creates resources.
- Optimistic concurrency: return `ETag`, accept `If-Match` on PUT/PATCH/DELETE, reply 412 on mismatch.

## Contract
- Separate request and response schemas (`DocumentCreate`, `DocumentOut`); never return persistence models.
- Every endpoint has a summary, response model, and documented error responses in OpenAPI.
