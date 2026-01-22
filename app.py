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

    text_lower = text.lower()

if any(word in text_lower for word in ["ahoj", "čau", "nazdar"]):
    reply = "Ahoj! Rád tě vidím 🙂"
elif "jak se máš" in text_lower:
    reply = "Mám se fajn, díky! A ty?"
elif len(memory["messages"]) == 1:
    reply = "To je naše první zpráva 🙂"
else:
    reply = f"Rozumím. Toto je zpráva číslo {len(memory['messages'])}."


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
