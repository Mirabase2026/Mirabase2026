from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from logic import save_message, read_messages, clear_memory
from pathlib import Path
import json
import os

app = FastAPI(title="Mirabase2026")

# =========================
# KONFIGURACE
# =========================

API_KEY = os.getenv("MIRABASE_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing environment variable MIRABASE_API_KEY")

MEMORY_FILE = Path("memory.json")

# =========================
# Pydantic modely
# =========================

class TextRequest(BaseModel):
    text: str


class IdRequest(BaseModel):
    id: str


# =========================
# Zabezpečení
# =========================

def check_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


# =========================
# ZÁKLADNÍ ENDPOINTY
# =========================

@app.get("/")
def root():
    return {"status": "ok", "app": "Mirabase2026"}


@app.get("/healthz")
def healthz():
    return {"status": "healthy"}


@app.get("/ping")
def ping():
    return {"ping": "pong"}


# =========================
# PAMĚŤ
# =========================

@app.post("/echo")
def echo(
    data: TextRequest,
    _: None = Depends(check_api_key)
):
    save_message("user", data.text)

    reply = "OK, uloženo."
    save_message("assistant", reply)

    return {
        "user": data.text,
        "assistant": reply
    }


@app.get("/history")
def history(
    _: None = Depends(check_api_key)
):
    return {"messages": read_messages()}


@app.post("/memory/mark_long")
def mark_long(
    data: IdRequest,
    _: None = Depends(check_api_key)
):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        mem = json.load(f)

    for m in mem["messages"]:
        if m["id"] == data.id:
            m["memory_type"] = "long"
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(mem, f, indent=2, ensure_ascii=False)
            return {"status": "ok", "id": data.id}

    raise HTTPException(status_code=404, detail="Message not found")


@app.get("/memory/long")
def get_long_memory(
    _: None = Depends(check_api_key)
):
    messages = read_messages()
    long_messages = [m for m in messages if m.get("memory_type") == "long"]
    return {"messages": long_messages}


@app.post("/memory/note")
def add_note(
    data: TextRequest,
    _: None = Depends(check_api_key)
):
    save_message("assistant", data.text)

    messages = read_messages()
    messages[-1]["memory_type"] = "long"

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"messages": messages}, f, indent=2, ensure_ascii=False)

    return {"status": "ok", "stored_as": "long"}


@app.post("/memory/clear")
def memory_clear(
    _: None = Depends(check_api_key)
):
    clear_memory()
    return {"status": "cleared"}

