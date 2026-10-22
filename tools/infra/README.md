# tools/infra

Scripts for managing docayana's infrastructure (provisioning, connection checks, data seeding, cleanup).
Each tool reads its config from `DOCAYANA_*` environment variables; never hard-code credentials or commit key files.

## Naming
All Firestore infrastructure code lives only in this folder, in files named `firestore_*.py`.

## Tools
- `firestore_setup.py`: creates the collections listed in `firestore_settings.py` if they are missing; existing collections are never modified.
  Run from the repo root: `.\env\Scripts\python.exe tools\infra\firestore_setup.py`
