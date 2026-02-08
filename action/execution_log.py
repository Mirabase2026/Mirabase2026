# action/execution_log.py
# =======================
# Execution Log (jsonl) for idempotence & audit
# =======================

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

LOG_FILE = Path("execution_log.jsonl")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_result_by_request_id(request_id: str) -> Optional[Dict[str, Any]]:
    if not request_id or not LOG_FILE.exists():
        return None

    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("request_id") == request_id:
                return rec.get("result")
    return None


def count_actions_last_24h(user_id: str) -> int:
    if not LOG_FILE.exists():
        return 0

    cutoff = datetime.now(timezone.utc).timestamp() - 24 * 3600
    count = 0

    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            if rec.get("user_id") != user_id:
                continue

            ts = rec.get("ts")
            if not isinstance(ts, (int, float)):
                continue

            if ts >= cutoff:
                count += 1

    return count


def append_record(
    *,
    user_id: str,
    request_id: str,
    trace_id: str,
    action_type: str,
    result: Dict[str, Any],
) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    rec = {
        "time": _now_iso(),
        "ts": datetime.now(timezone.utc).timestamp(),
        "user_id": user_id,
        "request_id": request_id,
        "trace_id": trace_id,
        "action_type": action_type,
        "result": result,
    }

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
