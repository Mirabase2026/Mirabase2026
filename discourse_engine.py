# =========================
# MIRA BASE – DISCOURSE ENGINE
# =========================
#
# Responsibilities:
# - render text from semantic payload
# - NO decision making
# - NO emotion logic
#

from typing import Dict, Any


def render_social(payload: Dict[str, Any]) -> str:
    """
    Deterministic social responses.
    """
    value = payload.get("value", {})
    intent = value.get("intent")

    if intent == "GREETING":
        return "Ahoj."

    return "Promiň, ale tohle nevím."


def render(payload: Dict[str, Any]) -> str:
    kind = payload.get("kind")

    if kind == "SOCIAL":
        return render_social(payload)

    # fallback for other kinds handled elsewhere
    return "Promiň, ale tohle nevím."
