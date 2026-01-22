from fastapi import FastAPI
memory = {}

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


@ app.post("/echo")
def echo(data: dict):
    memory["last"] = data["text"]
    return {"you_sent": data["text"]}
@ app.get("/last")
def last():
    return {"last_message": memory.get("last")}
