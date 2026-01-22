# logic.py

import json
import os

MEMORY_FILE = "memory.json"


# ---------- práce se souborem ----------

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"messages": []}


def save_memory(memory: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


# ---------- inicializace paměti ----------

memory = load_memory()


# ---------- hlavní logika ----------

def handle_message(text: str) -> dict:
    memory["messages"].append(text)
    save_memory(memory)

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


# ---------- pomocné endpointy ----------

def get_history():
    return memory["messages"]


def clear_memory():
    memory["messages"].clear()
    save_memory(memory)

