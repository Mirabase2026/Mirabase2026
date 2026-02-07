# =========================
# MIRA BASE – EPISTEMIC ENGINE (KNOWLEDGE LIMITS)
# =========================
#
# Responsibilities:
# - detect questions that are not knowable by the system
# - do NOT generate text
# - only return epistemic state + reason
#
# Examples:
# - "jak mi je" (user internal state) -> USER_STATE_UNKNOWN
#

from typing import Dict, Any
import re


# User internal state: system cannot know unless user provides it.
_USER_STATE_PATTERNS = [
    r"\bjak\s+(mi|mně)\s+je\b",
    r"\bco\s+(mi|mně)\s+je\b",
    r"\bjak\s+se\s+cítím\b",
    r"\bjak\s+se\s+citím\b",
    r"\bcítím\s+se\s+jak\b",
    r"\bcitim\s+se\s+jak\b",
]


def resolve_epistemic(attention: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    t = (raw_text or "").lower().strip()

    for pat in _USER_STATE_PATTERNS:
        if re.search(pat, t):
            return {
                "epistemic_state": "USER_STATE_UNKNOWN",
                "reason": "USER_INTERNAL_STATE",
            }

    return {
        "epistemic_state": "OK",
        "reason": None,
    }
