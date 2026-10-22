"""Create the collections listed in firestore_settings.py if they are missing.

A collection that already holds any document is left untouched.
Run from the repo root: .\\env\\Scripts\\python.exe tools\\infra\\firestore_setup.py
"""

import os

import firebase_admin
import firestore_settings as settings
from firebase_admin import credentials, firestore
from google.api_core.exceptions import AlreadyExists
from google.cloud.firestore import Client


def connect() -> Client:
    cred = credentials.Certificate(os.environ[settings.CREDS_ENV_VAR])
    firebase_admin.initialize_app(cred)
    return firestore.client(database_id=settings.DATABASE_ID)


def ensure_collection(db: Client, name: str) -> str:
    collection = db.collection(name)
    if collection.limit(1).get():
        return "exists, left unchanged"
    try:
        # create() fails instead of overwriting, so a concurrent writer is never clobbered.
        collection.document(settings.MARKER_DOC_ID).create(
            {"created_by": "firestore_setup","created_at": firestore.SERVER_TIMESTAMP}
        )
    except AlreadyExists:
        return "exists, left unchanged"
    return "created"


def main() -> None:
    db = connect()
    print(f"Database: {settings.DATABASE_ID}")
    for name in settings.COLLECTIONS:
        print(f"{name}: {ensure_collection(db, name)}")


if __name__ == "__main__":
    main()
