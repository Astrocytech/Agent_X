"""Failure taxonomy classifying recoverable vs blocking failures."""
from enum import Enum

class FailureClass(str, Enum):
    RECOVERABLE = "recoverable"
    BLOCKING = "blocking"
    POLICY_DENIED = "policy_denied"
    VALIDATION_FAILED = "validation_failed"
    UNKNOWN = "unknown"

class FailureCategory(str, Enum):
    PATCH_INVALID = "patch_invalid"
    PATH_FORBIDDEN = "path_forbidden"
    VALIDATION_FAILURE = "validation_failure"
    SCHEMA_MISMATCH = "schema_mismatch"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    ROLLBACK_NEEDED = "rollback_needed"
    EVIDENCE_WRITE_FAILED = "evidence_write_failed"
    REVIEW_REJECTED = "review_rejected"
    PROMOTION_REJECTED = "promotion_rejected"

def classify_failure(category: FailureCategory) -> FailureClass:
    mapping = {
        FailureCategory.RECOVERABLE: FailureClass.RECOVERABLE,
        FailureCategory.BLOCKING: FailureClass.BLOCKING,
        FailureCategory.POLICY_DENIED: FailureClass.POLICY_DENIED,
        FailureCategory.VALIDATION_FAILURE: FailureClass.VALIDATION_FAILED,
    }
    return mapping.get(category, FailureClass.UNKNOWN)
