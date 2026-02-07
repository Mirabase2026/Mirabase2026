# =========================
# MIRA BASE – BRAIN (MEANING ONLY)
# =========================
#
# This file MUST NOT:
# - produce natural language output
# - contain any user-facing strings
# - call discourse/stylistic renderers
# - execute "actions" that generate text
#
# It MAY:
# - decide intent, actions, source
# - compute deterministic facts (data)
# - output semantic payload + constraints

from typing import Dict, Optional, Any, List

from sensor import sense
from attention_engine import resolve_attention
from disambiguation_engine import resolve_disambiguation
from emotion_engine import resolve_emotion
from personal_fact_engine import resolve_personal_fact
from epistemic_engine import resolve_epistemic
from security_engine import resolve_security
from response_planner import plan_actions
from fact_engine import resolve_facts
from stm import get_stm, update_stm
from ltm import load_ltm
from chrono_context import build_chrono_context
from homeostasis_engine import resolve_homeostasis
from social import handle as social_handle
from meta_engine import resolve_meta
from prediction_guard import resolve_prediction_guard
from response_source_router import resolve_response_source

from contract_adapter import to_contract
from response_contract import ResponseContract


# ---------- normalizers ----------
def D(x):
    return x if isinstance(x, dict) else {}

def L(x):
    return x if isinstance(x, list) else []


