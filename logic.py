# logic.py
# Core pipeline with behavior + intent + memory hook (stable)

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

    # ---------------------------------
    # 0) BEHAVIOR (reflex / social / intent)
    # ---------------------------------
    behavior = behavior_route(user_text)

    if behavior is not None:
        routed = None
        response = behavior.get("response")

        # -----------------------------
        # INTENT → ENGINE
        # -----------------------------
        if behavior.get("action") == "INTENT":
            routed = route_intent(
                behavior.get("intent"),
                user_text
            )
            response = routed.get("response")

            # -------------------------
            # MEMORY HOOK (C)
            # -------------------------
            if behavior.get("intent") in ("INTENT_EXPLAIN", "INTENT_NOTE") and response:
                save_message(
                    role="assistant",
                    content=response,
                    tag=behavior.get("intent")
                )

        return {
            "response": response,
            "decision": {
                "action": behavior.get("action"),
                "intent": behavior.get("intent"),
                "routed": routed,
                "source": behavior.get("source"),
            },
            "memory_read": [],
            "memory_write": behavior.get("intent")
            if behavior.get("intent") in ("INTENT_EXPLAIN", "INTENT_NOTE")
            else None,
            "error": None,
            "pipeline": "BEHAVIOR",
        }

    # ---------------------------------
    # FALLBACK (should not happen now)
    # ---------------------------------
    return {
        "response": None,
        "decision": None,
        "memory_read": [],
        "memory_write": None,
        "error": "no_behavior_match",
        "pipeline": "NONE",
    }
