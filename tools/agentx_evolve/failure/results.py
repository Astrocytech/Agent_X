"""Stable error-code system and public/internal message separation.

Item 48 (42.1/42.2): Stable numeric error codes with
human-readable messages and internal diagnostic details.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ErrorCode(Enum):
    # Policy & Boundaries
    POLICY_DENIED = (1001, "Policy denied the requested operation")
    FORBIDDEN_PATH = (1002, "Access to the specified path is forbidden")
    STALE_LOCK = (1003, "Session lock is stale or expired")

    # Patch
    MALFORMED_PATCH = (2001, "Patch candidate is malformed or incomplete")
    PATCH_APPLY_FAILED = (2002, "Failed to apply the governed patch")
    ROLLBACK_FAILED = (2003, "Rollback operation failed")

    # Artifacts & Evidence
    MISSING_ARTIFACT = (3001, "Required artifact not found")
    PLACEHOLDER_HASH = (3002, "Source hash is a placeholder value")
    PROVENANCE_GAP = (3003, "Generated file lacks full provenance chain")
    SCHEMA_MISMATCH = (3004, "Artifact does not match expected schema")

    # Providers & Commands
    PROVIDER_FAILURE = (4001, "Model or data provider returned an error")
    COMMAND_TIMEOUT = (4002, "Subprocess command timed out")
    COMMAND_FAILED = (4003, "Subprocess command returned non-zero exit")

    # Review & Promotion
    REVIEW_REJECTED = (5001, "Review decision was rejection")
    PROMOTION_REJECTED = (5002, "Promotion decision was rejected")

    # Replay & Acceptance
    REPLAY_MISMATCH = (6001, "Clean replay results differ from development run")
    BENCHMARK_FAILED = (6002, "Benchmark evaluation returned failures")
    MISSING_PROVENANCE = (6003, "No provenance record found for artifact")

    # Internal
    INTERNAL_ERROR = (9001, "Internal system error")
    CONFIG_ERROR = (9002, "Configuration is invalid or missing")

    def __init__(self, code: int, message: str):
        self.code = code
        self.default_message = message


@dataclass
class ErrorResult:
    error_code: int
    error_name: str
    internal_message: str = ""
    user_message: str = ""
    component: str = ""
    related_artifact_id: str = ""
    evidence_ref: str = ""
    redacted: bool = False
    safe_next_action: str = ""  # retry | rollback | review | abort | report

    def to_user_facing(self) -> dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.user_message or self.internal_message,
            "safe_next_action": self.safe_next_action,
        }

    def to_internal(self) -> dict[str, Any]:
        return {
            "error_code": self.error_code,
            "error_name": self.error_name,
            "internal_message": self.internal_message,
            "user_message": self.user_message,
            "component": self.component,
            "related_artifact_id": self.related_artifact_id,
            "evidence_ref": self.evidence_ref,
            "redacted": self.redacted,
            "safe_next_action": self.safe_next_action,
        }


def make_error(code: ErrorCode, component: str = "",
               internal_msg: str = "",
               user_msg: str = "",
               artifact_id: str = "",
               evidence: str = "") -> ErrorResult:
    return ErrorResult(
        error_code=code.code,
        error_name=code.name,
        internal_message=internal_msg or code.default_message,
        user_message=user_msg or code.default_message,
        component=component,
        related_artifact_id=artifact_id,
        evidence_ref=evidence,
        safe_next_action=_default_action(code),
    )


def _default_action(code: ErrorCode) -> str:
    mapping = {
        ErrorCode.POLICY_DENIED: "review",
        ErrorCode.FORBIDDEN_PATH: "abort",
        ErrorCode.STALE_LOCK: "retry",
        ErrorCode.MALFORMED_PATCH: "retry",
        ErrorCode.PATCH_APPLY_FAILED: "rollback",
        ErrorCode.ROLLBACK_FAILED: "report",
        ErrorCode.MISSING_ARTIFACT: "abort",
        ErrorCode.PLACEHOLDER_HASH: "report",
        ErrorCode.PROVENANCE_GAP: "abort",
        ErrorCode.SCHEMA_MISMATCH: "retry",
        ErrorCode.PROVIDER_FAILURE: "retry",
        ErrorCode.COMMAND_TIMEOUT: "retry",
        ErrorCode.COMMAND_FAILED: "review",
        ErrorCode.REVIEW_REJECTED: "review",
        ErrorCode.PROMOTION_REJECTED: "review",
        ErrorCode.REPLAY_MISMATCH: "report",
        ErrorCode.BENCHMARK_FAILED: "report",
        ErrorCode.MISSING_PROVENANCE: "abort",
        ErrorCode.INTERNAL_ERROR: "report",
        ErrorCode.CONFIG_ERROR: "abort",
    }
    return mapping.get(code, "report")


ERROR_CODE_REGISTRY: dict[int, ErrorCode] = {ec.code: ec for ec in ErrorCode}


def lookup_error(code: int) -> ErrorCode | None:
    return ERROR_CODE_REGISTRY.get(code)
