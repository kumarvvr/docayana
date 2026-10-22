---
name: dynamodb-coding
description: AWS DynamoDB data modeling and boto3 coding patterns (single-table keys, queries, conditional writes, pagination, errors, local testing). Use when designing tables or writing repository code that talks to DynamoDB.
---

# DynamoDB Coding

## Modeling
- Start from access patterns: list every read/write the API needs before choosing keys.
- Prefer single-table design with generic keys: `PK`, `SK`, plus `GSI1PK`/`GSI1SK` as needed.
  - e.g. `PK=DOC#<id>`, `SK=META`; versions `SK=VER#<zero-padded n>`; by owner `GSI1PK=USER#<id>`, `GSI1SK=DOC#<created_at>`.
- Store an `entity_type` attribute on every item. Keep items well under 400 KB; put large blobs in S3 and store the key.
- Use ISO-8601 UTC strings for sortable timestamps; `ttl` (epoch seconds) for expiring items.

## boto3 patterns
- Create the client/resource once in the composition root and inject the `Table`; set region and retries via `botocore.config.Config(retries={"mode": "standard"})`.
- Never `scan` in request paths; use `query` with `Key("PK").eq(...) & Key("SK").begins_with(...)`.
- Always paginate: loop on `LastEvaluatedKey` / `ExclusiveStartKey`; expose an opaque cursor (base64 JSON) to the API.
- Use `ProjectionExpression` for partial reads, `ConsistentRead=True` only when needed.
- Writes that must not clobber: `ConditionExpression="attribute_not_exists(PK)"`. Optimistic locking: `version` attribute with `ConditionExpression="version = :expected"`.
- Updates: `update_item` with `UpdateExpression` and `ExpressionAttributeNames` (`#name`) to avoid reserved words.
- Multi-item atomicity: `transact_write_items` (max 100 items). Bulk loads: `batch_writer()`; handle `UnprocessedItems` for raw `batch_*` calls.
- Numbers come back as `Decimal`; convert in the mapper, never leak `Decimal` into domain or JSON.

## Errors
```python
from botocore.exceptions import ClientError

try:
    table.put_item(Item=item, ConditionExpression="attribute_not_exists(PK)")
except ClientError as err:
    if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
        raise DocumentAlreadyExists(doc.id) from err
    raise
```
Translate AWS errors into domain/application errors inside the repository; nothing above infrastructure sees `ClientError`.

## Testing
- Unit tests: in-memory fake of the repository port.
- Repository tests: `moto` (`mock_aws`) or DynamoDB Local; create the table in a fixture from the same definition used in IaC.
