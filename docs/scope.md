# Docayana Project Scope

Status: draft, 2026-10-11. Owner: Kumar. Lines marked **Assumption** and the Open questions table are proposed defaults, not decisions. The ADRs were cleared on 2026-10-22 and will be rebuilt after the research thread; once they exist, an ADR in `docs/adr/` wins over this file. Discussion copy: [Claude Doc](https://claude.ai/code/artifact/7033e6b9-78e9-43e3-8fdc-ebe4b308b02e). This file is the canonical copy for the codebase; update it whenever the scope changes.

## Purpose

Docayana is a high-performance REST API for managing trees of nodes of arbitrary width and depth, where every node carries typed properties, stored in DynamoDB and protected by user authentication.

- Each node has a **type**. The type supplies a set of default properties whose definitions are configurable and can change over time ("fluid").
- Users can add **custom properties** to any node beyond its type's defaults.
- A catalog of **pre-defined node types and property definitions** ships with the service in a local settings file and is loaded at startup.
- Every request is authenticated and every node is owned and access-checked.

## Users and authentication

Authentication is mandatory on every endpoint except `/healthz` and `/readyz`. **Assumption:** users belong to a workspace, the workspace is the isolation boundary, and access is decided by the user's role in that workspace.

| Actor | What they can do | Identified by |
| --- | --- | --- |
| Workspace owner | Everything an editor can, plus manage members, roles and workspace-level custom property definitions | JWT `sub` + workspace membership with role `owner` |
| Editor | Create, move, update and delete nodes and their properties | Role `editor` |
| Viewer | Read nodes, subtrees and properties | Role `viewer` |
| Service client | Machine-to-machine access to one workspace | OAuth client-credentials token scoped to a workspace |
| Platform admin | Edits the pre-defined catalog file and deploys it; no API access to user data | Repo and AWS IAM |

**Assumption:** Amazon Cognito user pools issue the tokens and the API verifies them against Cognito's JWKS. The workspace id is taken from the URL path and checked against the caller's membership, never trusted on its own.

## Core concepts

A node is a typed item in a tree; its effective properties are its type's defaults overlaid with the values set on the node itself.

| Concept | Meaning | Stored in |
| --- | --- | --- |
| Workspace | Isolation boundary that owns trees, members and custom definitions | DynamoDB |
| Node | Id, type, parent id, sibling position, name, property values, `version`, audit fields | DynamoDB item |
| Root node | A node with no parent; a workspace can hold many trees | DynamoDB item |
| Node type | Named template (for example `folder`, `asset`, `location`) listing its default property definitions and which child types it allows | Catalog file, optionally extended per workspace |
| Property definition | Key, data type (string, number, boolean, date, enum, list, object), default value, required flag, validation rules | Catalog file or workspace item |
| Property value | A value set on one node, for a type default or a user-added custom property | Map attribute on the node item |
| Catalog | The pre-defined node types and property definitions, versioned in the repo as a settings file and loaded at startup | YAML file in the repo |

Two rules make the defaults "fluid":

1. **Defaults are resolved on read, never copied into nodes.** Changing a type's default changes every node that has not overridden it, with no data migration.
2. **Custom properties live beside default ones on the node**, validated by their own definition, so a user can extend one node without changing its type.

## In scope for v1

Version 1 delivers authenticated tree CRUD with typed, extensible properties and a file-based catalog.

1. Sign in and call the API with a bearer token; manage workspace members and roles.
2. Create a root node or a child node of a given type; the type's allowed-children rule is enforced.
3. Get a node with its effective properties (defaults resolved), optionally with its own values only.
4. List a node's direct children in sibling order, with cursor pagination.
5. Get a subtree to a requested depth (default 1, capped), paginated.
6. Get a node's ancestors (breadcrumb path to the root).
7. Move a node, with its whole subtree, under a new parent or to a new position among siblings; moving a node under its own descendant is rejected.
8. Update property values and add or remove custom properties, validated against their definitions, with `ETag` / `If-Match` concurrency.
9. Delete a node; its subtree is deleted asynchronously and is invisible immediately.
10. Read the catalog: list node types and property definitions.
11. Idempotent create via the `Idempotency-Key` header.

## Out of scope for v1

These are deferred, not rejected; each would get its own ADR when picked up.

- Querying nodes by property value across a tree ("all assets where status = active"); needs a search index such as OpenSearch.
- Per-node permissions; v1 checks access at the workspace level only.
- Editing node types through the API; v1 types come from the catalog file (see open question 5).
- Node history and undo.
- Links between nodes other than parent and child (a graph, not a tree).
- Binary attachments on nodes.
- Real-time change notifications to clients.
- A web UI; v1 is API only.

## Access patterns

Recommended: an adjacency list. Each node is its own item keyed by id, and each parent holds one small "child edge" item per child, sorted by sibling position. Every v1 operation is then a `get_item`, a `query` or a small transaction, with no `scan`. An ADR will finalize the keys. `w` = workspace id, `n` = node id, `p` = parent id, `u` = user id.

| # | Access pattern | Operation | Proposed keys |
| --- | --- | --- | --- |
| 1 | Get node by id | `get_item` | `PK=WS#w#NODE#n`, `SK=NODE` |
| 2 | List children in order | `query` | `PK=WS#w#NODE#p`, `SK begins_with CHILD#`; edge `SK=CHILD#<position>#n` carries the child's name and type |
| 3 | List root nodes | `query` | Same as 2 with `p=ROOT` |
| 4 | Get subtree to depth k | One `query` per node per level, run in parallel | Pattern 2 repeated; depth and total items capped |
| 5 | Get ancestors | Walk `parent_id` with `get_item` per level | Pattern 1; optional ancestor cache if depth is large |
| 6 | Create child | `transact_write_items` | Put node (`attribute_not_exists`) + put edge under parent |
| 7 | Move or reorder | `transact_write_items` | Delete old edge, put new edge, update node `parent_id` with `version = :expected`; cycle check by walking the new parent's ancestors |
| 8 | Update properties | `update_item` conditional | Pattern 1 with `version = :expected` |
| 9 | Delete subtree | Transaction, then async cleanup | Mark node deleted and remove its edge at once; a background worker deletes descendants |
| 10 | List workspace members / a user's workspaces | `query` / `query` GSI1 | `PK=WS#w`, `SK=MEMBER#u`; `GSI1PK=USER#u`, `GSI1SK=WS#w` |
| 11 | Workspace custom definitions | `query` | `PK=WS#w`, `SK begins_with PROPDEF#` or `TYPE#` |
| 12 | Idempotent create | `put_item` conditional | `PK=WS#w#IDEM#<key>`, `SK=IDEM`, `ttl` 24 h |

Why not a materialized path: a path key would make whole-subtree reads one query, but DynamoDB sort keys cap at 1 KB, which breaks "arbitrary depth", and every move would rewrite every descendant. Sibling `position` is a fractional index string, so inserting between two siblings never renumbers the others.

## Non-functional requirements

"High performance" is proposed below as concrete targets; replace these numbers with real ones when known.

| Area | Proposed target |
| --- | --- |
| Latency | p99 under 50 ms for get node, list children and update; under 300 ms for a 3-level subtree of up to 500 nodes |
| Throughput | 500 requests per second sustained per region, scaling horizontally |
| Tree shape | No limit on depth or children per node; each response is paginated and subtree reads are capped at 1,000 nodes per page |
| Node size | Up to 350 KB of property data per node (DynamoDB item limit is 400 KB) |
| Catalog | Loaded once at startup and cached in memory; a property lookup never hits the database |
| Availability | 99.9% monthly, single AWS region |
| Durability | DynamoDB point-in-time recovery on; on-demand capacity |
| Security | TLS everywhere; DynamoDB encrypted with KMS; every request authenticated; workspace membership checked on every call |
| Observability | Structured JSON logs with request id, user id and workspace id; OpenTelemetry traces; error reporting through Sentry |
| Audit | `created_by`, `updated_by` and timestamps on every node |

## Architecture constraints

These are already fixed by the skeleton in the repo and by CLAUDE.md; the scope must fit within them.

| Constraint | Source |
| --- | --- |
| Python 3.15, FastAPI, Pydantic v2 | `pyproject.toml` |
| Clean architecture: domain, application, infrastructure, api; dependencies point inward | `clean-architecture` skill |
| DynamoDB single-table design with generic `PK`/`SK` keys | `dynamodb-coding` skill, `infrastructure/dynamodb/table.py` |
| REST under `/v1`, problem+json errors, cursor pagination, `ETag`/`If-Match`, `Idempotency-Key` | `rest-api-design` skill |
| Request ids on every request; `/healthz` and `/readyz` probes | `api/request_id.py`, `api/routers/health.py` |
| OpenTelemetry tracing, off by default | `infrastructure/telemetry.py` |
| Config only through `DOCAYANA_` environment variables | `infrastructure/settings.py` |

## Open questions

All questions are open again until the ADRs are rebuilt after the research thread.

| # | Question | Recommended default | What it changes |
| --- | --- | --- | --- |
| 1 | Is the workspace the isolation boundary, or is every tree private to one user? | Workspaces with member roles | Partition keys, auth checks |
| 2 | Do siblings have a user-defined order, or are they sorted by name or date? | User-defined order via fractional index | Child edge sort key |
| 3 | Do clients need whole-subtree reads of very deep trees in one call? | No; depth-capped and paginated | Whether a materialized path or closure table is worth its write cost |
| 4 | Must you query nodes by property value ("all nodes where status = open")? | Not in v1 | A search index or extra GSIs |
| 5 | Can workspace owners define their own node types and property definitions, or only the catalog file? | Catalog file defines types; owners can add workspace-level property definitions | Whether types live only in YAML or also in DynamoDB |
| 6 | When a catalog default changes, should existing nodes see the new default? | Yes, defaults resolve on read | Confirms the "fluid" rule |
| 7 | Which identity provider? | Amazon Cognito user pools | Auth middleware, sign-up flow |
| 8 | Where does it run? | ECS Fargate behind an Application Load Balancer | Latency floor, cost floor, background worker for deletes |
| 9 | Infrastructure as code? | AWS CDK in Python, same repo | Tooling, one language across the repo |

## Next steps

- [ ] Finish the research thread
- [ ] Rebuild the ADRs in `docs/adr/` from its findings
- [ ] Rename the `Document` examples in the skills to `Node`
