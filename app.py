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

from datetime import datetime

@app.get("/dashboard")
def dashboard(
    _: None = Depends(check_api_key)
):
    messages = read_messages()

    total = len(messages)
    short_count = sum(1 for m in messages if m.get("memory_type") == "short")
    long_count = sum(1 for m in messages if m.get("memory_type") == "long")

    last_summary = None
    for m in reversed(messages):
        if (
            m.get("memory_type") == "long"
            and isinstance(m.get("content"), str)
            and m["content"].startswith("SHRNUTÍ:")
        ):
            last_summary = {
                "timestamp": m.get("timestamp"),
                "preview": m["content"][:120]
            }
            break

    return {
        "status": "ok",
        "memory": {
            "total": total,
            "short": short_count,
            "long": long_count,
        },
        "last_summary": last_summary
    }

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

@app.post("/memory/summarize")
def summarize_memory(
    _: None = Depends(check_api_key)
):
    messages = read_messages()

    # vezmeme posledních 10 zpráv
    last_messages = messages[-10:]

    if not last_messages:
        raise HTTPException(status_code=400, detail="No messages to summarize")

    # jednoduché „shrnutí“ – jen slepený text
    summary_text = " | ".join(
        f"{m['role']}: {m['content']}" for m in last_messages
    )

    # uložíme jako long-term poznámku
    save_message("assistant", f"SHRNUTÍ: {summary_text}")

    # označíme poslední zprávu jako long
    messages = read_messages()
    messages[-1]["memory_type"] = "long"

    from pathlib import Path
    import json
    with open(Path("memory.json"), "w", encoding="utf-8") as f:
        json.dump({"messages": messages}, f, indent=2, ensure_ascii=False)

    return {"status": "ok", "summarized_messages": len(last_messages)}

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

from datetime import datetime, timezone, timedelta

@app.post("/memory/cleanup")
def cleanup_memory(
    days: int = 7,
    _: None = Depends(check_api_key)
):
    messages = read_messages()
    if not messages:
        return {"status": "ok", "deleted": 0}

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    kept = []
    deleted = 0

    for m in messages:
        if m.get("memory_type") == "long":
            kept.append(m)
            continue

        ts = m.get("timestamp")
        if not ts:
            kept.append(m)
            continue

        try:
            msg_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            kept.append(m)
            continue

        if msg_time >= cutoff:
            kept.append(m)
        else:
            deleted += 1

    # zapiš zpět
    import json
    from pathlib import Path
    with open(Path("memory.json"), "w", encoding="utf-8") as f:
        json.dump({"messages": kept}, f, indent=2, ensure_ascii=False)

    return {"status": "ok", "deleted": deleted}

@app.post("/memory/clear")
def memory_clear(
    _: None = Depends(check_api_key)
):
    clear_memory()
    return {"status": "cleared"}

