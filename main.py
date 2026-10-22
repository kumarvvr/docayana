"""Entry point: `fastapi dev main.py` or `uvicorn main:app`."""

from docayana.app import create_app
from docayana.settings import Settings

app = create_app(Settings())
