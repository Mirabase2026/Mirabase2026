# intent_router.py
# Central intent → engine routing (with minimal context)

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

def route_intent(intent: str, text: str, last_assistant_response: str | None = None) -> dict:
    engine_module = ENGINE_MAP.get(intent)

    if not engine_module:
        return {
            "response": None,
            "error": "unknown_intent",
            "next": None,
        }

    # chat_engine wants context, others not
    if intent == "INTENT_CHAT":
        response = engine_module.run(text, last_assistant_response)
    else:
        response = engine_module.run(text)

    return {
        "next": engine_module.__name__,
        "response": response,
        "error": None,
    }
