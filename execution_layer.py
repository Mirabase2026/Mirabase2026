# execution_layer.py
# =========================
# MIRA BASE – EXECUTION / DISCOURSE LAYER (v2.2)
# =========================

from __future__ import annotations
from typing import Dict, Any

from response_contract import (
    ResponseContract,
    Source,
    Constraint,
    PayloadType,
)

from epistemic_response_engine import resolve_epistemic_response


def render(contract: ResponseContract) -> str:
    # Silent exit
    if Constraint.SILENT_EXIT in contract.constraints:
        return ""

    # ---- EPISTEMIC FIRST (v2) ----
    if contract.epistemic_state and contract.epistemic_state != "OK":
        msg = resolve_epistemic_response(contract.epistemic_state)
        if isinstance(msg, str):
            return msg

    # Generative fallback (should be rare)
    if contract.source == Source.GENERATIVE:
        return _say_unknown()

    # FACTS
    for item in contract.payload:
        if item.type == PayloadType.FACTS:
            return _render_facts(item.data)

    # SOCIAL
    for item in contract.payload:
        if item.type == PayloadType.SOCIAL:
            return _render_social(item.data)

    # ERROR
    for item in contract.payload:
        if item.type == PayloadType.ERROR:
            return _render_error(item.data)

    return _say_unknown()


def _render_facts(data: Dict[str, Any]) -> str:
    kind = data.get("kind")

    if kind == "TIME_NOW":
        return f"Je {data.get('value')}."
    if kind == "DATE_TODAY":
        return f"Dnes je {data.get('value')}."
    if kind == "DAY_TODAY":
        return f"Dnes je {data.get('value')}."
    if kind == "ARITHMETIC":
        return f"{data.get('expression')} = {data.get('value')}"

    if data.get("value") is not None:
        return str(data.get("value"))

    return _say_unknown()


def _render_social(data: Dict[str, Any]) -> str:
    """
    SOCIAL v2
    Brain already resolved final text.
    """
    text = data.get("text")
    if isinstance(text, str):
        return text

    return "Ahoj."


def _render_error(data: Dict[str, Any]) -> str:
    if data.get("reason") == "SECURITY_BLOCKED":
        return "Na tohle odpovědět nemohu."
    return _say_unknown()


def _say_unknown() -> str:
    return "Promiň, ale tohle nevím."
