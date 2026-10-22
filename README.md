# docayana

A high-performance REST API for trees of nodes of any width and depth. Each node has a type that supplies default properties, users can add their own properties, and data is stored in AWS DynamoDB behind user authentication.

Status: fresh start. The app is a single FastAPI file with a health check.

## Run locally

Requires Python 3.13+.

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
pip install "fastapi[standard]"
fastapi dev main.py
```

Then open http://127.0.0.1:8000/healthz or the interactive docs at http://127.0.0.1:8000/docs.

## Project docs

- [docs/scope.md](docs/scope.md): product scope, v1 features and DynamoDB access patterns
- [docs/adr/](docs/adr/): accepted architecture decisions
