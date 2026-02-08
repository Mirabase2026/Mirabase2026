# ltm.py
# =========================
# MIRA BASE – LTM v2.2 (BACKWARD COMPATIBLE)
# =========================

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


# -------------------------------------------------
# PATHS
# -------------------------------------------------
MEMORY_FILE = Path("memory.json")


def _profile_path(user_id: str) -> Path:
    return Path("users") / user_id / "profile.json"


# -------------------------------------------------
# LTM CORE
# -------------------------------------------------
def load_ltm(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Backward compatible:
    - load_ltm() -> full LTM
    - load_ltm(user_id) -> user-specific LTM
    """
    if not MEMORY_FILE.exists():
        data = {"ltm": {}}
    else:
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {"ltm": {}}
        except Exception:
            data = {"ltm": {}}

    if user_id is None:
        return data

    return data.get("ltm", {}).get(user_id, {})


def save_ltm(data: Dict[str, Any]) -> None:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def upsert_fact(user_id: str, key: str, value: Any) -> None:
    """
    Legacy API – used by personal_fact_engine
    """
    data = load_ltm()
    data.setdefault("ltm", {})
    data["ltm"].setdefault(user_id, {})
    data["ltm"][user_id][key] = value
    save_ltm(data)


# -------------------------------------------------
# PREFERENCES WRITE (v2)
# -------------------------------------------------
def set_preference(user_id: str, key: str, value: Any) -> bool:
    path = _profile_path(user_id)

    if not path.exists():
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        if not isinstance(profile, dict):
            return False

        profile[key] = value

        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

        return True
    except Exception:
        return False


def set_preferences(user_id: str, updates: Dict[str, Any]) -> bool:
    if not isinstance(updates, dict):
        return False

    ok = True
    for k, v in updates.items():
        ok = ok and set_preference(user_id, k, v)
    return ok
