# intents.py

import re
import unicodedata

# =========================
# NORMALIZACE VSTUPU
# =========================

def normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[?!.,:;\"'()\[\]{}]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


# =========================
# INTENT PRAVIDLA
# =========================

INTENT_RULES = [
    # ---- EXPLAIN ----
    (r"^(vysvetli|vysvetli to)$", "INTENT_EXPLAIN"),
    (r"^(vysvetli vic|rozved to)$", "INTENT_EXPLAIN"),

    # ---- NOTES / SUMMARY ----
    (r"^(udelej poznamky|udelej si poznamky)$", "INTENT_NOTE"),
    (r"^(shrn|shrni|shrnut)$", "INTENT_NOTE"),
    (r"^(zapis si to)$", "INTENT_NOTE"),

    # ---- CONTINUE ----
    (r"^(pokracuj|jdeme dal|jedeme dal)$", "INTENT_CONTINUE"),

    # ---- OPINION ----
    (r"^co si myslis( o.*)?$", "INTENT_OPINION"),
    (r"^jaky je tvuj nazor( na.*)?$", "INTENT_OPINION"),

    # ---- META / NEXT STEP ----
    (r"^co s tim( udelame)?$", "INTENT_META"),
]


# =========================
# HANDLER
# =========================

def handle(user_input: str):
    text = normalize(user_input)

    for pattern, intent in INTENT_RULES:
        if re.match(pattern, text):
            return {
                "action": "INTENT",
                "intent": intent,
                "response": None,
                "source": "intent"
            }

    return None
