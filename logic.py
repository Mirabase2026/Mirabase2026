# logic.py
# Core pipeline with behavior + intent + memory hook (with DEBUG TAGS)

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from behavior import route as behavior_route
from intent_router import route_intent

# =========================
# FILE PATHS
# =========================

MEMORY_FILE = Path("memory.json")

# =========================
# MEMORY (low-level)
# =========================

def _load_memory():
    if not MEMORY_FILE.exists():
        return {"messages": []}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_message(role: str, content: str, tag: str | None = None):
    data = _load_memory()
    data["messages"].append({
        "role": role,
        "content": content,
        "tag": tag,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _save_memory(data)

def read_messages():
    return _load_memory().get("messages", [])

def clear_memory():
    _save_memory({"messages": []})

# =========================
# PIPELINE
# =========================

def run_pipeline(
    user_text: str,
    session: str = "cli",
    source: str = "cli"
) -> Dict[str, Any]:

    behavior = behavior_route(user_text)

    # ---------------------------------
    # BEHAVIOR MATCH
    # ---------------------------------
    if behavior is not None:
        response = behavior.get("response")
        tag = None

        # INTENT → ENGINE
        if behavior.get("action") == "INTENT":
            routed = route_intent(
                behavior.get("intent"),
                user_text
            )
            response = routed.get("response")
            tag = "[ENGINE]"

            if behavior.get("intent") in ("INTENT_EXPLAIN", "INTENT_NOTE") and response:
                save_message(
                    role="assistant",
                    content=response,
                    tag=behavior.get("intent")
                )

        else:
            # reflex / social
            tag = "[REFLEX]"

        if response:
            response = f"{tag} {response}"

        return {
            "response": response,
            "pipeline": "BEHAVIOR",
            "error": None,
        }

    # ---------------------------------
    # FALLBACK → MODEL
    # ---------------------------------
    return {
        "response": "[MODEL] (zatím žádný model nepřipojen)",
        "pipeline": "MODEL",
        "error": None,
    }
