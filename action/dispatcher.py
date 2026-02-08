# action/dispatcher.py
# ====================
# Action Dispatcher
# ====================
# - enrich with user_id + context
# - gate (auth/limits/idempotence)
# - registry -> handler
# - append execution log
# - STOP on first error

from __future__ import annotations

from typing import Any, Dict

from action.execution_log import append_record
from action.gate import authorize
from action.registry import get_handler


def _blocked_unknown() -> dict:
    return {
        "status": "error",
        "message": "Unknown action type",
        "payload": {"error_type": "blocked"},
        "retryable": False,
    }


def dispatch(action: dict, user_id: str, context: dict) -> dict:
    enriched = {
        "action_type": action.get("action_type"),
        "params": action.get("params", {}),
        "user_id": user_id,
        "context": context,
    }

    gate_result = authorize(enriched)
    if gate_result.get("status") != "allow":
        return gate_result

    handler = get_handler(enriched["action_type"])
    if handler is None:
        return _blocked_unknown()

    result = handler(enriched)

    # Log for idempotence/audit
    req_id = (context or {}).get("request_id", "")
    trace_id = (context or {}).get("trace_id", "")
    if isinstance(req_id, str) and req_id:
        append_record(
            user_id=user_id,
            request_id=req_id,
            trace_id=str(trace_id),
            action_type=str(enriched.get("action_type")),
            result=result,
        )

    return result
