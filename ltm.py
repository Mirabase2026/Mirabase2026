# =========================
# MIRA BASE – LONG TERM MEMORY (LTM)
# =========================
#
# Responsibilities:
# - load and persist long-term memory
# - expose PERSONAL FACTS separately from message history
#
# This module is the single source of truth for memory.json structure.
#
# Backward compatible:
# - provides store_fact() expected by personal_fact_engine.py

import json
from pathlib import Path
from typing import Dict, Any

MEMORY_FILE = Path("memory.json")


def load_ltm() -> Dict[str, Any]:
    """
    Loads PERSONAL FACTS from memory.json.

    Expected structure:
    {
      "personal": {...},
      "messages": [...]
    }

    Returns ONLY the personal dict.
    """
    if not MEMORY_FILE.exists():
        return {}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}

    personal = data.get("personal")
    if isinstance(personal, dict):
        return personal

    return {}


def save_personal_fact(key: str, value: Any) -> None:
    """
    Persist a single personal fact into memory.json.
    """
    data: Dict[str, Any] = {}

    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    if not isinstance(data, dict):
        data = {}

    personal = data.get("personal")
    if not isinstance(personal, dict):
        personal = {}

    personal[key] = value
    data["personal"] = personal

    # ensure messages key exists
    if "messages" not in data or not isinstance(data["messages"], list):
        data["messages"] = []

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -------------------------------------------------
# BACKWARD COMPATIBILITY
# -------------------------------------------------
def store_fact(key: str, value: Any) -> None:
    """
    Alias for legacy imports.
    """
    save_personal_fact(key, value)
