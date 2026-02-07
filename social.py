# social.py
# =========================
# MIRA BASE – SOCIAL (v1)
# =========================
#
# Responsibilities:
# - deterministic social decisions
# - returns semantic dict (NO user-facing text)

from __future__ import annotations

import re
from typing import Optional, Dict, Any


_GREET_RE = re.compile(r"^(ahoj|cau|čau|dobry den|dobrý den|zdravim|zdravím)\b", re.IGNORECASE)
_ASK_RE = re.compile(r"\b(co|jak|kde|kdy|proc|proč|kolik)\b", re.IGNORECASE)


def handle(user_text: str) -> Optional[Dict[str, Any]]:
    t = "" if user_text is None else str(user_text).strip()
    if not t:
        return None

    if _GREET_RE.search(t):
        if _ASK_RE.search(t):
            return {"key": "HELLO_ASK"}
        return {"key": "HELLO"}

    return None
