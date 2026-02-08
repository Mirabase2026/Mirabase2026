# =========================
# MIRA BASE – PERSONAL FACT ENGINE (v1)
# =========================
#
# Responsibilities:
# - detect explicit personal facts in user_text
# - write deterministic PERSONAL_FACT into LTM
# - multi-user aware (user_id scope)
#
# Hard rules:
# - NO natural language output
# - NO inference
# - ONLY explicit statements -> facts
#

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from ltm import upsert_fact


_NAME_PATTERNS = [
    # Czech
    re.compile(r"^\s*jmenuji\s+se\s+([A-Za-zÁ-Žá-ž\-']+)\s*$", re.IGNORECASE),
    re.compile(r"^\s*jmenuju\s+se\s+([A-Za-zÁ-Žá-ž\-']+)\s*$", re.IGNORECASE),
    re.compile(r"^\s*já\s+jsem\s+([A-Za-zÁ-Žá-ž\-']+)\s*$", re.IGNORECASE),
    # English
    re.compile(r"^\s*my\s+name\s+is\s+([A-Za-z\-']+)\s*$", re.IGNORECASE),
    re.compile(r"^\s*i'?m\s+([A-Za-z\-']+)\s*$", re.IGNORECASE),
    # Spanish
    re.compile(r"^\s*me\s+llamo\s+([A-Za-zÁ-Žá-ž\-']+)\s*$", re.IGNORECASE),
    re.compile(r"^\s*soy\s+([A-Za-zÁ-Žá-ž\-']+)\s*$", re.IGNORECASE),
    # German
    re.compile(r"^\s*ich\s+hei(?:ß|ss)e\s+([A-Za-zÄÖÜäöüß\-']+)\s*$", re.IGNORECASE),
]


_LOCALE_PATTERNS = [
    # explicit locale / language preference statements (kept minimal and explicit)
    re.compile(r"^\s*preferuji\s+(.+)\s*$", re.IGNORECASE),      # cz: "Preferuji angličtinu"
    re.compile(r"^\s*prefiero\s+(.+)\s*$", re.IGNORECASE),       # es
    re.compile(r"^\s*i\s+prefer\s+(.+)\s*$", re.IGNORECASE),     # en
    re.compile(r"^\s*ich\s+bevorzuge\s+(.+)\s*$", re.IGNORECASE) # de
]


def _pick_user_id(ctx: Optional[Dict[str, Any]]) -> str:
    if isinstance(ctx, dict) and isinstance(ctx.get("user_id"), str) and ctx["user_id"].strip():
        return ctx["user_id"].strip()
    return "default"


def resolve_personal_fact(
    primary_intent: Any,
    entities: Dict[str, Any],
    user_text: str,
    ctx: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Detects explicit user facts and stores them in LTM as PERSONAL_FACT.
    Side-effect only. Deterministic.
    """
    text = (user_text or "").strip()
    if not text:
        return

    user_id = _pick_user_id(ctx)
    locale = None
    if isinstance(ctx, dict):
        loc = ctx.get("locale")
        if isinstance(loc, str) and loc.strip():
            locale = loc.strip()

    # -------- explicit NAME facts --------
    for pat in _NAME_PATTERNS:
        m = pat.match(text)
        if m:
            name = m.group(1).strip()
            if name:
                upsert_fact(
                    user_id=user_id,
                    key="user.name",
                    value=name,
                    confidence="HIGH",
                    source="USER",
                    locale=locale,
                )
            return

    # -------- explicit LANGUAGE PREFERENCE (stored as plain value; no inference) --------
    for pat in _LOCALE_PATTERNS:
        m = pat.match(text)
        if m:
            raw_pref = m.group(1).strip()
            if raw_pref:
                upsert_fact(
                    user_id=user_id,
                    key="user.language_preference",
                    value=raw_pref,
                    confidence="LOW",
                    source="USER",
                    locale=locale,
                )
            return

    # Otherwise: do nothing (no inference)
    return
