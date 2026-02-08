# action/handlers/set_preference.py
# =================================
# set_preference Handler
# =================================

from __future__ import annotations

from typing import Any, Dict, Tuple

from action.profile_store import load_profile, save_profile_atomic


# Allowlist: key -> (type, optional range tuple (min,max) or None)
PREFERENCE_SCHEMA: Dict[str, Tuple[type, Tuple[int, int] | None]] = {
    "verbosity": (int, (0, 5)),
    "response_language": (str, None),
    "communication_style": (str, None),
}


def _error(message: str, field: str | None = None, expected: str | None = None) -> dict:
    payload: Dict[str, Any] = {"error_type": "failed"}
    if field:
        payload["field"] = field
    if expected:
        payload["expected"] = expected
    return {
        "status": "error",
        "message": message,
        "payload": payload,
        "retryable": False,
    }


def handle(action: dict) -> dict:
    user_id = action.get("user_id")
    params = action.get("params") or {}

    if not isinstance(params, dict) or not params:
        return _error("Missing params", field="params")

    profile = load_profile(user_id)
    prefs = profile.get("preferences")
    if not isinstance(prefs, dict):
        prefs = {}
        profile["preferences"] = prefs

    for key, value in params.items():
        if key not in PREFERENCE_SCHEMA:
            return _error("Preference key not allowed", field=key)

        expected_type, rng = PREFERENCE_SCHEMA[key]

        # 🚫 EXPLICITNÍ ZÁKAZ BOOL PRO INT
        if expected_type is int and isinstance(value, bool):
            return _error("Invalid preference type", field=key, expected="int")

        if not isinstance(value, expected_type):
            return _error("Invalid preference type", field=key)

        if rng is not None:
            lo, hi = rng
            if not (lo <= value <= hi):
                return _error("Invalid preference value", field=key, expected=f"{lo}-{hi}")

    # Apply updates
    for key, value in params.items():
        prefs[key] = value

    save_profile_atomic(user_id, profile)

    return {
        "status": "success",
        "message": "Preference updated",
        "payload": {
            "preferences": dict(profile.get("preferences", {}))
        },
        "retryable": False,
    }
