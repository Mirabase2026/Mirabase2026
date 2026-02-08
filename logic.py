# logic.py
# =========================
# MIRA BASE – BRAIN (v7)
# =========================

from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
import uuid
import re

from sensor import sense
from attention_engine import resolve_attention
from disambiguation_engine import resolve_disambiguation
from emotion_engine import resolve_emotion_signal
from personal_fact_engine import resolve_personal_fact
from epistemic_engine import resolve_epistemic
from security_engine import resolve_security
from response_planner import plan_actions
from fact_engine import resolve_facts
from stm import get_last, append_entry
from ltm import load_ltm, set_preference
from chrono_context import build_chrono_context
from homeostasis_engine import resolve_homeostasis
from social import handle as social_handle
from meta_engine import resolve_meta
from prediction_guard import resolve_prediction_guard
from response_source_router import resolve_response_source

from contract_adapter import to_contract
from response_contract import ResponseContract


# ---------- helpers ----------
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mk_result(
    *,
    pipeline: str,
    intent: Any,
    actions: List[Any],
    epistemic: Dict[str, Any],
    source: Optional[str] = None,
    reason: Optional[str] = None,
    constraints: Optional[List[str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    facts: Optional[Dict[str, Any]] = None,
    chrono: Optional[Dict[str, Any]] = None,
    entities: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "pipeline": pipeline,
        "intent": intent,
        "actions": actions,
        "epistemic": epistemic,
    }
    if source is not None:
        out["source"] = source
    if reason is not None:
        out["reason"] = reason
    if constraints is not None:
        out["constraints"] = constraints
    if payload is not None:
        out["payload"] = payload
    if facts is not None:
        out["facts"] = facts
    if chrono is not None:
        out["chrono"] = chrono
    if entities is not None:
        out["entities"] = entities
    return out


def _append_stm(result: Dict[str, Any], ctx: Dict[str, Any]) -> None:
    entry = {
        "turn_id": str(uuid.uuid4()),
        "user_id": ctx.get("user_id"),
        "timestamp": _now(),
        "pipeline": result.get("pipeline"),
        "intent": result.get("intent"),
        "actions": result.get("actions", []),
        "source": result.get("source"),
        "epistemic_state": result.get("epistemic", {}).get("epistemic_state"),
        "flags": result.get("constraints", []),
        "emotion_signal": ctx.get("emotion", {}).get("emotion_signal"),
    }
    append_entry(entry)


def _social_payload_text(text: str) -> Dict[str, Any]:
    return {"kind": "SOCIAL", "value": {"text": text}}


# ---------- COMMAND PARSER ----------
CMD_PATTERNS = {
    "communication_style": re.compile(r"^\s*styl\s*:\s*(\w+)\s*$", re.IGNORECASE),
    "verbosity": re.compile(r"^\s*verbosity\s*:\s*(\d+)\s*$", re.IGNORECASE),
    "response_language": re.compile(r"^\s*jazyk\s*:\s*(\w+)\s*$", re.IGNORECASE),
}


def _try_command(user_text: str, user_id: str) -> Optional[Dict[str, Any]]:
    for key, rx in CMD_PATTERNS.items():
        m = rx.match(user_text)
        if m:
            val = m.group(1)
            if key == "verbosity":
                try:
                    val = int(val)
                except ValueError:
                    return None
            ok = set_preference(user_id, key, val)
            if not ok:
                return None
            return _mk_result(
                pipeline="COMMAND",
                intent="SET_PREFERENCE",
                actions=["ACK"],
                epistemic={"epistemic_state": "OK"},
                source="SOCIAL",
                reason="COMMAND_APPLIED",
                constraints=["NO_MEMORY_WRITE"],
                payload=_social_payload_text("OK."),
                facts={},
                chrono=build_chrono_context({}),
                entities={},
            )
    return None


# =========================================================
# PIPELINE
# =========================================================
def run_pipeline(user_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ctx: Dict[str, Any] = {}
    seed = context or {}

    # identity
    ctx["user_id"] = seed.get("user_id", "default")
    ctx["timezone"] = seed.get("timezone", "Europe/Prague")
    ctx["metrics"] = {"turn_count": seed.get("metrics", {}).get("turn_count", 0) + 1}

    # ---- COMMAND short-circuit (A) ----
    cmd = _try_command(user_text, ctx["user_id"])
    if cmd:
        _append_stm(cmd, ctx)
        return cmd

    # memory snapshot
    ctx["personal"] = load_ltm(ctx["user_id"])

    # SENSOR
    sensor = sense(user_text, ctx)

    # ATTENTION
    attention = resolve_attention(
        {"signals": sensor.signals, "entities": sensor.entities, "confidence": sensor.confidence},
        user_text,
    )

    entities = attention.get("entities", {})
    secondary_intents = attention.get("secondary_intents", [])

    # DISAMBIGUATION
    disamb = resolve_disambiguation(attention)
    primary_intent = disamb.get("resolved_intent") or attention.get("primary_intent")

    # PERSONAL FACTS
    resolve_personal_fact(primary_intent, entities, user_text, ctx)

    # EPISTEMIC
    epistemic = resolve_epistemic(attention, user_text)
    if epistemic.get("epistemic_state") not in ("OK", "PASS"):
        result = _mk_result(
            pipeline="EPISTEMIC",
            intent=primary_intent,
            actions=[],
            epistemic=epistemic,
            constraints=["NO_GENERATION", "NO_MEMORY_WRITE"],
            payload={},
            facts={},
            chrono=build_chrono_context({}),
            entities=entities,
        )
        _append_stm(result, ctx)
        return result

    # SECURITY
    security = resolve_security(attention, user_text)
    if security.get("security_state") == "BLOCKED":
        result = _mk_result(
            pipeline="SECURITY",
            intent=primary_intent,
            actions=[],
            epistemic=epistemic,
            constraints=["NO_GENERATION", "NO_MEMORY_WRITE"],
            payload={},
            facts={},
            chrono=build_chrono_context({}),
            entities=entities,
        )
        _append_stm(result, ctx)
        return result

    # EMOTION (from STM)
    recent_stm = get_last(ctx["user_id"], 5)
    ctx["emotion"] = resolve_emotion_signal(recent_stm)

    # HOMEOSTASIS
    ctx["homeostasis"] = resolve_homeostasis(
        turn_count=ctx["metrics"]["turn_count"],
        recent_intents=[e.get("intent") for e in recent_stm],
    )

    # SOCIAL (deterministic)
    social = social_handle(user_text, ctx)
    if isinstance(social, dict):
        result = _mk_result(
            pipeline="SOCIAL",
            intent=social.get("intent"),
            actions=["SOCIAL"],
            epistemic=epistemic,
            source="SOCIAL",
            reason="SOCIAL_HANDLER",
            constraints=["NO_MEMORY_WRITE"],
            payload={"kind": "SOCIAL", "value": {"text": social.get("text")}},
            facts={},
            chrono=build_chrono_context({}),
            entities=entities,
        )
        _append_stm(result, ctx)
        return result

    # ACTIONS
    actions = plan_actions(primary_intent, secondary_intents, entities)

    # META / GUARD
    ctx["meta"] = resolve_meta(last_results=recent_stm)
    guard = resolve_prediction_guard(
        attention=attention,
        epistemic=epistemic,
        meta=ctx["meta"],
        planned_actions=actions,
    )
    flags = guard.get("flags", [])

    if flags:
        result = _mk_result(
            pipeline="GUARD",
            intent=primary_intent,
            actions=actions,
            epistemic=epistemic,
            constraints=flags,
            payload={},
            facts={},
            chrono=build_chrono_context({}),
            entities=entities,
        )
        _append_stm(result, ctx)
        return result

    # ROUTER
    route = resolve_response_source(actions=actions, attention=attention, entities=entities, context=ctx)
    source = route.get("source")

    if source == "DETERMINISTIC":
        facts = resolve_facts(actions, entities, ctx)
        result = _mk_result(
            pipeline="FACT",
            intent=primary_intent,
            actions=actions,
            epistemic=epistemic,
            source="DETERMINISTIC",
            payload={},
            facts=facts,
            chrono=build_chrono_context(facts),
            entities=entities,
        )
        _append_stm(result, ctx)
        return result

    result = _mk_result(
        pipeline="FALLBACK",
        intent=primary_intent,
        actions=actions,
        epistemic=epistemic,
        source=source,
        constraints=["NO_GENERATION"],
        payload={},
        facts={},
        chrono=build_chrono_context({}),
        entities=entities,
    )
    _append_stm(result, ctx)
    return result


def run(user_text: str, context: Optional[Dict[str, Any]] = None) -> ResponseContract:
    return to_contract(run_pipeline(user_text, context))
