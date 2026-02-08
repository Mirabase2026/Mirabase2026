# action/parser.py
# =================
# Input Parser
# =================
# Supported verbs:
# - /noop
# - /set <key> <value>
# - /get_profile

from __future__ import annotations

import re
from typing import Any, Dict


def _parser_error(parser_code: str, field: str | None = None, message: str = "Invalid command syntax") -> dict:
    payload: Dict[str, Any] = {"error_type": "parser_error", "parser_code": parser_code}
    if field:
        payload["field"] = field
    return {
        "status": "error",
        "message": message,
        "payload": payload,
        "retryable": False,
    }


_INT_RE = re.compile(r"^-?\d+$")


def _parse_value(token: str) -> Any:
    # quoted string
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return token[1:-1]

    # integer
    if _INT_RE.match(token):
        return int(token)

    # keep everything else as string
    return token


def parse_input(raw_input):
    # JSON direct
    if isinstance(raw_input, dict):
        action_type = raw_input.get("action_type")
        params = raw_input.get("params", {})
        if not isinstance(action_type, str) or not action_type:
            return _parser_error("syntax_error")
        if params is None:
            params = {}
        if not isinstance(params, dict):
            return _parser_error("invalid_param_type", field="params")
        return {"action_type": action_type, "params": params}

    # Text command
    if not isinstance(raw_input, str):
        return _parser_error("syntax_error")

    text = raw_input.strip()
    if not text.startswith("/"):
        return _parser_error("unknown_command")

    parts = text.split()
    verb = parts[0][1:].strip()

    if not re.fullmatch(r"[a-z_]+", verb):
        return _parser_error("syntax_error")

    # /noop
    if verb == "noop":
        if len(parts) != 1:
            return _parser_error("syntax_error")
        return {"action_type": "noop", "params": {}}

    # /get_profile
    if verb == "get_profile":
        if len(parts) != 1:
            return _parser_error("syntax_error")
        return {"action_type": "get_profile", "params": {}}

    # /set <key> <value> [<key> <value> ...]
    if verb == "set":
        if len(parts) < 3:
            return _parser_error("missing_param", field="params")
        if (len(parts) - 1) % 2 != 0:
            return _parser_error("syntax_error")

        params: Dict[str, Any] = {}
        i = 1
        while i < len(parts):
            key = parts[i]
            val = parts[i + 1]

            if not re.fullmatch(r"[a-z_]+", key):
                return _parser_error("syntax_error")

            if key in params:
                return _parser_error("syntax_error")

            params[key] = _parse_value(val)
            i += 2

        return {"action_type": "set_preference", "params": params}

    return _parser_error("unknown_command")
