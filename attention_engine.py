# attention_engine.py
# =========================
# MIRA BASE – ATTENTION ENGINE (v1)
# =========================
#
# Responsibilities:
# - lightweight focus + secondary intent signals
# - may enrich entities (e.g., arithmetic expression)
# - NO text generation

from __future__ import annotations

import re
from typing import Any, Dict, List


def _D(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _L(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def _norm(s: str) -> str:
    s = "" if s is None else str(s)
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


_ARITH_RE = re.compile(r"([0-9][0-9\s\+\-\*\/\(\)\.]*[0-9])")
_TIME_RE = re.compile(r"\b(kolik je hodin|kolik je hodin\?|cas je kolik|cas)\b", re.IGNORECASE)
_DATE_RE = re.compile(r"\b(jake je dnes datum|jaké je dnes datum|dnesni datum|datum)\b", re.IGNORECASE)
_DAY_RE = re.compile(r"\b(jaky je dnes den|jaký je dnes den|jaky je dneska den|jaký je dneska den|den je dnes)\b", re.IGNORECASE)
_GREET_RE = re.compile(r"^(ahoj|cau|čau|dobry den|dobrý den|zdravim|zdravím)\b", re.IGNORECASE)


def resolve_attention(sensor_pack: Dict[str, Any], user_text: str) -> Dict[str, Any]:
    sensor_pack = _D(sensor_pack)
    entities = _D(sensor_pack.get("entities"))
    signals = _L(sensor_pack.get("signals"))
    confidence = sensor_pack.get("confidence", 1.0)

    text = _norm(user_text)

    secondary_intents: List[str] = []

    # greeting
    if _GREET_RE.search(text):
        secondary_intents.append("GREETING")

    # time/date/day
    if _TIME_RE.search(text):
        secondary_intents.append("TIME_QUERY")
    if _DATE_RE.search(text):
        secondary_intents.append("DATE_QUERY")
    if _DAY_RE.search(text):
        secondary_intents.append("DAY_QUERY")

    # arithmetic expression
    m = _ARITH_RE.search(text)
    if m:
        expr = m.group(1)
        expr = expr.strip()
        # keep only allowed chars (hard sanitize)
        expr = re.sub(r"[^0-9\+\-\*\/\(\)\.\s]", "", expr)
        expr = re.sub(r"\s+", " ", expr).strip()
        if expr:
            entities["expression"] = expr
            secondary_intents.append("ARITH_QUERY")

    return {
        "primary_intent": None,
        "secondary_intents": secondary_intents,
        "entities": entities,
        "signals": signals,
        "confidence": confidence,
    }
