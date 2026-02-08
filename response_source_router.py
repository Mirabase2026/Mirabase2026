# =========================
# MIRA BASE – RESPONSE SOURCE ROUTER
# =========================
#
# Responsibilities:
# - choose response source deterministically
# - consider actions, attention, entities
# - apply emotion-aware routing (v1)
#
# Sources:
# - DETERMINISTIC
# - SOCIAL
# - FALLBACK
#

from typing import Dict, Any, List, Optional


def _get_emotion(ctx: Dict[str, Any]) -> Optional[str]:
    if isinstance(ctx, dict):
        emo = ctx.get("emotion")
        if isinstance(emo, dict):
            sig = emo.get("emotion_signal")
            if isinstance(sig, str):
                return sig
    return None


def resolve_response_source(
    *,
    actions: List[Any],
    attention: Dict[str, Any],
    entities: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Decide which response source to use.
    Deterministic, emotion-aware (v1).
    """
    emotion = _get_emotion(context)
    primary_intent = attention.get("primary_intent")

    # -------------------------------------------------
    # 1) SOCIAL ROUTE (greetings, social turns)
    # -------------------------------------------------
    if primary_intent == "GREETING":
        # Emotion-aware preference for social handling
        if emotion in ("CALM", "CONFUSED", "ENGAGED"):
            return {"source": "SOCIAL"}

    # -------------------------------------------------
    # 2) DETERMINISTIC FACTS
    # -------------------------------------------------
    if actions:
        # When frustrated, still allow deterministic answers
        return {"source": "DETERMINISTIC"}

    # -------------------------------------------------
    # 3) FALLBACK
    # -------------------------------------------------
    return {"source": "FALLBACK"}
