"""Entry point: `fastapi dev main.py` or `uvicorn main:app`."""

from docayana.app import create_app
from docayana.machine import machine_name
from docayana.settings import Settings

print(f"Running on machine: {machine_name()}")

app = create_app(Settings())
