import json
import uuid
from datetime import datetime
from pathlib import Path

MEMORY_FILE = Path("memory.json")


def _load_memory():
    if not MEMORY_FILE.exists():
        return {"messages": []}

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_message(text: str, session: str = "default"):
    data = _load_memory()

    message = {
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": text,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tags": ["input"],
        "session": session
    }

    data["messages"].append(message)
    _save_memory(data)

    return message


def read_messages(session: str = "default"):
    data = _load_memory()
    return [m for m in data["messages"] if m.get("session") == session]


def clear_memory():
    _save_memory({"messages": []})
