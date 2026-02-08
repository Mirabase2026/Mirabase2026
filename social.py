# social.py
# =========================
# MIRA BASE – SOCIAL v2.2 (DETERMINISTIC + EMOTION AWARE)
# =========================

from __future__ import annotations

import json
import os
import random
import re
from pathlib import Path
from typing import Any, Dict, Optional


# ---------- helpers ----------
def _n(text: str) -> str:
    return (text or "").lower().strip()


def _has(text_n: str, pattern: str) -> bool:
    return re.search(pattern, text_n, flags=re.IGNORECASE) is not None


def _get_user_id(context: Optional[Dict[str, Any]]) -> str:
    if isinstance(context, dict):
        uid = context.get("user_id")
        if isinstance(uid, str) and uid.strip():
            return uid.strip()
    return "default"


def _get_emotion(context: Optional[Dict[str, Any]]) -> str:
    if isinstance(context, dict):
        emo = context.get("emotion")
        if isinstance(emo, dict):
            sig = emo.get("emotion_signal")
            if isinstance(sig, str):
                return sig
    return "CALM"


def _admin_id() -> Optional[str]:
    v = os.getenv("MIRABASE_ADMIN_ID")
    return v.strip() if isinstance(v, str) and v.strip() else None


def _profile_path(user_id: str) -> Path:
    return Path("users") / user_id / "profile.json"


def _load_profile(user_id: str) -> Dict[str, Any]:
    p = _profile_path(user_id)
    if not p.exists():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _pick(pool: list[str]) -> str:
    if not pool:
        return ""
    if len(pool) == 1:
        return pool[0]
    return random.choice(pool)


# ---------- SOCIAL CONFIG ----------
SOCIAL_PATTERNS: Dict[str, Dict[str, Any]] = {
    "GREETING": {
        "triggers": r"\b(ahoj|nazdar|čau|cau|zdravím|zdravim|dobrý den|dobry den)\b",
        "responses": {
            "brief": ["Ahoj."],
            "calm": ["Ahoj."],
            "neutral": ["Ahoj."],
            "special": ["Ahoj stvořiteli."],
        },
    },
    "THANKS": {
        "triggers": r"\b(dík|dik|díky|diky|děkuju|dekuju|děkuji|dekuji)(\s+moc)?\b",
        "responses": {
            "brief": ["Rádo se stalo."],
            "calm": ["V pořádku."],
            "neutral": ["Rádo se stalo."],
            "special": ["Pro tebe vždycky."],
        },
    },
    "BYE": {
        "triggers": r"\b(čau|cau|měj se|mej se|zatím|zatim|na shledanou|nashle|dobrou)\b",
        "responses": {
            "brief": ["Čau."],
            "calm": ["Čau."],
            "neutral": ["Na shledanou."],
            "special": ["Čau stvořiteli."],
        },
    },
    "ACK": {
        "triggers": r"\b(ok|okej|okey|ok\s+ok|jasně|jasne|rozumím|rozumim|chápu|chapu|beru|platí|plati)\b",
        "responses": {
            "brief": ["OK."],
            "calm": ["OK."],
            "neutral": ["Rozumím."],
            "special": ["Rozumím, stvořiteli."],
        },
    },
}

INTENT_ORDER = ["BYE", "THANKS", "GREETING", "ACK"]


def _resolve_tone(user_id: str, profile: Dict[str, Any], emotion: str) -> str:
    admin = _admin_id()
    if admin and user_id == admin:
        return "special"

    # Emotion override (VERY gentle)
    if emotion in ("FRUSTRATED", "IMPAIRED"):
        return "calm"
    if emotion == "CONFUSED":
        return "neutral"

    if profile.get("communication_style") == "brief":
        return "brief"

    return "brief"


def detect_intent(user_text: str) -> Optional[str]:
    t = _n(user_text)
    for intent in INTENT_ORDER:
        if _has(t, SOCIAL_PATTERNS[intent]["triggers"]):
            return intent
    return None


def handle(user_text: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    intent = detect_intent(user_text)
    if not intent:
        return None

    user_id = _get_user_id(context)
    emotion = _get_emotion(context)
    profile = _load_profile(user_id)

    tone = _resolve_tone(user_id, profile, emotion)
    responses = SOCIAL_PATTERNS[intent]["responses"]
    pool = responses.get(tone) or responses["brief"]

    return {
        "handled": True,
        "version": "SOCIAL_V2.2",
        "intent": intent,
        "text": _pick(pool),
        "skip_llm": True,
        "user_id": user_id,
        "tone": tone,
        "emotion": emotion,
    }
