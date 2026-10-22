# 0004. Authentication and authorization

Status: accepted
Date: 2026-10-17

## Context
Users and authentication are mandatory. Access must be checked on every call without adding a database round trip that breaks the latency targets.

## Decision
- **Amazon Cognito user pools** issue JWTs. The API verifies the signature, issuer, audience and expiry against Cognito's cached JWKS (`infrastructure/auth/cognito.py`) and builds a `Principal` from `sub`.
- Every endpoint except `/healthz` and `/readyz` requires a bearer token; a missing or bad token returns 401.
- **Authorization is per workspace by role**: `viewer` reads, `editor` also writes nodes and properties, `owner` also manages members and workspace definitions. Each role includes the ones below it.
- The workspace comes from the URL path (`/v1/workspaces/{workspace_id}/...`) and is checked against the caller's membership item on every request; a non-member gets 403.
- Service clients use Cognito's client-credentials flow and hold a membership like a user.

## Consequences
- One `get_item` per request for the membership check; cache it briefly if it shows up in latency.
- No per-node permissions in v1.
- Action: add PyJWT to `pyproject.toml`.
- Settles scope open question 7 (identity provider).
