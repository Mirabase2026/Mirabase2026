# greeting.py
# Heuristic greeting detection (semantic, subtype-aware)
# Uses existing greeting_phrases exports

import random
import re
import unicodedata
from typing import Optional

from greeting_phrases import BASIC_GREETINGS, GREETINGS_WITH_CONTACT


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
    "jsi",
    "tu",
}


def _looks_like_greeting(words: list[str]) -> bool:
    if not words:
        return False

    if len(words) > 8:
        return False

    # greeting at start
    if words[0] in GREETING_TOKENS:
        return True

    # short message containing greeting token
    if len(words) <= 3 and any(w in GREETING_TOKENS for w in words):
        return True

    return False


def _has_question(words: list[str]) -> bool:
    return any(w in QUESTION_WORDS for w in words)


def handle(user_input: str) -> Optional[dict]:
    text = normalize(user_input)
    words = text.split()

    if not _looks_like_greeting(words):
        return None

    # Greeting + question → answer appropriately
    if _has_question(words):
        response = random.choice(GREETINGS_WITH_CONTACT)
        return {
            "action": "RESPOND",
            "response": response,
            "source": "greeting_question",
        }

    # Simple greeting
    response = random.choice(BASIC_GREETINGS)
    return {
        "action": "RESPOND",
        "response": response,
        "source": "greeting_simple",
    }
