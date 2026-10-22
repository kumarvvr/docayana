---
name: product-scope
description: Docayana's product scope (node trees of arbitrary width and depth, typed and custom properties, file-based catalog, workspaces and auth) and its architecture decisions. Use when designing or building a feature, domain model, endpoint, DynamoDB key, auth rule or catalog change, or when judging whether work is in scope.
---

# Product scope

The scope lives in `docs/scope.md`; decisions live in `docs/adr/`. Read both before designing or building anything user-facing. This skill only says how to use them; it does not repeat them.

## How to use the scope
- Read the sections of `docs/scope.md` your task touches. For data access, always read "Access patterns".
- An accepted ADR overrides `docs/scope.md`. Lines marked **Assumption** and the "Open questions" defaults are proposals, not decisions: follow them, but say so when your work depends on one.
- Work listed under "Out of scope for v1" needs Kumar's go-ahead first. Say it is out of scope and ask; don't build it quietly.
- A new access pattern, entity, endpoint family or NFR change means the scope changes: update `docs/scope.md` in the same change, and propose an ADR in `docs/adr/` for anything that alters keys, auth or deployment.

## Vocabulary
Use the scope's terms in code and docs: `Workspace`, `Node`, `NodeType`, `PropertyDefinition`, property value, `Catalog`, child edge. There is no `Document` entity; the `Document` examples in other skills are placeholders.

## Rules that are easy to get wrong
- Type defaults are resolved when a node is read, never copied onto the node.
- Every key starts with the workspace; the workspace in a request is checked against the caller's membership.
- Trees use an adjacency list with child-edge items; no materialized paths, and no `scan`.
- Unbounded reads (children, subtrees, ancestors) are paginated or capped.
- The catalog is a YAML settings file in the repo, loaded once at startup and read from memory.
