from fastapi import FastAPI, Header, HTTPException, Depends
from logic import save_message, read_messages, clear_memory

app = FastAPI(title="Mirabase2026")

API_KEY = "mirabase"


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

    # uložíme vstup uživatele
    save_message("user", text)

    # zatím „hloupá“ odpověď (placeholder)
    reply = "OK, uloženo."

    # uložíme odpověď AI
    save_message("assistant", reply)

    return {
        "user": text,
        "assistant": reply
    }


@app.get("/history")
def history(
    _: None = Depends(check_api_key)
):
    return {
        "messages": read_messages()
    }


@app.post("/memory/clear")
def memory_clear(
    _: None = Depends(check_api_key)
):
    clear_memory()
    return {"status": "cleared"}


