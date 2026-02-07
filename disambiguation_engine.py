# =========================
# MIRA BASE – DISAMBIGUATION ENGINE
# =========================
#
# Responsibilities:
# - resolve conflicts between multiple intents
# - choose the most reasonable interpretation
# - ask for clarification ONLY if necessary
#
# Philosophy:
# - if it can be reasonably interpreted → DO IT
# - clarify only when no dominant intent exists

from typing import Dict, Any, List


# Priority = human common sense
_INTENT_PRIORITY = {
    "ARITHMETIC": 100,
    "TIME_NOW": 90,
    "DAY_TODAY": 85,
    "DATE_TODAY": 80,
    "SMALLTALK_STATE": 40,
    "GREETING": 10,
    "THANKS": 5,
    "UNKNOWN": 0,
}


def resolve_disambiguation(attention: Dict[str, Any]) -> Dict[str, Any]:
    primary = attention.get("primary_intent")
    secondary: List[str] = attention.get("secondary_intents", [])
    ranked: List[str] = attention.get("ranked_intents", [])

    # If only one intent → no ambiguity
    if len(ranked) <= 1:
        return {
            "decision": "OK",
            "resolved_intent": primary,
        }

    # Pick the highest priority intent
    best = max(ranked, key=lambda x: _INTENT_PRIORITY.get(x, 0))

    best_score = _INTENT_PRIORITY.get(best, 0)

    # Check if there is another intent with equal priority
    competitors = [
        i for i in ranked
        if i != best and _INTENT_PRIORITY.get(i, 0) == best_score
    ]

    # True ambiguity only if two equal, high-priority intents
    if competitors and best_score >= 50:
        return {
            "decision": "CLARIFY",
            "reason": "AMBIGUOUS_INTENT",
            "candidates": [best] + competitors,
        }

    # Otherwise: interpret reasonably
    return {
        "decision": "OK",
        "resolved_intent": best,
    }
