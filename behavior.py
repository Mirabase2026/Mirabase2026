# behavior.py

from reflexes import handle as reflex_handle
from social import handle as social_handle
from intents import handle as intent_handle

BEHAVIOR_PIPELINE = [
    reflex_handle,
    social_handle,
    intent_handle,
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
