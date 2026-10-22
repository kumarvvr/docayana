"""The only module that knows how to open Firestore; swap the datastore here."""

from collections.abc import Iterator
from contextlib import contextmanager

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client

from docayana.settings import Settings

APP_NAME = "docayana"


@contextmanager
def firestore_client(settings: Settings) -> Iterator[Client]:
    # A named app keeps us clear of any default app another library may have initialised.
    app = firebase_admin.initialize_app(
        credentials.Certificate(settings.gcp_creds), name=APP_NAME
    )
    try:
        yield firestore.client(app=app, database_id=settings.firestore_database)
    finally:
        firebase_admin.delete_app(app)
