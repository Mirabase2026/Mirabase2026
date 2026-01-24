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
        r".*\b(vysvetli|vysvetlit|vysvetlis|muzes mi vysvetlit|"
        r"objasni|jak to funguje)\b.*",
        "INTENT_EXPLAIN",
    ),

    # -------------------------
    # NOTE / SUMMARY
    # -------------------------
    (
        r".*\b(shrn|shrnut|poznamky|stru(c|č)ne|v bodech)\b.*",
        "INTENT_NOTE",
    ),

    # -------------------------
    # OPINION
    # -------------------------
    (
        r".*\b(co si myslis|jaky je tvuj nazor|tvuj nazor|myslis si ze)\b.*",
        "INTENT_OPINION",
    ),

    # -------------------------
    # CHAT / CONTINUE
    # -------------------------
    (
        r".*\b(co delas|konkretizuj|rozved|rozvest|pokracuj|"
        r"a dal|jdeme dal|pokracuj dal)\b.*",
        "INTENT_CHAT",
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
