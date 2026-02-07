# fact_engine.py
# =========================
# MIRA BASE – FACT ENGINE
# =========================
#
# Responsibilities:
# - compute factual values for actions
# - NEVER generate text

from __future__ import annotations

from typing import Dict, Any, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
import ast
import operator as op


_CZ_DAY_NAMES = {
    0: "pondělí",
    1: "úterý",
    2: "středa",
    3: "čtvrtek",
    4: "pátek",
    5: "sobota",
    6: "neděle",
}


def _require_timezone(context: Optional[Dict[str, Any]]) -> Optional[str]:
    if not context:
        return None
    tz = context.get("timezone")
    if isinstance(tz, str) and tz.strip():
        return tz.strip()
    return None


def _now_in_tz(tz_name: str) -> datetime:
    return datetime.now(ZoneInfo(tz_name))


def _format_time_24h(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def _format_date_cz(dt: datetime) -> str:
    return f"{dt.day}. {dt.month}. {dt.year}"


_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def _eval_expr(expr: str) -> float:
    def _eval(node):
        if isinstance(node, ast.Num):  # Py < 3.8
            return float(node.n)
        if isinstance(node, ast.Constant):  # Py >= 3.8
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError("BAD_CONST")
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
        raise ValueError("BAD_EXPR")

    parsed = ast.parse(expr, mode="eval")
    return float(_eval(parsed.body))


def resolve_facts(
    actions: list,
    entities: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {}

    # TIME / DATE / DAY
    if any(a in actions for a in ("TIME_NOW", "DAY_TODAY", "DATE_TODAY")):
        tz_name = _require_timezone(context)
        if not tz_name:
            out["fact_error"] = "MISSING_TIMEZONE"
            return out

        try:
            now = _now_in_tz(tz_name)
        except Exception:
            out["fact_error"] = "BAD_TIMEZONE"
            return out

        if "TIME_NOW" in actions:
            t = _format_time_24h(now)
            out["time_now"] = t
            out["time"] = t  # legacy bridge

        if "DAY_TODAY" in actions:
            d = _CZ_DAY_NAMES[now.weekday()]
            out["day_today"] = d
            out["day"] = d  # legacy bridge

        if "DATE_TODAY" in actions:
            dt = _format_date_cz(now)
            out["date_today"] = dt
            out["date"] = dt  # legacy bridge

    # ARITHMETIC
    if "ARITHMETIC" in actions:
        expr = (entities or {}).get("expression", "")
        if isinstance(expr, str):
            expr = expr.strip()
        else:
            expr = ""

        if not expr:
            out["fact_error"] = "MISSING_EXPRESSION"
            return out

        try:
            val = _eval_expr(expr)
            out["arithmetic_value"] = val
            out["expression"] = expr  # adapter expects this
            out["result"] = val       # legacy bridge
        except Exception:
            out["fact_error"] = "BAD_ARITHMETIC"

    return out
