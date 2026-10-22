# 0005. REST API surface for nodes

Status: accepted
Date: 2026-10-17

## Context
The `rest-api-design` skill allows nesting one level below a resource. Nodes nest without limit, and moves and property updates have different write shapes.

## Decision
All node routes sit under `/v1/workspaces/{workspace_id}/nodes` (`api/routers/nodes.py`):

| Method and path | Purpose |
| --- | --- |
| `POST /nodes` | Create a root or child node; `Idempotency-Key` supported |
| `GET /nodes?parent_id=…` | List a node's children in order; without `parent_id`, list roots |
| `GET /nodes/{id}` | Get a node with effective properties |
| `GET /nodes/{id}/subtree?depth=…` | Subtree to depth 1 to 10, up to 1,000 nodes per page |
| `GET /nodes/{id}/ancestors` | Path from the root to the node |
| `PUT /nodes/{id}/position` | Move under a new parent or among siblings |
| `PATCH /nodes/{id}` | Set or remove property values |
| `DELETE /nodes/{id}` | Delete a node and its subtree |

- Children are a filter on the collection, not a nested `/nodes/{id}/children` route, so URLs never deepen with the tree.
- Moves get their own resource because they are a multi-item transaction, while `PATCH` is a single conditional write.
- Writes return an `ETag` and accept `If-Match`; a mismatch returns 412. Lists use cursor pagination.
- Members, workspaces and catalog reads have their own routers under `/v1/workspaces`.

## Consequences
- Clients build a tree view from repeated children calls or one capped subtree call.
- Routers are mounted in `create_app` only as each feature is implemented.
