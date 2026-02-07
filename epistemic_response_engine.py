# =========================
# MIRA BASE – EPISTEMIC RESPONSE ENGINE (v1)
# =========================
#
# Responsibilities:
# - convert epistemic states to short human responses
# - no logic, no facts, no memory

from typing import Optional


def resolve_epistemic_response(epistemic_state: str) -> Optional[str]:
    if epistemic_state == "UNKNOWN":
        return "Tomu nerozumím."

    if epistemic_state == "USER_STATE_UNKNOWN":
        return "To bez dalších informací nevím."

    if epistemic_state == "INSUFFICIENT_CONTEXT":
        return "Potřebuji víc informací."

    return None
