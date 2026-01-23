from dataclasses import dataclass
from typing import List, Dict, Optional

# =========================
# AKCE (zatím zachováváme)
# =========================

Action = str

RESPOND: Action = "respond"
VERIFY: Action = "verify"
SUMMARIZE: Action = "summarize"
STORE_LONG: Action = "store_long"
DO_NOTHING: Action = "do_nothing"


# =========================
# STRUKTUROVANÝ VÝSTUP
# =========================

@dataclass
class DecisionResult:
    """
    Výsledek rozhodování mozku.
    action:
        - respond
        - verify
        - summarize
        - store_long
        - do_nothing
    reflex_type:
        - None (zatím)
    memory_action:
        - None (zatím)
    """
    action: Action
    reflex_type: Optional[str] = None
    memory_action: Optional[str] = None


# =========================
# HLAVNÍ ROZHODOVÁNÍ
# =========================

def decide(
    user_text: str,
    recent_messages: List[Dict]
) -> DecisionResult:
    """
    Rozhodovací logika v1.1
    - BEZ AI
    - deterministická
    - připravená na NO_ACTION / reflexy / paměť
    """

    if not user_text:
        return DecisionResult(action=DO_NOTHING)

    text = user_text.lower().strip()

    # 1) Výslovná žádost o shrnutí
    if "shrň" in text or "shrnutí" in text:
        return DecisionResult(action=SUMMARIZE)

    # 2) Dotazy na fakta / ověřování
    if any(word in text for word in ["kolik", "kdy", "proč", "zdroj", "pravda"]):
        return DecisionResult(action=VERIFY)

    # 3) Opakování (už to padlo nedávno) → mlčet
    recent_contents = " ".join(
        m.get("content", "").lower() for m in recent_messages[-5:]
    )
    if text and text in recent_contents:
        return DecisionResult(action=DO_NOTHING)

    # 4) Potenciálně dlouhodobé / osobní sdělení
    # (zatím jen značíme – skutečné ukládání přijde později)
    if any(word in text for word in ["chci", "plán", "cíl", "budu", "dlouhodobě"]):
        return DecisionResult(
            action=RESPOND,
            memory_action=STORE_LONG  # zatím jen signál
        )

    # 5) Default: odpovědět
    return DecisionResult(action=RESPOND)

