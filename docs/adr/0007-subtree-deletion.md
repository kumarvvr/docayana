# 0007. Subtree deletion

Status: accepted
Date: 2026-10-17

## Context
A subtree can hold any number of nodes, but `transact_write_items` is capped at 100 items and a delete request must stay fast.

## Decision
- `DELETE /nodes/{id}` marks the node deleted and removes its edge from the parent in one transaction, then returns 204. The subtree is unreachable from that moment.
- A background job (`PurgeDeletedSubtree`) walks the subtree and deletes descendants and their edges in batches. It is safe to retry.
- Reads treat a node marked deleted as not found.

## Consequences
- Deletes are fast at any size, but storage is freed later.
- How the purge runs is open until the deployment ADR: a DynamoDB Streams-triggered Lambda or an in-process worker.
