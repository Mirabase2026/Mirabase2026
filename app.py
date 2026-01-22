from fastapi import FastAPI

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
from pydantic import BaseModel

class Echo(BaseModel):
    text: str

@app.post("/echo")
def echo(data: Echo):
    return {"you_sent": data.text}
