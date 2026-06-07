from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    PatchProposal,
    ValidationHandoff,
)
from agentx_evolve.models.model_models import new_id, utc_now_iso

VR_SCHEMA_VERSION = "1.0"
VALIDATION_REQUEST_SCHEMA_ID = "validation_request.schema.json"

VALIDATION_MODE_FULL = "FULL"
VALIDATION_MODE_QUICK = "QUICK"
VALIDATION_MODE_SYNTAX_ONLY = "SYNTAX_ONLY"
ALL_VALIDATION_MODES = [VALIDATION_MODE_FULL, VALIDATION_MODE_QUICK, VALIDATION_MODE_SYNTAX_ONLY]


@dataclass
class ValidationRequest:
    schema_version: str = VR_SCHEMA_VERSION
    schema_id: str = VALIDATION_REQUEST_SCHEMA_ID
    validation_request_id: str = ""
    task_id: str = ""
    patch_proposal_id: str = ""
    mode: str = VALIDATION_MODE_QUICK
    commands: list[str] = field(default_factory=list)
    expected_commands: list[str] = field(default_factory=list)
    timeout_seconds: int = 120
    created_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = {}
        for f in self.__dataclass_fields__:
            val = getattr(self, f)
            result[f] = val
        return result


def build_validation_request(
    patch_proposal: PatchProposal,
    task_id: str,
    mode: str = VALIDATION_MODE_QUICK,
    custom_commands: list[str] | None = None,
) -> ValidationRequest:
    commands = custom_commands or []
    if not commands:
        commands = _derive_validation_commands(patch_proposal)

    return ValidationRequest(
        validation_request_id=new_id("vr"),
        task_id=task_id,
        patch_proposal_id=patch_proposal.patch_proposal_id,
        mode=mode,
        commands=commands,
        expected_commands=list(commands),
        timeout_seconds=120 if mode == VALIDATION_MODE_FULL else 60,
        created_at=utc_now_iso(),
    )


def build_handoff_from_request(request: ValidationRequest) -> ValidationHandoff:
    return ValidationHandoff(
        validation_handoff_id=new_id("ho"),
        task_id=request.task_id,
        created_at=utc_now_iso(),
        patch_proposal_id=request.patch_proposal_id,
        validation_commands=request.commands,
    )


def _derive_validation_commands(proposal: PatchProposal) -> list[str]:
    commands: list[str] = []
    if proposal.task_id:
        commands.append("compileall")
        commands.append("pytest")
    return commands
