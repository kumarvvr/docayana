# 0006. AWS configuration and credentials

Status: accepted
Date: 2026-10-17

## Context
Kumar asked for DynamoDB access configured from system environment variables. The latency target (p99 under 50 ms) and secret handling constrain how the client is built.

## Decision
- **Region is required.** It is read from `DOCAYANA_AWS_REGION`, then `AWS_REGION`, then `AWS_DEFAULT_REGION`; there is no default, so startup fails without one.
- **Credentials never pass through `Settings`.** boto3's default chain supplies them (environment variables, `AWS_PROFILE`, or an IAM role). Startup stops with `AwsCredentialsMissing` if none are found.
- Production runs with an **IAM role** and no access keys.
- The endpoint can be overridden with `DOCAYANA_DYNAMODB_ENDPOINT_URL` or `AWS_ENDPOINT_URL_DYNAMODB` for DynamoDB Local; blank means real AWS.
- The client uses a 2 s connect timeout, 5 s read timeout and standard retries with 3 attempts, instead of botocore's 60 s defaults.
- Tests clear every `AWS_*` and `DOCAYANA_*` variable and never reach real AWS.

## Consequences
- A misconfigured machine fails at startup with a clear message instead of on the first request.
- The runtime role needs `dynamodb:DescribeTable` for `/readyz`, plus the item permissions on the table and its GSI.
- Implemented in `infrastructure/settings.py` and `infrastructure/dynamodb/table.py`.
