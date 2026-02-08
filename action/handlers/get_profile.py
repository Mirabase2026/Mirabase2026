# action/handlers/get_profile.py
# ==============================
# get_profile Handler
# ==============================
# - read-only
# - strict output sanitization (allowlist)
# - NEVER returns internal/system fields

from __future__ import annotations

from typing import Any, Dict

from action.profile_store import load_profile


# Allowlist top-level sections that are safe to expose
ALLOWED_SECTIONS = {
    "user_id",
    "identity",
    "access",
    "preferences",
    "temporal",
    "meta",
}

# Nested allowlists (defensive; future-proof)
IDENTITY_ALLOWED = {"role", "status", "name", "display_name"}
ACCESS_ALLOWED = {
    "allowed_actions",
    "denied_actions",
    "restricted_to_self",
    "daily_limit",
    "access_level",
    "max_credits",
}
PREFERENCES_ALLOWED = {
    "verbosity",
    "response_language",
    "communication_style",
}
META_ALLOWED = {"created_at", "profile_version"}
TEMPORAL_ALLOWED = {"valid_until", "temporary_actions"}


def _sanitize_section(section: str, value: Any) -> Any:
    if section == "identity" and isinstance(value, dict):
        return {k: v for k, v in value.items() if k in IDENTITY_ALLOWED}
    if section == "access" and isinstance(value, dict):
        return {k: v for k, v in value.items() if k in ACCESS_ALLOWED}
    if section == "preferences" and isinstance(value, dict):
        return {k: v for k, v in value.items() if k in PREFERENCES_ALLOWED}
    if section == "meta" and isinstance(value, dict):
        return {k: v for k, v in value.items() if k in META_ALLOWED}
    if section == "temporal" and isinstance(value, dict):
        return {k: v for k, v in value.items() if k in TEMPORAL_ALLOWED}
    # user_id or unknown shapes
    return value


def handle(action: dict) -> dict:
    user_id = action.get("user_id")

    try:
        profile = load_profile(user_id)
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Profile not found",
            "payload": {"error_type": "failed"},
            "retryable": False,
        }

    sanitized: Dict[str, Any] = {}

    for section, value in profile.items():
        # Drop any internal/system fields or underscored keys
        if section.startswith("_"):
            continue
        if section not in ALLOWED_SECTIONS:
            continue

        sanitized[section] = _sanitize_section(section, value)

    return {
        "status": "success",
        "message": "Profile loaded",
        "payload": {
            "profile": sanitized
        },
        "retryable": False,
    }
