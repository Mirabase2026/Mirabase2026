# =========================
# MIRA BASE – EMOTION ENGINE
# =========================
#
# Purpose:
# - classify interaction state
# - NEVER influence logic
# - NEVER generate text

from typing import Dict, Any


def resolve_emotion(attention: Dict[str, Any]) -> Dict[str, Any]:
    primary_intent = attention.get("primary_intent")

    # default
    emotion = "NEUTRAL"
    confidence = 0.7

    if primary_intent in ("GREETING", "THANKS"):
        emotion = "POSITIVE"
        confidence = 0.8

    elif primary_intent in ("UNKNOWN",):
        emotion = "CONFUSED"
        confidence = 0.9

    return {
        "emotion_state": emotion,
        "confidence": confidence,
    }
