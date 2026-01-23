# intent_router.py

def route_intent(intent: str):
    """
    Mapuje intent na další logický krok.
    Zatím žádná AI, žádné odpovědi.
    """

    if intent == "INTENT_EXPLAIN":
        return {
            "next": "EXPLAIN_ENGINE"
        }

    if intent == "INTENT_NOTE":
        return {
            "next": "NOTE_ENGINE"
        }

    if intent == "INTENT_OPINION":
        return {
            "next": "OPINION_ENGINE"
        }

    if intent == "INTENT_CONTINUE":
        return {
            "next": "CONTINUE_ENGINE"
        }

    if intent == "INTENT_META":
        return {
            "next": "META_ENGINE"
        }

    return None
