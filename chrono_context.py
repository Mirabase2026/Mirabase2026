# =========================
# CHRONO CONTEXT (SIGNALS)
# =========================
#
# Úkol:
# - převést "čas jako číslo" na "čas jako kontext"
# - vracet jen signály/flagy (žádný text)
#
# Použití:
# - logic.py uloží výsledek do context["chrono"]
# - discourse ho může později využít (zatím ne)

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, List

try:
    from zoneinfo import ZoneInfo  # py>=3.9
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore


DEFAULT_TZ = "Europe/Prague"


@dataclass
class ChronoContext:
    hour: Optional[int]
    minute: Optional[int]
    part_of_day: str
    flags: List[str]


def _parse_time_hhmm(s: Any) -> tuple[Optional[int], Optional[int]]:
    if not isinstance(s, str):
        return None, None
    t = s.strip()
    # očekáváme "HH:MM"
    if len(t) != 5 or t[2] != ":":
        return None, None
    hh, mm = t.split(":")
    if not (hh.isdigit() and mm.isdigit()):
        return None, None
    h = int(hh)
    m = int(mm)
    if h < 0 or h > 23 or m < 0 or m > 59:
        return None, None
    return h, m


def _now_local(tz_name: str) -> datetime:
    if ZoneInfo is None:
        return datetime.now()
    try:
        return datetime.now(ZoneInfo(tz_name))
    except Exception:
        return datetime.now()


def _part_of_day_from_hour(h: int) -> str:
    # jednoduché, stabilní bucketování (nezávislé na stylu)
    if 0 <= h <= 4:
        return "NIGHT"
    if 5 <= h <= 10:
        return "MORNING"
    if 11 <= h <= 13:
        return "MIDDAY"
    if 14 <= h <= 17:
        return "AFTERNOON"
    if 18 <= h <= 21:
        return "EVENING"
    return "LATE_NIGHT"  # 22–23


def _flags_from_hour(h: int) -> List[str]:
    flags: List[str] = []
    part = _part_of_day_from_hour(h)
    flags.append(part)

    # kompatibilní aliasy (ať se ti to později nerozsype)
    if part in ("NIGHT", "LATE_NIGHT"):
        flags.append("NIGHT")
    if part == "MORNING":
        flags.append("MORNING")
    if part == "EVENING":
        flags.append("EVENING")

    return sorted(set(flags))


def build_chrono_context(
    facts: Dict[str, Any],
    *,
    tz_name: str = DEFAULT_TZ,
) -> Dict[str, Any]:
    """
    Vstup:
      facts může obsahovat:
        - time_now: "HH:MM"
    Výstup:
      dict pro context["chrono"]
    """
    time_now = facts.get("time_now")
    h, m = _parse_time_hhmm(time_now)

    # fallback na systémový čas, když fact_engine čas nedodal
    if h is None:
        now = _now_local(tz_name)
        h, m = now.hour, now.minute
        source = "SYSTEM_NOW"
    else:
        source = "FACT_TIME_NOW"

    part = _part_of_day_from_hour(h)
    flags = _flags_from_hour(h)

    # WORK_HOURS – volitelný užitečný signál (později se hodí)
    now_local = _now_local(tz_name)
    weekday = now_local.weekday()  # 0=Mon ... 6=Sun
    if weekday <= 4 and 9 <= h <= 17:
        flags.append("WORK_HOURS")

    flags = sorted(set(flags))

    cc = ChronoContext(hour=h, minute=m, part_of_day=part, flags=flags)

    return {
        "hour": cc.hour,
        "minute": cc.minute,
        "part_of_day": cc.part_of_day,
        "flags": cc.flags,
        "source": source,
        "tz": tz_name,
    }
