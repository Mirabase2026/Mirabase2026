# greeting.py
# Heuristic greeting detection + dictionary-based response
# No model, no memory, semantic-ish classification

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


# greeting-like tokens (normalized)
GREETING_TOKENS = {
    "ahoj",
    "cau",
    "caau",
    "nazdar",
    "zdar",
    "zdravim",
    "zdravicko",
    "cus",
    "cusik",
    "dobry",
    "dobre",
}

# strong greeting phrases
GREETING_PHRASES = {
    "dobry den",
    "dobre rano",
    "dobry vecer",
}

# contact cues (greeting + contact)
CONTACT_CUES = {
    "jak",
    "mas",
    "mate",
    "dari",
    "jde",
    "co",
    "delas",
    "chvilku",
    "jsi",
    "tu",
    "slysis",
}


def _looks_like_greeting(text_norm: str) -> bool:
    if not text_norm:
        return False

    words = text_norm.split()

    # too long → not greeting
    if len(words) > 8:
        return False

    joined = " ".join(words)

    # strong phrases
    if joined in GREETING_PHRASES:
        return True

    # start token
    first = words[0]
    if first in GREETING_TOKENS:
        return True

    # first two tokens
    if len(words) >= 2 and f"{words[0]} {words[1]}" in GREETING_PHRASES:
        return True

    # very short with greeting token anywhere
    if len(words) <= 3 and any(w in GREETING_TOKENS for w in words):
        return True

    return False


def _prefer_contact_reply(text_norm: str) -> bool:
    words = set(text_norm.split())
    return any(w in CONTACT_CUES for w in words)


def handle(user_input: str) -> Optional[dict]:
    text = normalize(user_input)

    if not _looks_like_greeting(text):
        return None

    pool = GREETINGS_WITH_CONTACT if _prefer_contact_reply(text) else BASIC_GREETINGS
    response = random.choice(pool)

    return {
        "action": "RESPOND",
        "response": response,
        "source": "greeting",
    }
