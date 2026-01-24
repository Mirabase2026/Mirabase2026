# chat_engine.py
# Casual friend-style responses with minimal context awareness

def run(text: str, last_assistant_response: str | None = None) -> str:
    trigger_words = ("konkretizuj", "rozved", "rozvest", "a dal", "pokracuj")

    lowered = text.lower()

    wants_detail = any(word in lowered for word in trigger_words)

    if wants_detail:
        if last_assistant_response:
            return "Myslíš k tomu předchozímu? Můžu to víc rozvést."
        else:
            return "Jasně — co přesně chceš upřesnit?"

    return "Jsem tady, pojďme to vzít dál."
