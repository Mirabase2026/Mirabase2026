# social.py
import re

def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t.strip().lower())

SOCIAL_RULES = [
    {
        "patterns": ["hmm", "aha", "no jo", "jasně no", "ok...", "😅", "🙂"],
        "action": "NONE",
        "response": None
    },
    {
        "patterns": ["dobře", "beru", "platí"],
        "action": "RESPOND",
        "response": "Dobře."
    },
]

def handle(user_input: str):
    text = _norm(user_input)

    for rule in SOCIAL_RULES:
        for p in rule["patterns"]:
            if p in text:
                return {
                    "action": rule["action"],
                    "response": rule["response"],
                    "source": "social"
                }
    return None
