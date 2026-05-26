"""KernelTurnRequestV1 — single public turn request contract."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


KERNEL_REQUEST_SCHEMA_VERSION = "1.0"

DANGEROUS_FIELDS = frozenset({
    "bypass_governance",
    "force_tool",
    "disable_trace",
    "ignore_policy",
    "override_risk",
})


@dataclass
class KernelTurnRequestV1:
    schema_version: str = KERNEL_REQUEST_SCHEMA_VERSION
    request_id: str = ""
    profile_id: str = ""
    goal: str = ""
    constraints: list[str] = field(default_factory=list)
    allowed_tools: list[str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    dangerous_fields_detected: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        self.warnings = []
        dangerous = DANGEROUS_FIELDS & set(self.metadata.keys())
        for field_name in dangerous:
            self.warnings.append(f"Dangerous field '{field_name}' in metadata — ignored for safety")
        self.dangerous_fields_detected = list(dangerous)
        self.metadata = {k: v for k, v in self.metadata.items() if k not in DANGEROUS_FIELDS}
        if self.goal and len(self.goal) > 10000:
            self.warnings.append("Goal exceeds 10000 characters — truncating")
            self.goal = self.goal[:10000]
        return self.warnings

    def to_kernel_input(self):
        from core_kernel.models.kernel_io import KernelInput
        return KernelInput(
            user_goal=self.goal,
            profile_id=self.profile_id or "generalist",
        )

    @classmethod
    def from_request(cls, profile_id: str, user_input: str, **metadata: Any) -> KernelTurnRequestV1:
        req = cls(
            request_id=f"req-{uuid.uuid4().hex[:12]}",
            profile_id=profile_id,
            goal=user_input,
            metadata=dict(metadata),
        )
        req.validate()
        return req
