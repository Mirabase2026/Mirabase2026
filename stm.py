# =========================
# MIRA BASE – SHORT TERM MEMORY
# =========================
#
# Responsibilities:
# - keep short-term interaction signals
# - expose minimal recent history for meta-cognition
#

from typing import Dict, Any, Optional, List

_STM: Optional[Dict[str, Any]] = None
_HISTORY_LIMIT = 5


def update_stm(result: Dict[str, Any]) -> None:
    global _STM

    if _STM is None:
        _STM = {
            "last_intents": [],
            "last_actions": [],
            "last_entities": {},
            "history": [],
        }

    # --- history (for META) ---
    entry = {
        "pipeline": result.get("pipeline"),
        "actions": result.get("actions", []),
    }

    _STM["history"].append(entry)
    if len(_STM["history"]) > _HISTORY_LIMIT:
        _STM["history"] = _STM["history"][-_HISTORY_LIMIT:]

    # --- existing FACT behavior preserved ---
    if result.get("pipeline") == "FACT":
        _STM["last_intents"] = [result.get("intent")]
        _STM["last_actions"] = result.get("actions", [])
        _STM["last_entities"] = result.get("entities", {})


def get_stm() -> Optional[Dict[str, Any]]:
    return _STM
