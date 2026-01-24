# intent_router.py
# Central intent → engine routing (stable)

import explain_engine
import opinion_engine
import note_engine
import chat_engine

ENGINE_MAP = {
    "INTENT_EXPLAIN": explain_engine,
    "INTENT_OPINION": opinion_engine,
    "INTENT_NOTE": note_engine,
    "INTENT_CHAT": chat_engine,
}

def route_intent(intent: str, text: str) -> dict:
    engine_module = ENGINE_MAP.get(intent)

    if not engine_module:
        return {
            "response": None,
            "error": "unknown_intent",
            "next": None,
        }

    response = engine_module.run(text)

    return {
        "next": engine_module.__name__,
        "response": response,
        "error": None,
    }
