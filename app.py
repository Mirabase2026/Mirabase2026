from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
import os

from logic import run_pipeline

app = FastAPI(title="Mirabase2026")

API_KEY = os.getenv("MIRABASE_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing environment variable MIRABASE_API_KEY")


class TextRequest(BaseModel):
    text: str


def check_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/")
def root():
    return {"status": "ok", "app": "Mirabase2026"}


@app.get("/healthz")
def healthz():
    return {"status": "healthy"}


@app.post("/echo")
def echo(
    data: TextRequest,
    _: None = Depends(check_api_key)
):
    result = run_pipeline(data.text)
    return {
        "assistant": result.get("response"),
        "pipeline": result.get("pipeline"),
    }
