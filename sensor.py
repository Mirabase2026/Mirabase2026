# sensor.py
# =========================
# MIRA BASE – SENSOR (LANGUAGE + MEANING)
# =========================
#
# Sensor:
#  - detects signals (intents) and entities
#  - NEVER decides what to do
#
# Output ONLY:
#  - signals: list[str]
#  - entities: dict
#  - confidence: float

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import re


# =========================
# DATA STRUCTURE
# =========================

@dataclass
class SensorResult:
    signals: List[str]
    entities: Dict[str, Any]
    confidence: float = 1.0


# =========================
# HELPERS
# =========================

def _normalize(text: str) -> str:
    return text.lower().strip()


def _has(text_n: str, pattern: str) -> bool:
    return re.search(pattern, text_n, flags=re.IGNORECASE) is not None


def _extract_arithmetic_expression(text_n: str) -> Optional[str]:
    """
    Finds arithmetic expression inside text.
    Accepts digits, + - * / . ( ) and spaces.
    Example: "kolik je (2+3)*4" -> "(2+3)*4"
    """
    # First: whole string looks like expression
    if re.fullmatch(r"[0-9\+\-\*/\(\)\s\.]+", text_n):
        expr = text_n.strip()
        return expr if re.search(r"\d", expr) else None

    # Otherwise: try to find a chunk that looks like expression
    # Require at least one operator and at least one digit
    m = re.search(r"(\(?\s*\d[\d\s\.\(\)]*(?:[\+\-\*/]\s*\d[\d\s\.\(\)]*)+\)?)", text_n)
    if not m:
        return None

    expr = m.group(1).strip()
    # final sanity
    if re.search(r"\d", expr) and re.search(r"[\+\-\*/]", expr):
        return expr

    return None


# =========================
# SENSOR CORE
# =========================

def sense(text: str, context: Optional[Dict[str, Any]] = None) -> SensorResult:
    text_n = _normalize(text)

    signals: List[str] = []
    entities: Dict[str, Any] = {}
    confidence = 0.95

    # -------------------------
    # GREETINGS
    # -------------------------
    if _has(text_n, r"\b(ahoj|nazdar|čau|cau|zdravím|zdravim)\b"):
        signals.append("GREETING")

    # -------------------------
    # THANKS
    # -------------------------
    if _has(text_n, r"\b(dík|dik|díky|diky|děkuju|dekuju|děkuji|dekuji)\b"):
        signals.append("THANKS")

    # -------------------------
    # USER-STATE (EPISTEMIC LIMIT)
    # "jak mi je", "jak se cítím" = AI to nemůže vědět bez sdělení uživatele
    # -------------------------
    if _has(text_n, r"\b(jak mi je|jak se cítím|jak se citim|jak se teď cítím|jak se ted citim)\b"):
        signals.append("EPISTEMIC_USER_STATE")

    # -------------------------
    # SMALLTALK – ASSISTANT STATE
    # "jak se máš", "jak ti je" = otázka na asistenta
    # -------------------------
    if _has(text_n, r"\b(jak se máš|jak se mas|jak ti je)\b"):
        signals.append("SMALLTALK_STATE")

    # -------------------------
    # TIME
    # -------------------------
    if _has(text_n, r"\b(kolik je hodin|kolik je teď hodin|kolik je ted hodin)\b"):
        signals.append("TIME_NOW")

    # -------------------------
    # DATE
    # -------------------------
    if _has(text_n, r"\b(kolikátého je|kolikateho je|jaké je datum|jake je datum)\b"):
        signals.append("DATE_TODAY")

    # -------------------------
    # DAY
    # -------------------------
    if _has(text_n, r"\b(jaký je dnes den|jaky je dnes den|jaký je den|jaky je den)\b"):
        signals.append("DAY_TODAY")

    # -------------------------
    # ARITHMETIC (standalone or embedded)
    # -------------------------
    expr = _extract_arithmetic_expression(text_n)
    if expr is not None:
        signals.append("ARITHMETIC")
        entities["expression"] = expr

    # -------------------------
    # FALLBACK
    # -------------------------
    if not signals:
        return SensorResult(
            signals=["UNKNOWN"],
            entities={},
            confidence=0.2,
        )

    # Keep order stable, remove duplicates while preserving order
    seen = set()
    signals_unique: List[str] = []
    for s in signals:
        if s not in seen:
            signals_unique.append(s)
            seen.add(s)

    return SensorResult(
        signals=signals_unique,
        entities=entities,
        confidence=confidence,
    )
