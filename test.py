import os

import firebase_admin
from firebase_admin import credentials, firestore

CREDS_ENV_VAR = "DOCAYANA_GCP_CREDS"

cred = credentials.Certificate(os.environ[CREDS_ENV_VAR])
firebase_admin.initialize_app(cred)
db = firestore.client()

print([c.id for c in db.collections()])
