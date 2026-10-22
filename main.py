from fastapi import FastAPI

app = FastAPI(title="docayana")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
