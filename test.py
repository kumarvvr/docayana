import getpass
import os

import firebase_admin
from firebase_admin import credentials, firestore
import tools.infra.firestore_settings as firestoresettings
CREDS_ENV_VAR = firestoresettings.CREDS_ENV_VAR

cred = credentials.Certificate(os.environ[CREDS_ENV_VAR])
print(cred)
firebase_admin.initialize_app(cred)
db = firestore.client()

print([c.id for c in db.collections()])
