# =========================
# ACTION LAYER – TEXT OUTPUT
# =========================

from typing import Dict, Any, Optional
from discourse_engine import apply_discourse


def resolve_action(result: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
    if context is None:
        context = {}

    pipeline = result.get("pipeline")
    actions = result.get("actions") or []
    facts = result.get("facts") or {}

    text = ""

    # -------------------------
    # SOCIAL
    # -------------------------
    if pipeline == "SOCIAL":
        if "GREET_SIMPLE" in actions:
            text = "Ahoj."
        elif "THANK_SIMPLE" in actions:
            text = "Prosím."
        elif "SMALLTALK_STATE_SIMPLE" in actions:
            text = "Mám se dobře."
        elif "EPISTEMIC_LIMIT_USER_STATE" in actions:
            text = "To nemůžu vědět. Řekni mi, jak ti je."
        elif "CLARIFY" in actions:
            text = "Můžeš to upřesnit?"
        else:
            text = "Tomu nerozumím."

    # -------------------------
    # FACT
    # -------------------------
    elif pipeline == "FACT":
        if "time_now" in facts:
            text = f"je {facts['time_now']}."
        elif "day_today" in facts:
            text = f"dnes je {facts['day_today']}."
        elif "date_today" in facts:
            text = f"dnes je {facts['date_today']}."
        elif "arithmetic_value" in facts:
            text = str(facts["arithmetic_value"])
        else:
            text = "Tomu nerozumím."

    # -------------------------
    # SECURITY / FALLBACK
    # -------------------------
    else:
        text = "Tomu nerozumím."

    # =================================================
    # 🔑 FIRST TURN PERSONAL NAME – SAFE FINAL HOOK
    # =================================================
    try:
        session = context.get("session", {})
        personal = context.get("personal", {})

        if (
            session.get("first_turn") is True
            and "GREET_SIMPLE" in actions
            and isinstance(personal, dict)
        ):
            name = personal.get("name")
            if isinstance(name, str) and name.strip():
                text = f"{name}, {text.lower()}"
    except Exception:
        pass

    # -------------------------
    # DISCOURSE (unchanged)
    # -------------------------
    return apply_discourse(context, text, result)
