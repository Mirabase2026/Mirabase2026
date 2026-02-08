# action/handlers/noop.py
# ======================
# No-op Action Handler
# ======================

def handle(action: dict) -> dict:
    return {
        "status": "success",
        "message": "No-op action executed",
        "payload": {},
        "retryable": False,
    }
