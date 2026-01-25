# behavior.py

from social import handle as social_handle
from greeting import handle as greeting_handle
from reflexes import handle as reflex_handle
from intents import handle as intent_handle


BEHAVIOR_PIPELINE = [
    social_handle,
    greeting_handle,
    reflex_handle,
    intent_handle,
]


def route(user_input: str):
    for handler in BEHAVIOR_PIPELINE:
        result = handler(user_input)
        if result is not None:
            return result
    return None