# ---------- helpers ----------
def _mk_result(
    *,
    pipeline: str,
    intent: Any,
    actions: List[Any],
    emotion: Any,
    epistemic: Dict[str, Any],
    source: Optional[str] = None,
    reason: Optional[str] = None,
    constraints: Optional[List[str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    facts: Optional[Dict[str, Any]] = None,
    chrono: Optional[Dict[str, Any]] = None,
    entities: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Strictly semantic result.
    NO natural language keys. NO 'text'.
    """
    out: Dict[str, Any] = {
        "pipeline": pipeline,
        "intent": intent,
        "actions": actions,
        "emotion": emotion,
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


# =========================================================
# PIPELINE (MEANING ONLY)
# =========================================================
def run_pipeline(user_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

    ctx: Dict[str, Any] = {}
    seed = D(context)

    ctx["timezone"] = seed.get("timezone", "Europe/Prague")
    ctx["metrics"] = {"turn_count": seed.get("metrics", {}).get("turn_count", 0) + 1}
    ctx["personal"] = load_ltm()

    stm = D(get_stm())
    history = L(stm.get("history"))
    last_intents = L(stm.get("last_intents"))

    # SENSOR
    sensor = sense(user_text, ctx)

    # ATTENTION
    attention = D(
        resolve_attention(
            {
                "signals": sensor.signals,
                "entities": sensor.entities,
                "confidence": sensor.confidence,
            },
            user_text,
        )
    )

    entities = D(attention.get("entities"))
    secondary_intents = L(attention.get("secondary_intents"))

    # DISAMBIGUATION
    disamb = D(resolve_disambiguation(attention))
    primary_intent = disamb.get("resolved_intent") or attention.get("primary_intent")

    # EMOTION + PERSONAL
    emotion = resolve_emotion(attention)
    resolve_personal_fact(primary_intent, entities, user_text)

    # EPISTEMIC
    epistemic = D(resolve_epistemic(attention, user_text))
    epistemic_state = epistemic.get("epistemic_state")

    if epistemic_state and epistemic_state not in ("OK", "PASS"):
        result = _mk_result(
            pipeline="EPISTEMIC",
            intent=primary_intent,
            actions=[],
            emotion=emotion,
            epistemic=epistemic,
            reason="EPISTEMIC_EARLY_EXIT",
            constraints=["NO_GENERATION", "NO_MEMORY_WRITE"],
            payload={
                "kind": "EPISTEMIC",
                "value": {"epistemic_state": epistemic_state},
            },
            facts={},
            chrono=build_chrono_context({}),
            entities=entities,
        )
        update_stm(result)
        return result

    # SECURITY
    security = D(resolve_security(attention, user_text))
    if security.get("security_state") == "BLOCKED":
        result = _mk_result(
            pipeline="SECURITY",
            intent=primary_intent,
            actions=[],
            emotion=emotion,
            epistemic=epistemic,
            reason="SECURITY_BLOCKED",
            constraints=["NO_GENERATION", "NO_MEMORY_WRITE"],
            payload={"kind": "SECURITY", "value": security},
            facts={},
            chrono=build_chrono_context({}),
            entities=entities,
        )
        update_stm(result)
        return result

    # HOMEOSTASIS
    ctx["homeostasis"] = resolve_homeostasis(
        turn_count=ctx["metrics"]["turn_count"],
        recent_intents=last_intents,
    )

    # SOCIAL
    social = social_handle(user_text)
    if isinstance(social, dict):
        result = _mk_result(
            pipeline="SOCIAL",
            intent=primary_intent,
            actions=["SOCIAL"],
            emotion=emotion,
            epistemic=epistemic,
            reason="SOCIAL_HANDLER",
            constraints=["NO_MEMORY_WRITE"],
            payload={"kind": "SOCIAL", "value": social},
            facts={},
            chrono=build_chrono_context({}),
            entities=entities,
        )
        update_stm(result)
        return result

    # ACTIONS
    actions = L(plan_actions(primary_intent, secondary_intents, entities))

    # META
    meta = D(resolve_meta(last_results=history))
    ctx["meta"] = meta

    # GUARD
    guard = D(
        resolve_prediction_guard(
            attention=attention,
            epistemic=epistemic,
            meta=meta,
            planned_actions=actions,
        )
    )
    flags = L(guard.get("flags"))

    if "AVOID_MODEL" in flags:
        result = _mk_result(
            pipeline="GUARD",
            intent=primary_intent,
            actions=actions,
            emotion=emotion,
            epistemic=epistemic,
            reason="AVOID_MODEL",
            constraints=["NO_GENERATION", "NO_MEMORY_WRITE"],
            payload={"kind": "GUARD", "value": {"flags": flags}},
            facts={},
            chrono=build_chrono_context({}),
            entities=entities,
        )
        update_stm(result)
        return result

    if "LOW_SIGNAL" in flags:
        result = _mk_result(
            pipeline="GUARD",
            intent=primary_intent,
            actions=actions,
            emotion=emotion,
            epistemic=epistemic,
            reason="LOW_SIGNAL",
            constraints=["NO_GENERATION", "NO_MEMORY_WRITE"],
            payload={"kind": "GUARD", "value": {"flags": flags}},
            facts={},
            chrono=build_chrono_context({}),
            entities=entities,
        )
        update_stm(result)
        return result

    if "STALL_RISK" in flags:
        result = _mk_result(
            pipeline="GUARD",
            intent=primary_intent,
            actions=actions,
            emotion=emotion,
            epistemic=epistemic,
            reason="STALL_RISK",
            constraints=["NO_GENERATION", "NO_MEMORY_WRITE", "SILENT_EXIT"],
            payload={"kind": "GUARD", "value": {"flags": flags}},
            facts={},
            chrono=build_chrono_context({}),
            entities=entities,
        )
        update_stm(result)
        return result

    # ROUTER
    route = D(
        resolve_response_source(
            actions=actions,
            attention=attention,
            entities=entities,
            context=ctx,
        )
    )
    source = route.get("source")

    if source == "DETERMINISTIC":
        facts = D(resolve_facts(actions, entities, ctx))
        chrono = build_chrono_context(facts)

        result = _mk_result(
            pipeline="FACT",
            intent=primary_intent,
            actions=actions,
            emotion=emotion,
            epistemic=epistemic,
            source="DETERMINISTIC",
            reason="FACTS_COMPUTED",
            constraints=["NO_GENERATION", "NO_MEMORY_WRITE"],
            payload={"kind": "FACTS_BLOB", "value": facts},
            facts=facts,
            chrono=chrono,
            entities=entities,
        )
        update_stm(result)
        return result

    result = _mk_result(
        pipeline="FALLBACK",
        intent=primary_intent,
        actions=actions,
        emotion=emotion,
        epistemic=epistemic,
        source=source,
        reason="NO_DETERMINISTIC_PATH",
        constraints=["NO_GENERATION", "NO_MEMORY_WRITE"],
        payload={
            "kind": "FALLBACK",
            "value": {
                "source": source,
                "actions": actions,
            },
        },
        facts={},
        chrono=build_chrono_context({}),
        entities=entities,
    )
    update_stm(result)
    return result


def run(user_text: str, context: Optional[Dict[str, Any]] = None) -> ResponseContract:
    return to_contract(run_pipeline(user_text, context))
