# discourse_engine.py
# =========================
# DISCOURSE / RESPONSE COMPOSITION (KROK 7B)
# =========================
#
# Úkol:
# - SLOŽIT finální odpověď (pozdrav + fakta + oslovení) podle pravidel 7.1–7.5
# - NEROZHODOVAT (nemění intent/pipeline/actions/facts)
# - NEPOČÍTAT (žádné facty ani model)
#
# Vstupy (preferované):
# - context: dict (session, personal, emotion…)
# - raw_text: str (text z ACTION layeru)
# - result: dict (pipeline, actions, intent, ... )  [volitelné]
#
# Backward compatible:
# - apply_discourse(context, raw_text) funguje i bez result,
#   pokud jsou pipeline/actions v contextu (context["pipeline"], context["actions"])
#
# Pravidla:
# 7.1 FIRST CONTACT ADDRESSING
# 7.2 GREETING + FACT MERGE
# 7.3 GREETING DOMINANCE
# 7.4 EPISTEMIC LIMIT (bez faktů)
# 7.5 EMOTION–NAME AFFINITY (jen občas)

from __future__ import annotations
from typing import Any, Dict, List, Optional


def _get_session(context: Dict[str, Any]) -> Dict[str, Any]:
    session = context.get("session")
    return session if isinstance(session, dict) else {}


def _is_first_turn(context: Dict[str, Any]) -> bool:
    session = _get_session(context)
    if isinstance(session.get("first_turn"), bool):
        return session["first_turn"]
    if isinstance(context.get("first_turn"), bool):
        return context["first_turn"]
    return False


def _get_person_name(context: Dict[str, Any]) -> Optional[str]:
    personal = context.get("personal")
    if isinstance(personal, dict):
        name = personal.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return None


def _get_emotion_state(context: Dict[str, Any], result: Optional[Dict[str, Any]]) -> str:
    if isinstance(result, dict):
        emo = result.get("emotion")
        if isinstance(emo, dict):
            st = emo.get("emotion_state")
            if isinstance(st, str) and st.strip():
                return st.strip().upper()
    emo = context.get("emotion")
    if isinstance(emo, dict):
        st = emo.get("emotion_state")
        if isinstance(st, str) and st.strip():
            return st.strip().upper()
    return "NEUTRAL"


def _get_actions(context: Dict[str, Any], result: Optional[Dict[str, Any]]) -> List[str]:
    if isinstance(result, dict):
        acts = result.get("actions")
        if isinstance(acts, list):
            return [str(a) for a in acts]
    acts = context.get("actions")
    if isinstance(acts, list):
        return [str(a) for a in acts]
    return []


def _starts_with_greeting(text: str) -> bool:
    t = text.strip().lower()
    return t.startswith("ahoj")


def _ensure_trailing_period(text: str) -> str:
    t = text.strip()
    if not t:
        return t
    if t.endswith((".", "!", "?")):
        return t
    return t + "."


def apply_discourse(context: Dict[str, Any], raw_text: str, result: Optional[Dict[str, Any]] = None) -> str:
    raw_text = "" if raw_text is None else str(raw_text).strip()
    actions = _get_actions(context, result)
    first_turn = _is_first_turn(context)
    name = _get_person_name(context)
    emotion_state = _get_emotion_state(context, result)

    has_greet = "GREET_SIMPLE" in actions
    is_fact_text = raw_text.lower().startswith("je ") or raw_text.lower().startswith("dnes je ")

    if has_greet and not _starts_with_greeting(raw_text):
        raw_text = "Ahoj. " + raw_text

    if first_turn and name and raw_text.lower().startswith("ahoj"):
        if f"{name.lower()}" not in raw_text.lower():
            raw_text = raw_text.replace("Ahoj", f"Ahoj, {name}", 1)

    if name and not first_turn and emotion_state in ("POSITIVE", "HAPPY"):
        if not is_fact_text and not _starts_with_greeting(raw_text):
            raw_text = f"{name}, {raw_text}"

    return _ensure_trailing_period(raw_text)
