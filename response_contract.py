# response_contract.py
# =========================
# MIRA BASE – RESPONSE CONTRACT (v1)
# =========================
#
# Responsibilities:
# - canonical output of the Brain
# - NO language, NO style, NO "how to say"
# - may include computed/verified data (facts) as values
#

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


class Source(str, Enum):
    STATIC = "STATIC"
    DETERMINISTIC = "DETERMINISTIC"
    MEMORY = "MEMORY"
    GENERATIVE = "GENERATIVE"


class Confidence(str, Enum):
    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"


class Constraint(str, Enum):
    # hard safety rails
    NO_GENERATION = "no_generation"
    NO_MEMORY_WRITE = "no_memory_write"
    SHORT_ANSWER = "short_answer"
    SILENT_EXIT = "silent_exit"


class PayloadType(str, Enum):
    # semantic payloads
    FACTS = "FACTS"
    SOCIAL = "SOCIAL"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class PayloadItem(BaseModel):
    """
    Payload is semantic + computed data.
    It must never instruct language/style, and must not be a natural-language answer.
    """
    type: PayloadType
    data: Dict[str, Any] = Field(default_factory=dict)


class ResponseContract(BaseModel):
    # identity
    decision_id: str
    intent: Optional[str] = None
    confidence: Confidence = Confidence.MED

    # routing
    source: Source
    reason: str = ""

    # execution plan
    actions: List[str] = Field(default_factory=list)
    constraints: List[Constraint] = Field(default_factory=lambda: [Constraint.NO_GENERATION])

    # semantic payload + computed facts
    payload: List[PayloadItem] = Field(default_factory=list)

    # read-only signals (for audit / debugging / UI)
    chrono: Dict[str, Any] = Field(default_factory=dict)
    homeostasis: Dict[str, Any] = Field(default_factory=dict)
    meta_flags: List[str] = Field(default_factory=list)
    epistemic_state: Optional[str] = None

    @model_validator(mode="after")
    def _guard_contract(self) -> "ResponseContract":
        # If we claim silent exit, payload should be empty (or only ERROR with reason).
        if Constraint.SILENT_EXIT in self.constraints:
            if any(p.type not in (PayloadType.ERROR,) for p in self.payload):
                raise ValueError("SILENT_EXIT requires empty payload or only ERROR payload.")
        # If generative source is selected, we still require explicit allowance later.
        # (v1: keep it off by default; execution can enforce.)
        return self
