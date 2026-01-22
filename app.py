from fastapi import FastAPI, Header, HTTPException, Depends
from logic import save_message, read_messages, clear_memory
import json
from pathlib import Path

app = FastAPI(title="Mirabase2026")

API_KEY = "mirabase"
MEMORY_FILE = Path("memory.json")


def check_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/")
def root():
    return {"status": "ok", "app": "Mirabase2026"}


@app.get("/healthz")
def healthz():
    return {"status": "healthy"}


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.post("/echo")
def echo(
    data: dict,
    _: None = Depends(check_api_key)
):
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' field")

    save_message("user", text)
    reply = "OK, uloženo."
    save_message("assistant", reply)

    return {"user": text, "assistant": reply}


@app.get("/history")
def history(
    _: None = Depends(check_api_key)
):
    return {"messages": read_messages()}


@app.post("/memory/mark_long")
def mark_long(
    data: dict,
    _: None = Depends(check_api_key)
):
    message_id = data.get("id")
    if not message_id:
        raise HTTPException(status_code=400, detail="Missing 'id'")

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        mem = json.load(f)

    found = False
    for m in mem["messages"]:
        if m["id"] == message_id:
            m["memory_type"] = "long"
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Message not found")

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)

    return {"status": "ok", "id": message_id, "memory_type": "long"}


@app.post("/memory/clear")
def memory_clear(
    _: None = Depends(check_api_key)
):
    clear_memory()
    return {"status": "cleared"}



