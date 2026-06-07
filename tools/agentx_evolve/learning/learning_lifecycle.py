from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agentx_evolve.learning.outcome_models import (
    utc_now_iso,
    new_id,
)

LL_SCHEMA_VERSION = "1.0"
LL_SCHEMA_ID = "learning_lifecycle.schema.json"

STAGE_INITIAL = "INITIAL"
STAGE_EVENT_CAPTURED = "EVENT_CAPTURED"
STAGE_OUTCOME_REVIEWED = "OUTCOME_REVIEWED"
STAGE_SIGNAL_EXTRACTED = "SIGNAL_EXTRACTED"
STAGE_POLICY_CHECKED = "POLICY_CHECKED"
STAGE_CANDIDATE_BUILT = "CANDIDATE_BUILT"
STAGE_CANDIDATE_PROPOSED = "CANDIDATE_PROPOSED"
STAGE_MEMORY_PROMOTED = "MEMORY_PROMOTED"
STAGE_FOLLOW_UP_SUBMITTED = "FOLLOW_UP_SUBMITTED"
STAGE_FAILED = "FAILED"
STAGE_BLOCKED = "BLOCKED"

ALL_STAGES = [
    STAGE_INITIAL,
    STAGE_EVENT_CAPTURED,
    STAGE_OUTCOME_REVIEWED,
    STAGE_SIGNAL_EXTRACTED,
    STAGE_POLICY_CHECKED,
    STAGE_CANDIDATE_BUILT,
    STAGE_CANDIDATE_PROPOSED,
    STAGE_MEMORY_PROMOTED,
    STAGE_FOLLOW_UP_SUBMITTED,
    STAGE_FAILED,
    STAGE_BLOCKED,
]

_VALID_TRANSITIONS: dict[str, set[str]] = {
    STAGE_INITIAL: {STAGE_EVENT_CAPTURED, STAGE_FAILED},
    STAGE_EVENT_CAPTURED: {STAGE_OUTCOME_REVIEWED, STAGE_FAILED, STAGE_BLOCKED},
    STAGE_OUTCOME_REVIEWED: {STAGE_SIGNAL_EXTRACTED, STAGE_FAILED},
    STAGE_SIGNAL_EXTRACTED: {STAGE_POLICY_CHECKED, STAGE_FAILED, STAGE_BLOCKED},
    STAGE_POLICY_CHECKED: {STAGE_CANDIDATE_BUILT, STAGE_FAILED},
    STAGE_CANDIDATE_BUILT: {STAGE_CANDIDATE_PROPOSED, STAGE_FAILED, STAGE_BLOCKED},
    STAGE_CANDIDATE_PROPOSED: {STAGE_MEMORY_PROMOTED, STAGE_FAILED, STAGE_BLOCKED},
    STAGE_MEMORY_PROMOTED: {STAGE_FOLLOW_UP_SUBMITTED, STAGE_FAILED},
    STAGE_FOLLOW_UP_SUBMITTED: set(),
    STAGE_FAILED: set(),
    STAGE_BLOCKED: {STAGE_INITIAL, STAGE_EVENT_CAPTURED},
}


@dataclass
class LearningLifecycle:
    schema_version: str = LL_SCHEMA_VERSION
    schema_id: str = LL_SCHEMA_ID
    lifecycle_id: str = ""
    event_id: str = ""
    current_stage: str = STAGE_INITIAL
    started_at: str = ""
    updated_at: str = ""
    transitions: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = {}
        for f in self.__dataclass_fields__:
            val = getattr(self, f)
            result[f] = val
        return result


def create_lifecycle(event_id: str) -> LearningLifecycle:
    now = utc_now_iso()
    return LearningLifecycle(
        lifecycle_id=new_id("ll"),
        event_id=event_id,
        current_stage=STAGE_INITIAL,
        started_at=now,
        updated_at=now,
    )


def transition_to(lifecycle: LearningLifecycle, target_stage: str) -> LearningLifecycle:
    if target_stage not in _VALID_TRANSITIONS.get(lifecycle.current_stage, set()):
        raise ValueError(
            f"Invalid lifecycle transition: {lifecycle.current_stage} -> {target_stage}"
        )
    now = utc_now_iso()
    lifecycle.transitions.append({
        "from": lifecycle.current_stage,
        "to": target_stage,
        "timestamp": now,
    })
    lifecycle.current_stage = target_stage
    lifecycle.updated_at = now
    return lifecycle


def is_terminal(stage: str) -> bool:
    return stage in {STAGE_FOLLOW_UP_SUBMITTED, STAGE_FAILED}


def is_blocked(stage: str) -> bool:
    return stage == STAGE_BLOCKED
