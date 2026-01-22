from fastapi import FastAPI
memory = {
    "messages": []
}


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
    memory["messages"].append(text)

    if len(memory["messages"]) == 1:
        reply = "Ahoj! To je naše první zpráva 🙂"
    else:
        reply = f"Už jsme si psali. Toto je zpráva číslo {len(memory['messages'])}."

    return {
        "you_sent": text,
        "reply": reply,
        "count": len(memory["messages"])
    }

 


@app.get("/last")
def last():
    if not memory["messages"]:
        return {"last_message": None}
    return {"last_message": memory["messages"][-1]}

@app.get("/history")
def history():
    return {
        "messages": memory["messages"]
    }
