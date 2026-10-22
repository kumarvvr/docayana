# 0002. Tree storage in DynamoDB

Status: accepted
Date: 2026-10-17

## Context
Trees have no depth or width limit, moves must be cheap, and reads must meet the latency targets in `docs/scope.md`. DynamoDB sort keys are capped at 1 KB and items at 400 KB.

## Decision
Use an **adjacency list with child-edge items** in the single table, with `w` = workspace, `n` = node, `p` = parent, `u` = user:

| Item | PK | SK |
| --- | --- | --- |
| Node | `WS#w#NODE#n` | `NODE` |
| Child edge (name and type copied in) | `WS#w#NODE#p` | `CHILD#<position>#n` |
| Root edge | `WS#w#NODE#ROOT` | `CHILD#<position>#n` |
| Membership | `WS#w` | `MEMBER#u`, plus `GSI1PK=USER#u`, `GSI1SK=WS#w` |
| Workspace definition | `WS#w` | `PROPDEF#<key>` or `TYPE#<name>` |
| Idempotency record | `WS#w#IDEM#<key>` | `IDEM`, with `ttl` |

- Sibling `position` is a fractional index string (`domain/positions.py`), so inserting between siblings never renumbers.
- Create and move are `transact_write_items` over the node and its edges, with `version = :expected` on the node.
- Subtree reads walk edges level by level, capped at depth 10 and 1,000 nodes per page. Ancestors walk `parent_id`.
- The table gets one GSI, `GSI1` (`GSI1PK`, `GSI1SK`), for "my workspaces".

## Consequences
- Get, list children, update and move each touch at most three items, at any depth.
- Whole-subtree reads cost one query per node per level; very deep reads are slower, which is why they are capped.
- Rejected: materialized paths (break past ~1 KB of path and rewrite every descendant on move) and closure tables (writes grow with depth).
- Action: add `GSI1` to `TABLE_DEFINITION` in `infrastructure/dynamodb/table.py`; it is missing today.
- Settles scope open questions 2 (user-defined sibling order) and 3 (no unbounded subtree reads).
