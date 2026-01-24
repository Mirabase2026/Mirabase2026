# logic.py
# Core pipeline with behavior + intent + memory hook (with DEBUG TAGS)

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from behavior import route as behavior_route
from intent_router import route_intent

MEMORY_FILE = Path("memory.json")

LAST_ASSISTANT_RESPONSE: str | None = None


def _load_memory():
    if not MEMORY_FILE.exists():
        return {"messages": []}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_pipeline(user_text: str) -> Dict[str, Any]:
    global LAST_ASSISTANT_RESPONSE

    behavior = behavior_route(user_text)

    if behavior is not None:
        response = behavior.get("response")
        tag = None

        if behavior.get("action") == "INTENT":
            routed = route_intent(
                behavior.get("intent"),
                user_text,
                LAST_ASSISTANT_RESPONSE,
            )
            response = routed.get("response")
            tag = "[ENGINE]"
        else:
            tag = "[REFLEX]"

        if response:
            response = f"{tag} {response}"
            LAST_ASSISTANT_RESPONSE = response

        return {
            "response": response,
            "pipeline": "BEHAVIOR",
            "error": None,
        }

    response = "[MODEL] (zatím žádný model nepřipojen)"
    LAST_ASSISTANT_RESPONSE = response

    return {
        "response": response,
        "pipeline": "MODEL",
        "error": None,
    }
