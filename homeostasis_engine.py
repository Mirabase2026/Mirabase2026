# =========================
# MIRA BASE – HOMEOSTASIS ENGINE (v2)
# =========================
#
# Responsibilities:
# - track internal load / fatigue
# - emit ONLY signals (flags)
# - no text, no decisions, no memory
#
# Inputs:
# - turn_count: int
# - recent_intents: List[str]
#
# Outputs:
# - flags: List[str]

from typing import Dict, Any, List


def resolve_homeostasis(
    *,
    turn_count: int,
    recent_intents: List[str],
) -> Dict[str, Any]:
    flags: List[str] = []

    # -------------------------
    # ENERGY LEVELS
    # -------------------------
    if turn_count > 40:
        flags.append("ENERGY_CRITICAL")
    elif turn_count > 20:
        flags.append("ENERGY_LOW")
    else:
        flags.append("ENERGY_OK")

    # -------------------------
    # FATIGUE / REPETITION
    # -------------------------
    if len(recent_intents) >= 2 and recent_intents[-1] == recent_intents[-2]:
        flags.append("FATIGUE_REPEAT")

    if len(recent_intents) >= 3 and len(set(recent_intents[-3:])) == 1:
        flags.append("AVOID_REPEAT")

    return {
        "flags": flags,
    }
