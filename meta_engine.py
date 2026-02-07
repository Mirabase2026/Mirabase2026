# =========================
# MIRA BASE – META-COGNITION ENGINE (v1)
# =========================
#
# Responsibilities:
# - detect repeated failure / stagnation
# - emit ONLY meta flags
# - no text, no decisions

from typing import Dict, Any, List, Optional


def resolve_meta(
    *,
    last_results: Optional[List[Dict[str, Any]]],
) -> Dict[str, Any]:
    flags: List[str] = []

    if not last_results or len(last_results) < 2:
        return {"flags": flags}

    r1 = last_results[-1]
    r2 = last_results[-2]

    # REPEAT_FAILURE: stejný fail po sobě
    if r1.get("pipeline") == "EPISTEMIC" and r2.get("pipeline") == "EPISTEMIC":
        flags.append("REPEAT_FAILURE")

    # LOW_CONFIDENCE: opakovaný fallback / non-progress
    if r1.get("actions") == ["MODEL_FALLBACK"] and r2.get("actions") == ["MODEL_FALLBACK"]:
        flags.append("LOW_CONFIDENCE")

    # STALL: žádná fakta, žádná změna
    if (
        r1.get("pipeline") == r2.get("pipeline")
        and r1.get("actions") == r2.get("actions")
    ):
        flags.append("STALL")

    return {"flags": flags}
