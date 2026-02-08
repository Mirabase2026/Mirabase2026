# action/profile_store.py
# =======================
# Profile Store (load/save + simple cache)
# =======================

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

_USERS_DIR = Path("users")
_CACHE: Dict[str, Dict[str, Any]] = {}


def _profile_path(user_id: str) -> Path:
    # default user path: users/<user_id>/profile.json
    # also allow users/default/profile.json for bootstrap if user_id == "default"
    return _USERS_DIR / user_id / "profile.json"


def load_profile(user_id: str) -> Dict[str, Any]:
    path = _profile_path(user_id)
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # cache refresh
    _CACHE[user_id] = data
    return data


def get_cached_profile(user_id: str) -> Dict[str, Any] | None:
    return _CACHE.get(user_id)


def save_profile_atomic(user_id: str, profile: Dict[str, Any]) -> None:
    path = _profile_path(user_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = path.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
        f.write("\n")

    tmp_path.replace(path)

    # cache refresh
    _CACHE[user_id] = profile
