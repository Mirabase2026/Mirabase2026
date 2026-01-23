# logic.py

import os
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

# =========================
# CESTY K SOUBORŮM
# =========================
MEMORY_FILE = Path("memory.json")
EXECUTION_LOG_FILE = Path("execution_log.jsonl")

# =========================
# PAMĚŤ
# =========================
def save_message(role: str, content: str):
    data = {"messages": []}
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    data["messages"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_messages():
    if not MEMORY_FILE.exists():
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("messages", [])

# =========================
# EXECUTION LOG
# =========================
def log_step(action: str, status: str, details: dict | None = None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "status": status,
        "details": details
    }

    with open(EXECUTION_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# =========================
# OPENROUTER
# =========================
def call_openrouter(messages, model="google/gemini-2.0-flash-exp:free", json_mode=False):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        return {
            "content": data["choices"][0]["message"]["content"],
            "raw": data
        }
    except Exception as e:
        return {"error": str(e)}

# =========================
# PLANNER
# =========================
def plan_steps(user_text: str):
    prompt = [
        {
            "role": "system",
            "content": (
                "Jsi technický scheduler.\n"
                "Tvůj jediný úkol je vrátit JSON:\n"
                '{"steps": ["REPLY"]}\n\n'
                "Povolené kroky:\n"
                "- REPLY\n"
                "- SAVE_LONG\n"
                "- SEARCH_KNOWLEDGE\n"
                "- SUMMARIZE\n\n"
                "Nevysvětluj. Nevkládej text. Nevymýšlej nové kroky."
            )
        },
        {"role": "user", "content": user_text}
    ]

    result = call_openrouter(prompt, json_mode=True)

    if "error" in result:
        return ["REPLY"]

    try:
        plan = json.loads(result["content"])
        steps = plan.get("steps")
        if isinstance(steps, list) and steps:
            return steps
    except Exception:
        pass

    return ["REPLY"]

# =========================
# PIPELINE (CLI READY)
# =========================
def run_pipeline(user_text: str, session: str = "cli", source: str = "cli"):
    memory_read = []
    memory_write = None
    error = None
    final_reply = None

    # 1. Ulož vstup
    save_message("user", user_text)
    memory_write = "short"

    # 2. Planner
    log_step("PLANNER", "start")
    steps = plan_steps(user_text)
    log_step("PLANNER", "ok", {"steps": steps})

    # 3. Akce
    for step in steps:
        log_step(step, "start")

        if step == "REPLY":
            history = read_messages()
            memory_read.append("short")

            result = call_openrouter(history)

            if "error" in result:
                error = result["error"]
                log_step(step, "error", {"error": error})
                break

            final_reply = result["content"]
            save_message("assistant", final_reply)
            memory_write = "short"
            log_step(step, "ok")

        elif step == "SAVE_LONG":
            log_step(step, "ok", {"info": "not implemented"})

        elif step == "SEARCH_KNOWLEDGE":
            log_step(step, "ok", {"info": "not implemented"})

        elif step == "SUMMARIZE":
            log_step(step, "ok", {"info": "not implemented"})

        else:
            error = "unknown step"
            log_step(step, "error", {"error": error})
            break

    # 4. Návrat pro CLI
    return {
        "response": final_reply or "Došlo k chybě.",
        "action": steps,
        "memory_read": memory_read,
        "memory_write": memory_write,
        "error": error
    }

# =========================
# CLEAR MEMORY
# =========================
def clear_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"messages": []}, f, ensure_ascii=False, indent=2)


