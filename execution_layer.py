# execution_layer.py
# =========================
# MIRA BASE – EXECUTION / DISCOURSE LAYER (v1)
# =========================
#
# Responsibilities:
# - consume ResponseContract
# - generate final user-facing sentence
# - NO reasoning
# - NO intent / action / fact decisions
# - NO memory writes
#
# This is the ONLY place where natural language is allowed.
#

from __future__ import annotations

from typing import Dict, Any

from response_contract import (
    ResponseContract,
    Source,
    Constraint,
    PayloadType,
)


# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------
def render(contract: ResponseContract) -> str:
    """
    Deterministic execution.
    One-way translation: semantic contract -> sentence.
    """

    # 1) Silent exit (explicit)
    if Constraint.SILENT_EXIT in contract.constraints:
        return ""

    # 2) Hard block: generative disabled in v1
    if contract.source == Source.GENERATIVE:
        return _say_unknown()

    # 3) Prefer FACTS payload
    for item in contract.payload:
        if item.type == PayloadType.FACTS:
            return _render_facts(item.data)

    # 4) Social / static payloads
    for item in contract.payload:
        if item.type == PayloadType.SOCIAL:
            return _render_social(item.data)

    # 5) Errors
    for item in contract.payload:
        if item.type == PayloadType.ERROR:
            return _render_error(item.data)

    # 6) Epistemic / unknown fallback
    if contract.epistemic_state and contract.epistemic_state != "OK":
        return _say_unknown()

    # 7) Absolute fallback
    return _say_unknown()


# -------------------------------------------------
# RENDERERS (DETERMINISTIC)
# -------------------------------------------------
def _render_facts(data: Dict[str, Any]) -> str:
    """
    Expected canonical shapes:
    - {"kind": "TIME_NOW", "value": "15:30"}
    - {"kind": "DATE_TODAY", "value": "6. 2. 2026"}
    - {"kind": "DAY_TODAY", "value": "čtvrtek"}
    - {"kind": "ARITHMETIC", "expression": "2+2", "value": 4}
    """
    kind = data.get("kind")

    if kind == "TIME_NOW":
        return f"Je {data.get('value')}."

    if kind == "DATE_TODAY":
        return f"Dnes je {data.get('value')}."

    if kind == "DAY_TODAY":
        return f"Dnes je {data.get('value')}."

    if kind == "ARITHMETIC":
        return f"{data.get('expression')} = {data.get('value')}"

    # Generic factual blob (debug-safe)
    value = data.get("value")
    if value is not None:
        return str(value)

    return _say_unknown()


def _render_social(data: Dict[str, Any]) -> str:
    """
    Deterministic social responses only.
    """
    key = data.get("key")
    if key:
        return _static_social_map().get(key, "Ahoj.")

    raw = data.get("raw")
    if isinstance(raw, str):
        return raw

    return "Ahoj."


def _render_error(data: Dict[str, Any]) -> str:
    reason = data.get("reason")

    if reason == "SECURITY_BLOCKED":
        return "Na tohle odpovědět nemohu."

    return _say_unknown()


# -------------------------------------------------
# FIXED PHRASES (v1)
# -------------------------------------------------
def _say_unknown() -> str:
    return "Promiň, ale tohle nevím."


def _static_social_map() -> Dict[str, str]:
    return {
        "HELLO": "Ahoj.",
        "HELLO_ASK": "Ahoj, co potřebuješ?",
    }
