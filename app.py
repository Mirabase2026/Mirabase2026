from fastapi import FastAPI
from logic import handle_message, get_history, clear_memory


app = FastAPI()

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
def echo(data: dict):
    text = data["text"]
    result = handle_message(text)

    return {
        "you_sent": text,
        "reply": result["reply"],
        "count": result["count"]
    }
@app.get("/history")
def history():
    return {
        "messages": get_history()
    }
@app.post("/memory/clear")
def memory_clear():
    clear_memory()
    return {"status": "cleared", "count": 0}

