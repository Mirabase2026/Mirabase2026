# intents.py
import re

def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t.strip().lower())

INTENT_RULES = [
    {
        "patterns": ["pokračuj", "jdeme dál", "další krok"],
        "intent": "INTENT_CONTINUE"
    },
    {
        "patterns": ["vysvětli", "vysvětlení", "jak to funguje"],
        "intent": "INTENT_EXPLAIN"
    },
    {
        "patterns": ["udělej poznámky", "poznamky", "shrň"],
        "intent": "INTENT_NOTE"
    },
    {
        "patterns": ["navazujeme na", "pokračovací", "fáze"],
        "intent": "INTENT_CONTEXT"
    },
]

def handle(user_input: str):
    text = _norm(user_input)

    for rule in INTENT_RULES:
        for p in rule["patterns"]:
            if p in text:
                return {
                    "action": rule["intent"],
                    "response": None,
                    "source": "intent"
                }
    return None
