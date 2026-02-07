# =========================
# MIRA BASE – SECURITY ENGINE (ONLY SELF-HARM)
# =========================

from typing import Dict, Any


_SELF_HARM_KEYWORDS = (
    "sebevražda",
    "zabít se",
    "chci zemřít",
    "nechci žít",
    "ukončit život",
)


def resolve_security(sensor_info: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    t = (raw_text or "").lower()
    for k in _SELF_HARM_KEYWORDS:
        if k in t:
            return {"security_state": "BLOCKED", "reason": "SELF_HARM"}
    return {"security_state": "SAFE"}
