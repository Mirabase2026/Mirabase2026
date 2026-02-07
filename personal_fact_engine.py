# =========================
# MIRA BASE – PERSONAL FACT ENGINE
# =========================

from typing import Dict, Any, Optional
from ltm import store_fact


def resolve_personal_fact(
    intent: str,
    entities: Dict[str, Any],
    raw_text: str
) -> Optional[Dict[str, Any]]:
    """
    Returns stored fact info if something was stored.
    """

    # jednoduchá pravidla – rozšíříme později
    if intent == "PERSONAL_NAME" and "name" in entities:
        store_fact("name", entities["name"])
        return {"stored": "name"}

    if intent == "PERSONAL_PREFERENCE" and "preference" in entities:
        store_fact("preference", entities["preference"])
        return {"stored": "preference"}

    return None
