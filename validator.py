# =========================
# MIRA BASE – VALIDATOR
# =========================
#
# Responsibilities:
# - sanity check factual outputs
# - veto nonsense before ACTION LAYER
# - NEVER generate text

from typing import Dict, Any
import re


_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


def validate(result: Dict[str, Any]) -> Dict[str, Any]:
    actions = result.get("actions", [])
    facts = result.get("facts", {}) or {}

    # -------- FACT ERRORS --------
    if "fact_error" in facts:
        return {
            "status": "FAIL",
            "reason": facts["fact_error"],
        }

    # -------- TIME --------
    if "TIME_NOW" in actions:
        value = facts.get("time_now")
        if not isinstance(value, str) or not _TIME_RE.match(value):
            return {
                "status": "FAIL",
                "reason": "INVALID_TIME",
            }

    # -------- DAY --------
    if "DAY_TODAY" in actions:
        value = facts.get("day_today")
        if not isinstance(value, str) or not value:
            return {
                "status": "FAIL",
                "reason": "INVALID_DAY",
            }

    # -------- DATE --------
    if "DATE_TODAY" in actions:
        value = facts.get("date_today")
        if not isinstance(value, str) or not value:
            return {
                "status": "FAIL",
                "reason": "INVALID_DATE",
            }

    # -------- ARITHMETIC --------
    if "ARITHMETIC" in actions:
        value = facts.get("arithmetic_value")
        if not isinstance(value, (int, float)):
            return {
                "status": "FAIL",
                "reason": "INVALID_ARITHMETIC",
            }

    # -------- ACTIONS --------
    if not actions:
        return {
            "status": "FAIL",
            "reason": "NO_ACTIONS",
        }

    return {
        "status": "PASS",
    }
