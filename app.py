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

    for m in mem["messages"]:
        if m["id"] == message_id:
            m["memory_type"] = "long"
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(mem, f, indent=2, ensure_ascii=False)
            return {"status": "ok", "id": message_id}

    raise HTTPException(status_code=404, detail="Message not found")

@app.post("/memory/note")
def add_note(
    data: dict,
    _: None = Depends(check_api_key)
):
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' field")

    # uložíme poznámku rovnou jako long-term
    save_message("assistant", text)
    
    # přepíšeme poslední zprávu na long
    messages = read_messages()
    messages[-1]["memory_type"] = "long"

    # zapíšeme zpět
    from pathlib import Path
    import json
    with open(Path("memory.json"), "w", encoding="utf-8") as f:
        json.dump({"messages": messages}, f, indent=2, ensure_ascii=False)

    return {"status": "ok", "stored_as": "long"}

@app.post("/memory/clear")
def memory_clear(
    _: None = Depends(check_api_key)
):
    clear_memory()
    return {"status": "cleared"}

@app.get("/memory/long")
def get_long_memory(
    _: None = Depends(check_api_key)
):
    messages = read_messages()
    long_messages = [m for m in messages if m.get("memory_type") == "long"]
    return {"messages": long_messages}
