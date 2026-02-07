# social_engine.py
# =========================
# MIRA BASE – SOCIAL ENGINE
# =========================
#
# Converts SOCIAL ACTIONS into human responses.
# This file MAY contain language, tone, emotion.
# Brain never touches this.

from typing import Optional


def handle(action: str) -> Optional[str]:
    if action == "GREET_SIMPLE":
        return "Ahoj."

    if action == "THANK_SIMPLE":
        return "Rádo se stalo."

    if action == "SMALLTALK_STATE_SIMPLE":
        return "Mám se fajn."

    return None
