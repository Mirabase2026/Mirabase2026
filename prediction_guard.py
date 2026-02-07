# =========================
# MIRA BASE – PREDICTION / GUARD ENGINE (v1)
# =========================
#
# Responsibilities:
# - predict low-quality or risky responses
# - emit ONLY guard flags
# - no text, no decisions

from typing import Dict, Any, List


def resolve_prediction_guard(
    *,
    attention: Dict[str, Any],
    epistemic: Dict[str, Any],
    meta: Dict[str, Any],
    planned_actions: List[str],
) -> Dict[str, Any]:
    flags: List[str] = []

    confidence = attention.get("confidence", 1.0)
    epistemic_state = epistemic.get("epistemic_state")
    meta_flags = meta.get("flags", [])

    # LOW_SIGNAL: velmi nízká jistota vstupu
    if confidence < 0.2:
        flags.append("LOW_SIGNAL")

    # RISK_HALLUCINATION: nejasný stav + model fallback
    if epistemic_state == "UNKNOWN" and "MODEL_FALLBACK" in planned_actions:
        flags.append("RISK_HALLUCINATION")

    # AVOID_MODEL: raději nic než generovat
    if "LOW_SIGNAL" in flags and "MODEL_FALLBACK" in planned_actions:
        flags.append("AVOID_MODEL")

    # STALL_RISK: meta hlásí stagnaci
    if "STALL" in meta_flags or "REPEAT_FAILURE" in meta_flags:
        flags.append("STALL_RISK")

    return {"flags": flags}
