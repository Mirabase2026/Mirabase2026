# =========================
# MIRA BASE – EMOTION ENGINE (v1)
# =========================
#
# Output:
# - emotion_signal: CALM | CONFUSED | FRUSTRATED | ENGAGED | IMPAIRED
# - confidence: LOW | MED | HIGH
# - reason_codes: list[str]
#
# Rules:
# - deterministic
# - derived only from STM entries (meaning-only)
# - no text analysis, no sentiment, no LLM
#

from __future__ import annotations

from typing import Dict, Any, List


def _last(stm: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    if not isinstance(stm, list) or n <= 0:
        return []
    return stm[-n:]


def _get(entry: Dict[str, Any], key: str, default=None):
    if isinstance(entry, dict):
        return entry.get(key, default)
    return default


def resolve_emotion_signal(stm_last: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Input: list of STM entries (meaning-only), ideally last N (e.g., 5).
    Each entry may contain:
      - pipeline
      - intent
      - flags (list)
      - epistemic_state
    """
    stm = stm_last if isinstance(stm_last, list) else []
    recent = _last(stm, 5)

    # ---- 1) IMPAIRED: epistemic blocked ----
    for e in reversed(recent):
        ep = _get(e, "epistemic_state")
        if isinstance(ep, str) and ep.upper() == "BLOCKED":
            return {
                "emotion_signal": "IMPAIRED",
                "confidence": "HIGH",
                "reason_codes": ["EPISTEMIC_BLOCKED"],
            }

    # Collect signals
    intents = []
    pipelines = []
    all_flags = []

    for e in recent:
        intent = _get(e, "intent")
        pipeline = _get(e, "pipeline")
        flags = _get(e, "flags", [])

        if isinstance(intent, str):
            intents.append(intent)
        if isinstance(pipeline, str):
            pipelines.append(pipeline)
        if isinstance(flags, list):
            all_flags.extend([f for f in flags if isinstance(f, str)])

    # ---- 2) FRUSTRATED: repeated LOW_SIGNAL / STALL_RISK ----
    low_signal_count = sum(1 for f in all_flags if f == "LOW_SIGNAL")
    stall_risk_count = sum(1 for f in all_flags if f == "STALL_RISK")

    if low_signal_count >= 2:
        return {
            "emotion_signal": "FRUSTRATED",
            "confidence": "HIGH",
            "reason_codes": ["LOW_SIGNAL"],
        }

    if stall_risk_count >= 1 and len(recent) >= 2:
        return {
            "emotion_signal": "FRUSTRATED",
            "confidence": "MED",
            "reason_codes": ["STALL_RISK"],
        }

    # ---- 3) CONFUSED: same intent repeated 3 times, typically with FALLBACK/GUARD ----
    if len(intents) >= 3:
        last3 = intents[-3:]
        if last3[0] == last3[1] == last3[2]:
            return {
                "emotion_signal": "CONFUSED",
                "confidence": "HIGH",
                "reason_codes": ["REPEAT_INTENT"],
            }

    # ---- 4) ENGAGED: varied intents in last 3 and stable pipeline FACT ----
    if len(intents) >= 3:
        last3 = intents[-3:]
        if len(set(last3)) == 3:
            # prefer FACT streaks as engagement indicator
            last3_p = pipelines[-3:] if len(pipelines) >= 3 else []
            if last3_p and all(p == "FACT" for p in last3_p):
                return {
                    "emotion_signal": "ENGAGED",
                    "confidence": "HIGH",
                    "reason_codes": ["VARIED_INTENTS", "FACT_STREAK"],
                }
            return {
                "emotion_signal": "ENGAGED",
                "confidence": "MED",
                "reason_codes": ["VARIED_INTENTS"],
            }

    # ---- 5) CALM default ----
    return {
        "emotion_signal": "CALM",
        "confidence": "MED",
        "reason_codes": [],
    }
