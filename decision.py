from typing import List, Dict

Action = str

RESPOND: Action = "respond"
VERIFY: Action = "verify"
SUMMARIZE: Action = "summarize"
STORE_LONG: Action = "store_long"
DO_NOTHING: Action = "do_nothing"


def decide(
    user_text: str,
    recent_messages: List[Dict]
) -> Action:
    """
    Jednoduchá rozhodovací logika (bez AI).
    """

    text = user_text.lower()

    # 1) Pokud uživatel výslovně žádá shrnutí
    if "shrň" in text or "shrnutí" in text:
        return SUMMARIZE

    # 2) Pokud se ptá na fakta / čísla / zdroje
    if any(word in text for word in ["kolik", "kdy", "proč", "zdroj", "pravda"]):
        return VERIFY

    # 3) Pokud se něco opakuje (už to padlo nedávno)
    recent_contents = " ".join(
        m.get("content", "").lower() for m in recent_messages[-5:]
    )
    if text and text in recent_contents:
        return DO_NOTHING

    # 4) Pokud to zní osobně nebo dlouhodobě
    if any(word in text for word in ["chci", "plán", "cíl", "budu", "dlouhodobě"]):
        return STORE_LONG

    # Default
    return RESPOND
