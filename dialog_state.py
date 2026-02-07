# =========================
# MIRA BASE – BRAIN (ROUTER)
# =========================

from typing import Dict, Optional, Any, List

from sensor import sense, SensorResult
from attention_engine import resolve_attention
from fact_engine import resolve_time, resolve_date, resolve_day
from emotion_engine import resolve_emotion
from security_engine import resolve_security
from response_planner import plan_actions
from validator import validate
from dialog_state import DialogState


# --------
# GLOBAL dialog state (CLI / single-session)
# --------
dialog_state = DialogState()


def run_pipeline(user_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # -------------------------
    # SENSOR
    # -------------------------
    sensor_result: SensorResult = sense(user_text, context)
    intent = sensor_result.intent
    entities = sensor_result.entities

    # -------------------------
    # ATTENTION
    # -------------------------
    attention = resolve_attention(
        {
            "intent": intent,
            "entities": entities,
            "confidence": sensor_result.confidence,
        },
        user_text,
    )

    focus_intent = attention.get("focus_intent", intent)

    # -------------------------
    # EMOTION
    # -------------------------
    emotion = resolve_emotion({
        "intent": focus_intent,
        "confidence": sensor_result.confidence,
    })

    # -------------------------
    # SECURITY
    # -------------------------
    security = resolve_security(
        {"intent": focus_intent},
        user_text,
    )

    if security["security_state"] == "BLOCKED":
        return {
            "pipeline": "SECURITY",
            "actions": ["SECURITY_BLOCK"],
            "intent": focus_intent,
            "emotion": emotion,
            "security": security,
        }

    # -------------------------
    # RESPONSE PLANNING
    # -------------------------
    actions: List[str] = plan_actions(focus_intent, entities)

    # Suppress repeated greeting in dialog
    if dialog_state.should_suppress_greeting():
        actions = [a for a in actions if a != "GREET_SIMPLE"]

    result: Dict[str, Any] = {
        "pipeline": "FACT" if focus_intent in ("TIME_NOW", "DAY_TODAY", "DATE_TODAY", "ARITHMETIC") else "SOCIAL",
        "actions": actions,
        "intent": focus_intent,
        "emotion": emotion,
        "security": security,
    }

    # -------------------------
    # FACT ENGINE
    # -------------------------
    if focus_intent == "TIME_NOW":
        result.update(resolve_time(context))

    elif focus_intent == "DAY_TODAY":
        result.update(resolve_day(context))

    elif focus_intent == "DATE_TODAY":
        result.update(resolve_date(context))

    elif focus_intent == "ARITHMETIC":
        result["value"] = None
        result["expression"] = entities.get("expression")

    # -------------------------
    # VALIDATOR
    # -------------------------
    validation = validate(result)

    if validation["status"] != "PASS":
        return {
            "pipeline": "VALIDATOR",
            "actions": ["MODEL_FALLBACK"],
            "intent": focus_intent,
            "emotion": emotion,
            "security": security,
            "validation": validation,
        }

    # -------------------------
    # DIALOG STATE UPDATE
    # -------------------------
    dialog_state.update(
        intent=focus_intent,
        pipeline=result["pipeline"],
        entities=entities,
    )

    return result
