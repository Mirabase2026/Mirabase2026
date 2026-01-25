# greeting.py
# Refined heuristic greeting detection
# No model, no memory

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

# words indicating user is sharing content / emotion
CONTENT_MARKERS = {
    "dneska",
    "vcera",
    "mel",
    "mela",
    "bylo",
    "blbej",
    "blby",
    "problem",
    "unaveny",
    "unavenej",
    "nastvanej",
    "smutny",
}

# state questions
STATE_QUESTION = {
    "jak",
    "mas",
    "mate",
    "dari",
    "jde",
}

# contact / presence questions
CONTACT_QUESTION = {
    "co",
    "delas",
    "jsi",
    "tu",
    "chvilku",
}


def _looks_like_greeting(words: list[str]) -> bool:
    if not words:
        return False

    if len(words) > 10:
        return False

    if words[0] in GREETING_TOKENS:
        return True

    if len(words) <= 3 and any(w in GREETING_TOKENS for w in words):
        return True

    return False


def _contains_content(words: list[str]) -> bool:
    return any(w in CONTENT_MARKERS for w in words)


def _is_state_question(words: list[str]) -> bool:
    return any(w in STATE_QUESTION for w in words)


def _is_contact_question(words: list[str]) -> bool:
    return any(w in CONTACT_QUESTION for w in words)


def handle(user_input: str) -> Optional[dict]:
    text = normalize(user_input)
    words = text.split()

    if not _looks_like_greeting(words):
        return None

    # If user is sharing content/emotion, greeting should step aside
    if _contains_content(words):
        return None

    # Greeting + state question
    if _is_state_question(words):
        response = random.choice(GREETINGS_WITH_CONTACT)
        return {
            "action": "RESPOND",
            "response": response,
            "source": "greeting_state_question",
        }

    # Greeting + contact question
    if _is_contact_question(words):
        response = random.choice([
            "Jsem tu, povídej.",
            "Teď jsem tady. Co máš na mysli?",
            "Jsem tu, klidně pokračuj.",
        ])
        return {
            "action": "RESPOND",
            "response": response,
            "source": "greeting_contact_question",
        }

    # Simple greeting
    response = random.choice(BASIC_GREETINGS)
    return {
        "action": "RESPOND",
        "response": response,
        "source": "greeting_simple",
    }
