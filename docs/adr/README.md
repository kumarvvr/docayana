# Architecture decision records

One file per decision: `NNNN-short-title.md`, numbered in order, never renumbered. A superseded ADR stays and links to the one that replaces it.

Template:

```markdown
# NNNN. Title

Status: proposed | accepted | superseded by NNNN
Date: YYYY-MM-DD

## Context
What forces the decision; link the relevant section of docs/scope.md.

## Decision
What we will do, in one or two paragraphs.

## Consequences
What gets easier, what gets harder, what we must now do.
```

| # | Title | Status |
| --- | --- | --- |
| [0001](0001-product-scope-and-workspace-tenancy.md) | Product scope and workspace tenancy | accepted |
| [0002](0002-tree-storage-in-dynamodb.md) | Tree storage in DynamoDB | accepted |
| [0003](0003-node-types-properties-and-catalog.md) | Node types, property definitions and the catalog file | accepted |
| [0004](0004-authentication-and-authorization.md) | Authentication and authorization | accepted |
| [0005](0005-rest-api-surface.md) | REST API surface for nodes | accepted |
| [0006](0006-aws-configuration-and-credentials.md) | AWS configuration and credentials | accepted |
| [0007](0007-subtree-deletion.md) | Subtree deletion | accepted |

Not yet written: deployment target and infrastructure as code (scope open questions 8 and 9), and observability.
