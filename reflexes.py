# reflexes.py

import re

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

REFLEX_RULES = [
    {
        "pattern": r"^ahoj$",
        "response": "Ahoj."
    },
    {
        "pattern": r"^jak se mas$",
        "response": "Mám se dobře."
    },
    {
        "pattern": r"^diky$",
        "response": "Není zač."
    }
]


def handle(user_input: str):
    text = normalize(user_input)

    for rule in REFLEX_RULES:
        if re.match(rule["pattern"], text):
            return {
                "action": "RESPOND",
                "response": rule["response"],
                "source": "reflex"
            }
    return None

