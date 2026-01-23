# intents.py
import re
import unicodedata

def normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[?!.,:;\"'()\[\]{}]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

INTENT_RULES = [
    # explain
    (r"^(vysvetli|vysvetli to)$", "INTENT_EXPLAIN"),
    # notes / summarize
    (r"^(udelej poznamky|shr(n|ň))$", "INTENT_NOTE"),
    # continue
    (r"^(pokracuj|jdeme dal)$", "INTENT_CONTINUE"),
    # opinion
    (r"^co si myslis( o.*)?$", "INTENT_OPINION"),
]

def handle(user_input: str):
    text = normalize(user_input)
    for pattern, intent in INTENT_RULES:
        if re.match(pattern, text):
            return {
                "action": intent,
                "response": None,
                "source": "intent"
            }
    return None
