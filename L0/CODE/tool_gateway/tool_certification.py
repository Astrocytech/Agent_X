from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

_UNSET = object()

__all__ = [
    "ToolCertification",
    "CertificationRecord",
    "ToolCertificationRegistry",
    "CertificationError",
    "CertificationStatus",
]

CertificationStatus = Literal[
    "uncertified",
    "certified_readonly",
    "certified_mutating",
    "certified_irreversible_requires_approval",
    "disabled",
    "revoked",
]


class CertificationError(RuntimeError):
    """Raised on certification errors."""


@dataclass(frozen=True)
class CertificationRecord:
    tool_id: str
    version: str
    input_schema_valid: bool
    output_schema_valid: bool
    policy_bound: bool
    resource_limit_bound: bool
    evaluation_hooks_bound: bool
    side_effect_level_declared: bool
    idempotency_declared: bool
    rollback_strategy_declared: bool
    last_certified_at: str
    certification_status: CertificationStatus


ToolCertification = CertificationRecord


class ToolCertificationRegistry:
    """Manages tool certification status.

    No tool should execute unless it is:
    - registered
    - schema-valid
    - policy-bound
    - resource-bound
    - evaluation-bound
    - certified
    - enabled
    - authorized for profile
    """

    def __init__(self) -> None:
        self._certifications: dict[str, CertificationRecord] = {}

    def certify(
        self,
        tool_id: str,
        version: str,
        *,
        input_schema_valid: bool = True,
        output_schema_valid: bool = True,
        policy_bound: bool = True,
        resource_limit_bound: bool = True,
        evaluation_hooks_bound: bool = True,
        side_effect_level_declared: bool = True,
        idempotency_declared: bool = False,
        rollback_strategy_declared: bool = False,
        status: CertificationStatus | None = None,
    ) -> CertificationRecord:
        required = [
            input_schema_valid,
            output_schema_valid,
            policy_bound,
            resource_limit_bound,
            evaluation_hooks_bound,
            side_effect_level_declared,
        ]

        if status is None:
            if not all(required):
                status = "uncertified"
            elif rollback_strategy_declared:
                status = "certified_mutating"
            else:
                status = "certified_readonly"

        record = CertificationRecord(
            tool_id=tool_id,
            version=version,
            input_schema_valid=input_schema_valid,
            output_schema_valid=output_schema_valid,
            policy_bound=policy_bound,
            resource_limit_bound=resource_limit_bound,
            evaluation_hooks_bound=evaluation_hooks_bound,
            side_effect_level_declared=side_effect_level_declared,
            idempotency_declared=idempotency_declared,
            rollback_strategy_declared=rollback_strategy_declared,
            last_certified_at=datetime.now(timezone.utc).isoformat(),
            certification_status=status,
        )
        self._certifications[tool_id] = record
        return record

    def get_certification(self, tool_id: str) -> CertificationRecord:
        if tool_id not in self._certifications:
            raise CertificationError(f"Unknown tool: {tool_id}")
        return self._certifications[tool_id]

    def revoke(self, tool_id: str, reason: str = "") -> CertificationRecord:
        if tool_id not in self._certifications:
            raise CertificationError(f"Unknown tool: {tool_id}")
        old = self._certifications[tool_id]
        record = CertificationRecord(
            tool_id=old.tool_id,
            version=old.version,
            input_schema_valid=old.input_schema_valid,
            output_schema_valid=old.output_schema_valid,
            policy_bound=old.policy_bound,
            resource_limit_bound=old.resource_limit_bound,
            evaluation_hooks_bound=old.evaluation_hooks_bound,
            side_effect_level_declared=old.side_effect_level_declared,
            idempotency_declared=old.idempotency_declared,
            rollback_strategy_declared=old.rollback_strategy_declared,
            last_certified_at=datetime.now(timezone.utc).isoformat(),
            certification_status="revoked",
        )
        self._certifications[tool_id] = record
        return record

    def can_execute(self, tool_id: str, tool_registry=None) -> tuple[bool, str]:
        if tool_id not in self._certifications:
            return False, "not_certified"
        cert = self._certifications[tool_id]
        if cert.certification_status == "revoked":
            return False, "certification_revoked"
        if cert.certification_status == "disabled":
            return False, "certification_disabled"
        if cert.certification_status == "uncertified":
            return False, "uncertified"

        if tool_registry:
            try:
                desc = tool_registry.get_tool(tool_id)
                if not desc.enabled:
                    return False, "tool_disabled_in_registry"
            except Exception:
                return False, "tool_not_in_registry"

        return True, "ok"

    def list_certified_tools(self) -> list[CertificationRecord]:
        return [
            r
            for r in self._certifications.values()
            if r.certification_status not in ("revoked", "disabled", "uncertified")
        ]

    def list_all(self) -> list[CertificationRecord]:
        return list(self._certifications.values())
