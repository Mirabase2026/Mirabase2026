# social.py
import re

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[?!.,]", "", text)
    return text

SOCIAL_RULES = [
    r"^h+m+$",
    r"^a+ha+$",
    r"^ok$",
]

def handle(user_input: str):
    text = normalize(user_input)

    for pattern in SOCIAL_RULES:
        if re.match(pattern, text):
            return {
                "action": "NONE",
                "response": None,
                "source": "social"
            }
    return None


