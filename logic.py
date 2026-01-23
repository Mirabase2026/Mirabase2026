# logic.py

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
from opinion_engine import run as run_opinion_engine

from behavior import route as behavior_route
from intent_router import route_intent

from decision import (
    decide,
    DecisionResult,
    RESPOND,
    VERIFY,
    SUMMARIZE,
    DO_NOTHING,
    STORE_LONG,
)

# =========================
# FILE PATHS
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


# =========================
# EXECUTION LOG
# =========================

def log_step(action: str, status: str, details: Dict | None = None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "status": status,
        "details": details
    }

    with open(EXECUTION_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# =========================
# PIPELINE (BRAIN)
# =========================

def run_pipeline(
    user_text: str,
    session: str = "cli",
    source: str = "cli"
) -> Dict[str, Any]:

    # 0) BEHAVIOR (reflex / social / intent)
    behavior = behavior_route(user_text)

    if behavior is not None:
        routed = None

        if behavior.get("action") == "INTENT":
            routed = route_intent(behavior.get("intent"))

        return {
            "response": behavior.get("response"),
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

    # -------------------------
    # DECISION LAYER
    # -------------------------

    error = None
    response = None
    memory_read = []
    memory_write = None

    recent_messages = read_messages()
    memory_read.append("short")

    log_step("DECISION", "start", {"text": user_text})
    decision: DecisionResult = decide(user_text, recent_messages)

    log_step(
        "DECISION",
        "ok",
        {
            "action": decision.action,
            "reflex_type": decision.reflex_type,
            "memory_action": decision.memory_action,
        }
    )

    if decision.action != DO_NOTHING:
        save_message("user", user_text)
        memory_write = "short"

    if decision.action == DO_NOTHING:
        response = None

    elif decision.action in (RESPOND, VERIFY, SUMMARIZE):
        response = f"[{decision.action.upper()} – odpověď zatím vypnuta]"
        save_message("assistant", response)
        memory_write = "short"

    elif decision.action == STORE_LONG:
        response = "[ULOŽENÍ DO LONG – zatím pouze kandidát]"
        memory_write = "candidate_long"

    else:
        error = "unknown_action"
        log_step("PIPELINE", "error", {"error": error})

    return {
        "response": response,
        "decision": {
            "action": decision.action,
            "reflex_type": decision.reflex_type,
            "memory_action": decision.memory_action,
        },
        "memory_read": memory_read,
        "memory_write": memory_write,
        "error": error,
        "pipeline": "DECISION",
    }


# =========================
# CLEAR MEMORY
# =========================

def clear_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"messages": []}, f, ensure_ascii=False, indent=2)

