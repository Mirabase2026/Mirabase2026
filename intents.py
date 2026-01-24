# intents.py
# Intent detection with UX-friendly patterns
# No AI, pure rules + normalization

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
    # -------------------------
    # EXPLAIN
    # -------------------------
    (
        r".*\b(vysvetli|vysvetlit|vysvetlis|muze(s|š) mi vysvetlit|"
        r"muzes mi vysvetlit|objasni|jak to funguje)\b.*",
        "INTENT_EXPLAIN",
    ),

    # -------------------------
    # NOTE / SUMMARY
    # -------------------------
    (
        r".*\b(udelej|udelas|udelat|shr(n|ň)|shrnout|"
        r"poznamky|stru(c|č)ne|v bodech)\b.*",
        "INTENT_NOTE",
    ),

    # -------------------------
    # OPINION
    # -------------------------
    (
        r".*\b(co si myslis|jaky je tvuj nazor|jaky mas nazor|"
        r"tvuj nazor|myslis si ze)\b.*",
        "INTENT_OPINION",
    ),

    # -------------------------
    # CONTINUE
    # -------------------------
    (
        r".*\b(pokracuj|jedem dal|jdeme dal|dalsi|pokra(c|č)uj prosim)\b.*",
        "INTENT_CONTINUE",
    ),
]


def handle(user_input: str):
    text = normalize(user_input)

    for pattern, intent in INTENT_RULES:
        if re.search(pattern, text):
            return {
                "action": "INTENT",
                "intent": intent,
                "response": None,
                "source": "intent",
            }

    return None
