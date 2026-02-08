# =========================
# MIRA BASE – SHORT TERM MEMORY (STM v2)
# =========================
#
# Scope:
# - per-user isolation
# - FIFO buffer with fixed limit
# - meaning-only (no text, no facts, no emotion)
#

from __future__ import annotations

from typing import Dict, Any, List, Optional

# In-memory store
_STM: Dict[str, List[Dict[str, Any]]] = {}


# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------
def clear_all() -> None:
    _STM.clear()


def clear_user(user_id: str) -> None:
    if user_id in _STM:
        _STM[user_id] = []


def append_entry(entry: Dict[str, Any], limit: int = 10) -> None:
    """
    Appends a single STM entry for a user.
    Enforces FIFO with fixed limit.
    """
    user_id = entry.get("user_id")
    if not isinstance(user_id, str) or not user_id:
        return

    bucket = _STM.get(user_id)
    if not isinstance(bucket, list):
        bucket = []

    bucket.append(entry)

    # FIFO trim
    if isinstance(limit, int) and limit > 0:
        excess = len(bucket) - limit
        if excess > 0:
            bucket = bucket[excess:]

    _STM[user_id] = bucket


def get_last(user_id: str, n: int) -> List[Dict[str, Any]]:
    """
    Returns last n entries for user (chronological order).
    """
    if not isinstance(user_id, str) or not user_id:
        return []

    bucket = _STM.get(user_id)
    if not isinstance(bucket, list) or not bucket:
        return []

    if not isinstance(n, int) or n <= 0:
        return []

    return bucket[-n:]
