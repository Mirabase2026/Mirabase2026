# action/registry.py
# ==================
# Action Registry
# ==================

from action.handlers.noop import handle as noop_handler
from action.handlers.set_preference import handle as set_preference_handler
from action.handlers.get_profile import handle as get_profile_handler

REGISTRY = {
    "noop": noop_handler,
    "set_preference": set_preference_handler,
    "get_profile": get_profile_handler,
}

def get_handler(action_type: str):
    return REGISTRY.get(action_type)
