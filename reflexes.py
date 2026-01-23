# reflexes.py

import re

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

REFLEX_RULES = [
    {
        "patterns": ["ahoj", "čau", "cus", "nazdar", "hello", "hi"],
        "response": "Ahoj."
    },
    {
        "patterns": ["jak se máš", "jak se mas", "jak se ti daří"],
        "response": "Mám se dobře."
    },
    {
        "patterns": ["díky", "dik", "thanks", "thx"],
        "response": "Není zač."
    },
    {
        "patterns": ["ok", "jo", "jasně", "dobře"],
        "response": "Rozumím."
    }
]

def reflex_match(user_input: str):
    text = normalize(user_input)

    for rule in REFLEX_RULES:
        for p in rule["patterns"]:
            if p in text:
                return {
                    "action": "RESPOND",
                    "response": rule["response"],
                    "source": "reflex"
                }

    return None
