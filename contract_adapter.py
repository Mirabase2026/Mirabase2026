# contract_adapter.py
# =========================
# MIRA BASE – CONTRACT ADAPTER (v1)
# =========================
#
# Converts legacy result dict -> ResponseContract

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, List

from response_contract import (
    ResponseContract,
    PayloadItem,
    PayloadType,
    Source,
    Confidence,
    Constraint,
)


def to_contract(legacy: Dict[str, Any]) -> ResponseContract:
    decision_id = _new_decision_id()

    actions = legacy.get("actions", []) or []
    intent = legacy.get("intent")

    pipeline = legacy.get("pipeline")

    # source inference
    if pipeline == "FACT":
        source = Source.DETERMINISTIC
    elif pipeline in ("EPISTEMIC", "SECURITY", "SOCIAL"):
        source = Source.STATIC
    else:
        # fallback path: keep STATIC (no model)
        source = Source.STATIC

    constraints: List[Constraint] = [Constraint.NO_GENERATION, Constraint.NO_MEMORY_WRITE]

    # silent exit bridge (legacy might not use it anymore, but keep safe)
    if legacy.get("text", None) == "":
        constraints.append(Constraint.SILENT_EXIT)

    payload: List[PayloadItem] = []

    # FACTS
    facts = legacy.get("facts") or {}
    if facts:
        payload.append(PayloadItem(type=PayloadType.FACTS, data=_facts_to_payload(facts)))

    # SOCIAL (new meaning-only payload coming from logic.py)
    legacy_payload = legacy.get("payload") or {}
    if pipeline == "SOCIAL":
        # prefer semantic payload
        if isinstance(legacy_payload, dict) and legacy_payload.get("kind") == "SOCIAL":
            v = legacy_payload.get("value")
            if isinstance(v, dict):
                payload.append(PayloadItem(type=PayloadType.SOCIAL, data=v))
            elif isinstance(v, str) and v.strip():
                payload.append(PayloadItem(type=PayloadType.SOCIAL, data={"raw": v.strip()}))
        # backward compatibility (older versions might still set legacy["text"])
        elif isinstance(legacy.get("text"), str) and legacy["text"].strip():
            payload.append(PayloadItem(type=PayloadType.SOCIAL, data={"raw": legacy["text"].strip()}))

    # EPISTEMIC / SECURITY
    if pipeline == "EPISTEMIC":
        payload.append(PayloadItem(type=PayloadType.UNKNOWN, data={"reason": "EPISTEMIC"}))
    if pipeline == "SECURITY":
        payload.append(PayloadItem(type=PayloadType.ERROR, data={"reason": "SECURITY_BLOCKED"}))

    contract = ResponseContract(
        decision_id=decision_id,
        intent=intent,
        confidence=Confidence.MED,
        source=source,
        reason=f"ADAPTER_FROM_{pipeline}",
        actions=actions,
        constraints=constraints,
        payload=payload,
        chrono=legacy.get("chrono") or {},
        homeostasis=legacy.get("homeostasis") or {},
        meta_flags=(legacy.get("meta") or {}).get("flags", []) if isinstance(legacy.get("meta"), dict) else [],
        epistemic_state=(legacy.get("epistemic") or {}).get("epistemic_state")
        if isinstance(legacy.get("epistemic"), dict)
        else None,
    )
    return contract


def _facts_to_payload(facts: Dict[str, Any]) -> Dict[str, Any]:
    # Support BOTH old + new keys
    if "time" in facts:
        return {"kind": "TIME_NOW", "value": facts["time"]}
    if "time_now" in facts:
        return {"kind": "TIME_NOW", "value": facts["time_now"]}

    if "date" in facts:
        return {"kind": "DATE_TODAY", "value": facts["date"]}
    if "date_today" in facts:
        return {"kind": "DATE_TODAY", "value": facts["date_today"]}

    if "day" in facts:
        return {"kind": "DAY_TODAY", "value": facts["day"]}
    if "day_today" in facts:
        return {"kind": "DAY_TODAY", "value": facts["day_today"]}

    # arithmetic: support both schemas
    if "expression" in facts and "result" in facts:
        return {"kind": "ARITHMETIC", "expression": facts["expression"], "value": facts["result"]}
    if "arithmetic_value" in facts and "expression" in facts:
        return {"kind": "ARITHMETIC", "expression": facts["expression"], "value": facts["arithmetic_value"]}

    return {"kind": "FACTS_BLOB", "value": facts}


def _new_decision_id() -> str:
    return datetime.now(timezone.utc).strftime("D%Y%m%d%H%M%S%f")
