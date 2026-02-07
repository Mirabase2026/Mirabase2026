# =========================
# MIRA BASE – RESPONSE SOURCE ROUTER (v1)
# =========================
#
# Responsibilities:
# - decide WHERE the response should come from (source selection)
# - NO text, NO generation, NO facts
# - purely routing signals
#
# Sources (v1):
# - STATIC: deterministic short responses / social libs (future)
# - DETERMINISTIC: fact engines / calculators
# - MEMORY: LTM / personal facts (future)
# - GENERATIVE: model / chat engine (future)
#
# Note: v1 is intentionally conservative and minimal.

from typing import Dict, Any, List


FACT_ACTIONS = {"TIME_NOW", "DAY_TODAY", "DATE_TODAY", "ARITHMETIC"}


def resolve_response_source(
    *,
    actions: List[str],
    attention: Dict[str, Any],
    entities: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    # 1) Deterministic facts always win
    if any(a in FACT_ACTIONS for a in actions):
        return {"source": "DETERMINISTIC", "reason": "FACT_ACTION"}

    # 2) Memory-based responses (placeholder for future)
    #    (we keep it conservative; activate later when memory intents/actions exist)
    if actions and any(a.startswith("MEMORY_") for a in actions):
        return {"source": "MEMORY", "reason": "MEMORY_ACTION"}

    # 3) Generative fallback (future model)
    if "MODEL_FALLBACK" in actions:
        return {"source": "GENERATIVE", "reason": "MODEL_FALLBACK"}

    # 4) Default: STATIC/SOCIAL deterministic response path
    return {"source": "STATIC", "reason": "DEFAULT"}
