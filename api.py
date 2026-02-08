# api.py
# =========================
# MIRA BASE – API (v7)
# =========================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ltm import set_preference

app = FastAPI()


class PreferenceUpdate(BaseModel):
    user_id: str
    key: str
    value: object


@app.post("/user/preference")
def update_preference(body: PreferenceUpdate):
    ok = set_preference(body.user_id, body.key, body.value)
    if not ok:
        raise HTTPException(status_code=400, detail="Preference update failed")
    return {"status": "ok"}
