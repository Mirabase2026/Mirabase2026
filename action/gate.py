# action/gate.py
# ==============
# Authorization & Limits Gate
# ===========================
# - role / ACL / temporal / daily_limit (24h)
# - idempotence via request_id (execution_log.jsonl)
# - NEVER executes actions

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from action.execution_log import count_actions_last_24h, find_result_by_request_id
from action.profile_store import load_profile, get_cached_profile


def _blocked(message: str) -> dict:
    return {
        "status": "error",
        "message": message,
        "payload": {"error_type": "blocked"},
        "retryable": False,
    }


def authorize(action: dict) -> dict:
    action_type = action.get("action_type")
    user_id = action.get("user_id")
    context = action.get("context") or {}
    request_id = context.get("request_id")

    # Idempotence: if already executed, return stored result immediately
    if isinstance(request_id, str) and request_id:
        prev = find_result_by_request_id(request_id)
        if isinstance(prev, dict) and prev.get("status") in ("success", "error", "pending"):
            return prev

    # Load profile (prefer cache)
    profile = get_cached_profile(user_id)
    if profile is None:
        try:
            profile = load_profile(user_id)
        except FileNotFoundError:
            return _blocked("Action blocked by authorization")

    identity = profile.get("identity") or {}
    status = identity.get("status", "active")
    if status != "active":
        return _blocked("Action blocked by authorization")

    access = profile.get("access") or {}
    allowed = access.get("allowed_actions", [])
    denied = access.get("denied_actions", [])

    # Default deny if access missing or malformed
    if not isinstance(allowed, list) or not isinstance(denied, list):
        return _blocked("Action blocked by authorization")

    # Temporal constraints (optional)
    temporal = profile.get("temporal")
    if isinstance(temporal, dict):
        valid_until = temporal.get("valid_until")
        temp_actions = temporal.get("temporary_actions", [])
        now = datetime.now(timezone.utc)

        if isinstance(valid_until, str) and valid_until:
            try:
                until_dt = datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
            except ValueError:
                until_dt = None

            if until_dt and now > until_dt:
                # expired → treat as no temporary permissions
                temp_actions = []

        if isinstance(temp_actions, list) and action_type in temp_actions:
            # temporary allow for this action_type even if not in allowed
            pass
        else:
            # normal allowlist path
            pass

    # Allow/deny evaluation (explicit)
    is_allowed = ("*" in allowed) or (action_type in allowed)
    is_denied = ("*" in denied) or (action_type in denied)

    # Apply temporary allow if present and valid
    if isinstance(profile.get("temporal"), dict):
        temporal = profile["temporal"]
        temp_actions = temporal.get("temporary_actions", [])
        valid_until = temporal.get("valid_until")
        now = datetime.now(timezone.utc)

        if isinstance(valid_until, str) and valid_until:
            try:
                until_dt = datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
            except ValueError:
                until_dt = None
        else:
            until_dt = None

        temp_valid = (until_dt is None) or (now <= until_dt)

        if temp_valid and isinstance(temp_actions, list) and action_type in temp_actions:
            is_allowed = True

    if (not is_allowed) or is_denied:
        return _blocked("Action blocked by authorization")

    # Daily limit (24h) — optional
    daily_limit = access.get("daily_limit", -1)
    if isinstance(daily_limit, int) and daily_limit >= 0:
        used = count_actions_last_24h(user_id)
        if used >= daily_limit:
            return _blocked("Action blocked by authorization")

    return {"status": "allow"}
