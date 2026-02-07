# response_planner.py
# =========================
# MIRA BASE – RESPONSE PLANNER (v1)
# =========================
#
# Responsibilities:
# - map (intent + secondary_intents + entities) -> actions
# - NO text generation

from __future__ import annotations

from typing import Any, Dict, List


def _D(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _L(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def plan_actions(primary_intent: Any, secondary_intents: Any, entities: Any) -> List[str]:
    secondary = [str(x) for x in _L(secondary_intents)]
    ent = _D(entities)

    actions: List[str] = []

    # FACT actions
    if "TIME_QUERY" in secondary:
        actions.append("TIME_NOW")
    if "DATE_QUERY" in secondary:
        actions.append("DATE_TODAY")
    if "DAY_QUERY" in secondary:
        actions.append("DAY_TODAY")

    # arithmetic if we have expression or explicit arith signal
    if "ARITH_QUERY" in secondary or isinstance(ent.get("expression"), str) and ent.get("expression").strip():
        actions.append("ARITHMETIC")

    # social (pure deterministic)
    if "GREETING" in secondary:
        # This action is used by discourse rules (and can be used later for richer routing)
        actions.append("GREET_SIMPLE")

    # If nothing planned, keep it empty (router -> STATIC -> fallback contract)
    return actions
