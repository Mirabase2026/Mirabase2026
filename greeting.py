# greeting.py
# Heuristic greeting classification with subtypes
# No model, no memory

import random
import re
import unicodedata
from typing import Optional

from greeting_phrases import (
    GREETING_SIMPLE,
    GREETING_WITH_QUESTION,
    GREETING_CONTACT_QUESTION,
)


def normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[?!.,:;\"'()\[\]{}]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


GREETING_TOKENS = {
    "ahoj",
    "cau",
    "nazdar",
    "zdar",
    "zdravim",
    "cus",
    "dobry",
}

QUESTION_WORDS = {
    "jak",
    "co",
    "delas",
    "mas",
    "mate",
    "dari",
    "jde",
}


def _looks_like_greeting(words: list[str]) -> bool:
    if not words:
        return False

    if len(words) > 8:
        return False

    if words[0] in GREETING_TOKENS:
        return True

    if len(words) <= 3 and any(w in GREETING_TOKENS for w in words):
        return True

    return False


def _is_question(words: list[str]) -> bool:
    return any(w in QUESTION_WORDS for w in words)


def handle(user_input: str) -> Optional[dict]:
    text = normalize(user_input)
    words = text.split()

    if not _looks_like_greeting(words):
        return None

    # GREETING + QUESTION
    if _is_question(words):
        # "jak se máš" style
        if "mas" in words or "mate" in words:
            response = random.choice(GREETING_WITH_QUESTION)
        else:
            # "co děláš", "jsi tu" apod.
            response = random.choice(GREETING_CONTACT_QUESTION)

        return {
            "action": "RESPOND",
            "response": response,
            "source": "greeting_question",
        }

    # SIMPLE GREETING
    response = random.choice(GREETING_SIMPLE)

    return {
        "action": "RESPOND",
        "response": response,
        "source": "greeting_simple",
    }
