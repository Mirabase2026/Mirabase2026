# social.py
import re
import unicodedata

def normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[?!.,:;\"'()\[\]{}]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

SOCIAL_PATTERNS = [
    r"^h+m+$",        # hm, hmm, hmmm...
    r"^a+ha+$",       # aha, ahaa...
    r"^ok+$",         # ok, okk (když někdo drží klávesu)
]

def handle(user_input: str):
    text = normalize(user_input)
    for pat in SOCIAL_PATTERNS:
        if re.match(pat, text):
            return {"action": "NONE", "response": None, "source": "social"}
    return None



