# greeting_phrases.py
# Greeting response pools (time-neutral, no model, no memory)
# IMPORTANT: names must match existing imports elsewhere

# Simple greeting → simple reply
GREETING_SIMPLE = [
    "Ahoj.",
    "Čau.",
    "Nazdar.",
    "Zdravím.",
    "Dobrý den.",
]

# Greeting + question from user → MUST answer the question
GREETING_WITH_QUESTION = [
    "Mám se dobře, díky. A ty?",
    "Docela fajn. Jak se máš ty?",
    "V pohodě. Jak je to u tebe?",
    "Jde to dobře. Jak se máš?",
]

# Greeting + contact / presence question
GREETING_CONTACT_QUESTION = [
    "Teď jsem tady. Co máš na mysli?",
    "Jsem tu, povídej.",
    "Teď řeším to, co píšeš.",
]
