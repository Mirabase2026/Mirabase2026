# social.py
# Social micro-reactions (no model, no memory)

import re
import unicodedata


def normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[?!.,:;\"'()\[\]{}]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


# -------------------------
# SOCIAL PATTERNS
# -------------------------

# Silent fillers → no response
SILENT_PATTERNS = [
    r"^h+m+$",        # hm, hmm
    r"^a+ha+$",       # aha
    r"^ok+$",         # ok
]

# Positive affect / compliments
POSITIVE_PATTERNS = [
    r".*\bjsi milace?k\b.*",
    r".*\bjsi hodna\b.*",
    r".*\bjsi super\b.*",
    r".*\bjsi chytra\b.*",
]

# Negative affect / complaints
NEGATIVE_PATTERNS = [
    r".*\bjsi hrozna\b.*",
    r".*\bjsi strasna\b.*",
    r".*\bstves me\b.*",
    r".*\bpekne me stves\b.*",
]


def handle(user_input: str):
    text = normalize(user_input)

    # 1) silent social signals → no response
    for pat in SILENT_PATTERNS:
        if re.match(pat, text):
            return {"action": "NONE", "response": None, "source": "social"}

    # 2) positive affect → calm acknowledgment
    for pat in POSITIVE_PATTERNS:
        if re.match(pat, text):
            return {
                "action": "RESPOND",
                "response": "Díky, to mě těší.",
                "source": "social",
            }

    # 3) negative affect → calm apology (no escalation)
    for pat in NEGATIVE_PATTERNS:
        if re.match(pat, text):
            return {
                "action": "RESPOND",
                "response": "Omlouvám se.",
                "source": "social",
            }

    return None
