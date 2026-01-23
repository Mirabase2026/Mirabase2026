# intent_router.py
# Central intent → engine routing

from explain_engine import run_explain_engine
from opinion_engine import run_opinion_engine
from note_engine import run_note_engine

ENGINE_MAP = {
    "INTENT_EXPLAIN": {
        "engine": run_explain_engine,
    },
    "INTENT_OPINION": {
        "engine": run_opinion_engine,
    },
    "INTENT_NOTE": {
        "engine": run_note_engine,
    },
}

def route_intent(intent: str, text: str) -> dict:
    config = ENGINE_MAP.get(intent)

    if not config:
        return {
            "response": None,
            "error": "unknown_intent",
            "next": None,
        }

    engine = config["engine"]
    result = engine(text)

    return {
        "next": engine.__name__,
        "response": result,
        "error": None,
    }
