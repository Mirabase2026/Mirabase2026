# reflexes.py
import re
import unicodedata

def normalize(text: str) -> str:
    text = text.strip().lower()
    # remove diacritics
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    # remove punctuation
    text = re.sub(r"[?!.,:;\"'()\[\]{}]", "", text)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text

REFLEX_RULES = [
    # greetings
    (r"^ahoj$", "Ahoj."),
    (r"^cau$", "Čau."),
    (r"^ca(u+)$", "Čau."),
    # how are you
    (r"^jak se mas$", "Mám se dobře."),
    (r"^jak se mas\?$", "Mám se dobře."),
    # thanks
    (r"^(dik|dik+y|diky)$", "Není zač."),
    (r"^(diky moc|dik moc)$", "Není zač."),
    # combo: "ahoj jak se mas" (bez čárek)
    (r"^ahoj jak se mas$", "Ahoj. Mám se dobře."),
]

def handle(user_input: str):
    text = normalize(user_input)
    for pattern, response in REFLEX_RULES:
        if re.match(pattern, text):
            return {"action": "RESPOND", "response": response, "source": "reflex"}
    return None


