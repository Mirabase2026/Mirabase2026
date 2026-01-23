# logic.py
# Core pipeline – clean engine map architecture

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from behavior import route as behavior_route
from intent_router import route_intent

# =========================
# FILES
# =========================

MEMORY_FILE = Path("memory.json")
EXECUTION_LOG_FILE = Path("execution_log.jsonl")

# =========================
# MEMORY (LOW LEVEL)
# =========================

def save_message(role: str, content: str):
    data = {"messages": []}

    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    data["messages"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_messages():
    if not MEMORY_FILE.exists():
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("messages", [])


def clear_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"messages": []}, f, ensure_ascii=False, indent=2)

# =========================
# EXECUTION LOG
# =========================

def log_step(action: str, status: str, details: Dict | None = None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "status": status,
        "details": details,
    }
    with open(EXECUTION_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# =========================
# PIPELINE
# =========================

def run_pipeline(
    user_text: str,
    session: str = "cli",
    source: str = "cli"
) -> Dict[str, Any]:

    # ---------------------------------
    # 0) BEHAVIOR (reflex / social / intent)
    # ---------------------------------
    behavior = behavior_route(user_text)

    if behavior is not None:
        response = behavior.get("response")

        # INTENT → ENGINE ROUTING
        if behavior.get("action") == "INTENT":
            routed = route_intent(
                intent=behavior.get("intent"),
                text=user_text
            )
            response = routed.get("response")
        else:
            routed = None

        return {
            "response": response,
            "decision": {
                "action": behavior.get("action"),
                "intent": behavior.get("intent"),
                "routed": routed,
                "source": behavior.get("source"),
            },
            "memory_read": [],
            "memory_write": None,
            "error": None,
            "pipeline": "BEHAVIOR",
        }

    # ---------------------------------
    # FALLBACK (zatím prázdné)
    # ---------------------------------
    return {
        "response": None,
        "decision": None,
        "memory_read": [],
        "memory_write": None,
        "error": None,
        "pipeline": "EMPTY",
    }
