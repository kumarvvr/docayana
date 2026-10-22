"""Inputs for firestore_setup.py. Every value is a plain string."""

# Name of the env var holding the path to the service-account key file.
CREDS_ENV_VAR = "DOCAYANA_GCP_CREDS"

DATABASE_ID = "(default)"

# Firestore only lists a collection once it holds a document, so each new
# collection gets this placeholder document.
MARKER_DOC_ID = "_meta"

# Placeholders until the real collection names are decided; replace them.
COLLECTIONS = (
    "workspaces",
    "nodes",
    "catalog",
)
