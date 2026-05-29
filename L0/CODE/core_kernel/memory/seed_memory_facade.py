"""SeedMemoryFacade — L0 memory facade that writes governed turn records only.

Extended record types (evolution_lesson, failed_patch_lesson, skill_memory, etc.)
live in examples/extensions/memory_retrieval/ — not in L0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core_kernel.contracts.seed_ports import MemoryPort


class SeedMemoryRecordType(str, Enum):
    TURN_OBSERVATION = "turn_observation"
    TOOL_RESULT = "tool_result"
    EVALUATION_RESULT = "evaluation_result"
    CONSTRAINT = "constraint"


@dataclass(frozen=True)
class MemoryWriteRequest:
    record_type: SeedMemoryRecordType
    observation: str
    run_id: str
    profile_id: str = ""
    source_phase: str = ""
    replay_ref: str = ""
    schema_version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)


class SeedMemoryFacade:
    def __init__(self, inner: MemoryPort) -> None:
        self._inner = inner
        self._valid_types = set(t.value for t in SeedMemoryRecordType)

    def store_typed(self, request: MemoryWriteRequest) -> list[str]:
        if request.record_type.value not in self._valid_types:
            request = MemoryWriteRequest(
                record_type=SeedMemoryRecordType.TURN_OBSERVATION,
                observation=request.observation,
                run_id=request.run_id,
                profile_id=request.profile_id,
                source_phase=request.source_phase,
                replay_ref=request.replay_ref,
                metadata=request.metadata,
            )
        ctx = dict(request.metadata)
        ctx["record_type"] = request.record_type.value
        ctx["profile_id"] = request.profile_id
        ctx["run_id"] = request.run_id
        return self._inner.write(request.observation, ctx)

    def store(
        self,
        record_type: str,
        observation: str,
        ctx: dict[str, Any] | None = None,
    ) -> list[str]:
        ctx = dict(ctx or {})
        try:
            rt = SeedMemoryRecordType(record_type)
        except ValueError:
            rt = SeedMemoryRecordType.TURN_OBSERVATION
        req = MemoryWriteRequest(
            record_type=rt,
            observation=observation,
            run_id=ctx.pop("run_id", ""),
            profile_id=ctx.pop("profile_id", ""),
            source_phase=ctx.pop("source_phase", ""),
            replay_ref=ctx.pop("replay_ref", ""),
            metadata=ctx,
        )
        return self.store_typed(req)

    def store_evaluation_result(
        self, score: float, verdict: str, ctx: dict[str, Any] | None = None
    ) -> list[str]:
        obs = f"score:{score} verdict:{verdict}"
        req = MemoryWriteRequest(
            record_type=SeedMemoryRecordType.EVALUATION_RESULT,
            observation=obs,
            run_id=(ctx or {}).get("run_id", ""),
            profile_id=(ctx or {}).get("profile_id", ""),
            metadata=ctx or {},
        )
        return self.store_typed(req)

    @property
    def inner(self) -> MemoryPort:
        return self._inner
