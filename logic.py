# logic.py

memory = {
    "messages": []
}

def handle_message(text: str) -> dict:
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
        "reply": reply,
        "count": len(memory["messages"])
    }

def get_history():
    return memory["messages"]

def clear_memory():
    memory["messages"].clear()
