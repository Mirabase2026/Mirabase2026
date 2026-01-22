from fastapi import FastAPI, Header, HTTPException
from logic import handle_message, get_history, clear_memory


app = FastAPI()
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
def echo(data: dict, x_api_key: str = Header(None)):
    check_api_key(x_api_key)

    text = data["text"]
    result = handle_message(text)

    return {
        "you_sent": text,
        "reply": result["reply"],
        "count": result["count"]
    }
@app.get("/history")
def history(x_api_key: str = Header(None)):
    check_api_key(x_api_key)

    return {
        "messages": get_history()
    }
@app.post("/memory/clear")
def memory_clear(x_api_key: str = Header(None)):
    check_api_key(x_api_key)

    clear_memory()
    return {"status": "cleared", "count": 0}

