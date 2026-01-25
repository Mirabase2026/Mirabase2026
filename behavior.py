# behavior.py

from social import handle as social_handle
from greeting import handle as greeting_handle
from reflexes import handle as reflex_handle
from intents import handle as intent_handle


BEHAVIOR_PIPELINE = [
    social_handle,     # silence + affect
    greeting_handle,   # heuristic greeting (dictionary-based)
    reflex_handle,     # hard reflexes
    intent_handle,     # intents → engines
]


def route(user_input: str):
    """
    Spustí behaviorální vrstvy v daném pořadí
    a vrátí první match, jinak None.
    """
    for handler in BEHAVIOR_PIPELINE:
        result = handler(user_input)
        if result is not None:
            return result
    return None
