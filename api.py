# api.py
# =========================
# MIRA BASE – API LAYER
# =========================
# Minimal FastAPI wrapper
# Brain + Execution already tested via Golden Tests
# This file only exposes HTTP interface

from fastapi import FastAPI
from pydantic import BaseModel

import logic
import execution_layer


app = FastAPI(title="MiraBase API", version="1.0")


# --------
# Schemas
# --------

class InputRequest(BaseModel):
    text: str


class OutputResponse(BaseModel):
    output: str


# --------
# Routes
# --------

@app.post("/run", response_model=OutputResponse)
def run_text(req: InputRequest):
    contract = logic.run(req.text)
    output_text = execution_layer.render(contract)
    return OutputResponse(output=output_text)


@app.get("/health")
def health():
    return {"status": "ok"}
