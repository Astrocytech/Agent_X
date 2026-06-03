from agentx_evolve.recovery.failure_taxonomy import (
    REQUIRED_FAILURE_CLASSES,
    DEFAULT_SEVERITY_BY_FAILURE_CLASS,
    CRITICAL_CLASSES,
    is_known_failure_class,
    normalize_failure_class,
    get_failure_severity,
    classify_failure,
    FailureGroup,
    group_failure,
)

__all__ = [
    "REQUIRED_FAILURE_CLASSES",
    "DEFAULT_SEVERITY_BY_FAILURE_CLASS",
    "CRITICAL_CLASSES",
    "is_known_failure_class",
    "normalize_failure_class",
    "get_failure_severity",
    "classify_failure",
    "FailureGroup",
    "group_failure",
]
