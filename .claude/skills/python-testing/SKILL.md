---
name: python-testing
description: pytest conventions for this project (test layout, fakes vs mocks, FastAPI TestClient, DynamoDB with moto, fixtures). Use when writing or fixing tests.
---

# Python Testing

## Layout
```
tests/
  unit/          # domain + application, in-memory fakes, no I/O, fast
  integration/   # infrastructure adapters against moto / DynamoDB Local
  api/           # FastAPI TestClient against create_app with overridden dependencies
  conftest.py
```

## Rules
- Name tests by behavior: `test_create_document_rejects_duplicate_id`.
- Arrange-Act-Assert, one behavior per test; parametrize instead of copy-paste (`@pytest.mark.parametrize`).
- Prefer hand-written fakes of ports over `unittest.mock`; mock only at true external boundaries.
- Fixtures in `conftest.py` with the narrowest scope that works; factories for test data (`make_document(**overrides)`).
- API tests: `app.dependency_overrides[get_doc_service] = lambda: fake_service`; assert status code and body schema.
- DynamoDB tests: `with mock_aws():` create the table from the shared definition; set fake AWS creds via env in a fixture.
- No real network or AWS calls; no `sleep`; freeze time when asserting timestamps.
- Run: `pytest -q`; coverage with `pytest --cov=docayana --cov-report=term-missing`. New code ships with tests.
