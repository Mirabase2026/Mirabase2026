# social.py
import re

def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t.strip().lower())

SOCIAL_RULES = [
    {
        "pattern": r"^(h+m+|hm+)$",
        "action": "NONE",
        "response": None
    },
    {
        "pattern": r"^(a+ha+)$",
        "action": "NONE",
        "response": None
    },
    {
        "pattern": r"^ok(\.*)?$",
        "action": "NONE",
        "response": None
    }
]


def handle(user_input: str):
    text = _norm(user_input)

    for rule in SOCIAL_RULES:
        if re.match(rule["pattern"], text):
            return {
                "action": rule["action"],
                "response": rule["response"],
                "source": "social"
            }
    return None

