# 0001. Product scope and workspace tenancy

Status: accepted
Date: 2026-10-17

## Context
Kumar defined docayana as a high-performance API for nodes nested to any width and depth. Each node has configurable default properties, users can add their own, a pre-defined catalog ships as a local settings file, data lives in DynamoDB, and users and authentication are required. `docs/scope.md` expands this into v1 features, and open question 1 asks what the isolation boundary is.

## Decision
- Docayana v1 is the node-tree API described in `docs/scope.md` "In scope for v1"; the "Out of scope for v1" list needs Kumar's go-ahead before it is built.
- The **workspace** is the isolation boundary. Every node, edge, membership and custom definition belongs to exactly one workspace, and every DynamoDB key starts with it.
- Users reach a workspace through a membership with a role (ADR-0004). A workspace can hold many root nodes.

## Consequences
- Cross-workspace reads are impossible by key design, not just by code checks.
- Sharing one node with someone outside its workspace is not possible in v1.
- Querying nodes by property value is not in v1.
- Settles scope open questions 1 (workspace boundary) and 4 (no property-value queries in v1).
