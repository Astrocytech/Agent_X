from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
import hashlib
import json
import re
import uuid

OUTCOME_SUCCESS = "SUCCESS"
OUTCOME_PARTIAL = "PARTIAL"
OUTCOME_FAILED = "FAILED"
OUTCOME_BLOCKED = "BLOCKED"
OUTCOME_REGRESSION = "REGRESSION"
OUTCOME_REJECTED = "REJECTED"
OUTCOME_UNKNOWN = "UNKNOWN"

ALL_OUTCOME_STATUSES = {OUTCOME_SUCCESS, OUTCOME_PARTIAL, OUTCOME_FAILED, OUTCOME_BLOCKED, OUTCOME_REGRESSION, OUTCOME_REJECTED, OUTCOME_UNKNOWN}

REVIEW_VERIFIED = "VERIFIED"
REVIEW_BLOCKED = "BLOCKED"
REVIEW_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
REVIEW_NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
REVIEW_CONTRADICTORY = "CONTRADICTORY"
REVIEW_INVALID = "INVALID"

ALL_REVIEW_STATUSES = {REVIEW_VERIFIED, REVIEW_BLOCKED, REVIEW_NEEDS_MORE_EVIDENCE, REVIEW_NEEDS_HUMAN_REVIEW, REVIEW_CONTRADICTORY, REVIEW_INVALID}

SUCCESS_VERIFIED = "VERIFIED_SUCCESS"
SUCCESS_LUCKY = "LUCKY_SUCCESS"
SUCCESS_PARTIAL = "PARTIAL_SUCCESS"
SUCCESS_UNSUPPORTED = "UNSUPPORTED_SUCCESS"

ALL_SUCCESS_CLASSIFICATIONS = {SUCCESS_VERIFIED, SUCCESS_LUCKY, SUCCESS_PARTIAL, SUCCESS_UNSUPPORTED}

FAIL_VALIDATION = "VALIDATION_FAILURE"
FAIL_POLICY = "POLICY_FAILURE"
FAIL_SANDBOX = "SANDBOX_FAILURE"
FAIL_PROMOTION_REJECTION = "PROMOTION_REJECTION"
FAIL_REGRESSION = "REGRESSION_FAILURE"
FAIL_USER_REJECTION = "USER_REJECTION"
FAIL_UNKNOWN = "UNKNOWN_FAILURE"

ALL_FAILURE_CLASSIFICATIONS = {FAIL_VALIDATION, FAIL_POLICY, FAIL_SANDBOX, FAIL_PROMOTION_REJECTION, FAIL_REGRESSION, FAIL_USER_REJECTION, FAIL_UNKNOWN}

EVIDENCE_STRONG = "STRONG"
EVIDENCE_MEDIUM = "MEDIUM"
EVIDENCE_WEAK = "WEAK"
EVIDENCE_MISSING = "MISSING"
EVIDENCE_CONTRADICTORY = "CONTRADICTORY"

ALL_EVIDENCE_QUALITIES = {EVIDENCE_STRONG, EVIDENCE_MEDIUM, EVIDENCE_WEAK, EVIDENCE_MISSING, EVIDENCE_CONTRADICTORY}

SIGNAL_FIX_WORKED = "FIX_WORKED"
SIGNAL_FIX_FAILED = "FIX_FAILED"
SIGNAL_REGRESSION_DETECTED = "REGRESSION_DETECTED"
SIGNAL_POLICY_BLOCKED = "POLICY_BLOCKED"
SIGNAL_SANDBOX_BLOCKED = "SANDBOX_BLOCKED"
SIGNAL_TEST_GAP = "TEST_GAP"
SIGNAL_DOC_DRIFT = "DOC_DRIFT"
SIGNAL_REPEAT_FAILURE = "REPEAT_FAILURE"
SIGNAL_USER_REJECTION = "USER_REJECTION"
SIGNAL_PROMOTION_REJECTION = "PROMOTION_REJECTION"
SIGNAL_UNSUPPORTED = "UNSUPPORTED"

ALL_SIGNAL_TYPES = {SIGNAL_FIX_WORKED, SIGNAL_FIX_FAILED, SIGNAL_REGRESSION_DETECTED, SIGNAL_POLICY_BLOCKED, SIGNAL_SANDBOX_BLOCKED, SIGNAL_TEST_GAP, SIGNAL_DOC_DRIFT, SIGNAL_REPEAT_FAILURE, SIGNAL_USER_REJECTION, SIGNAL_PROMOTION_REJECTION, SIGNAL_UNSUPPORTED}

MEMORY_CANDIDATE_PROPOSED = "PROPOSED"
MEMORY_CANDIDATE_APPROVED = "APPROVED"
MEMORY_CANDIDATE_REJECTED = "REJECTED"
MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
MEMORY_CANDIDATE_BLOCKED = "BLOCKED"

ALL_MEMORY_CANDIDATE_STATUSES = {MEMORY_CANDIDATE_PROPOSED, MEMORY_CANDIDATE_APPROVED, MEMORY_CANDIDATE_REJECTED, MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW, MEMORY_CANDIDATE_BLOCKED}

LEARNING_ALLOW = "ALLOW"
LEARNING_BLOCK = "BLOCK"
LEARNING_NEEDS_APPROVAL = "NEEDS_APPROVAL"
LEARNING_NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
LEARNING_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
LEARNING_REJECT_UNSUPPORTED = "REJECT_UNSUPPORTED"

ALL_LEARNING_DECISIONS = {LEARNING_ALLOW, LEARNING_BLOCK, LEARNING_NEEDS_APPROVAL, LEARNING_NEEDS_HUMAN_REVIEW, LEARNING_NEEDS_MORE_EVIDENCE, LEARNING_REJECT_UNSUPPORTED}

VERDICT_NO_LEARNING_ALLOWED = "NO_LEARNING_ALLOWED"
VERDICT_LEARNING_CANDIDATES_PROPOSED = "LEARNING_CANDIDATES_PROPOSED"
VERDICT_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
VERDICT_NEEDS_HUMAN_APPROVAL = "NEEDS_HUMAN_APPROVAL"
VERDICT_LEARNING_APPROVED = "LEARNING_APPROVED"
VERDICT_REGRESSION_REVIEW_REQUIRED = "REGRESSION_REVIEW_REQUIRED"

ALL_LEARNING_VERDICTS = {VERDICT_NO_LEARNING_ALLOWED, VERDICT_LEARNING_CANDIDATES_PROPOSED, VERDICT_NEEDS_MORE_EVIDENCE, VERDICT_NEEDS_HUMAN_APPROVAL, VERDICT_LEARNING_APPROVED, VERDICT_REGRESSION_REVIEW_REQUIRED}

REJECT_MISSING_EVIDENCE = "MISSING_EVIDENCE"
REJECT_UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"
REJECT_OVERBROAD_CLAIM = "OVERBROAD_CLAIM"
REJECT_SECRET_OR_PROMPT = "SECRET_OR_PROMPT"
REJECT_POLICY_DENIED = "POLICY_DENIED"
REJECT_REGRESSION_UNRESOLVED = "REGRESSION_UNRESOLVED"
REJECT_PROMOTION_REJECTED = "PROMOTION_REJECTED"
REJECT_FAILED_VALIDATION = "FAILED_VALIDATION"
REJECT_SENSITIVE_DATA = "SENSITIVE_DATA"

ALL_REJECTION_REASONS = {REJECT_MISSING_EVIDENCE, REJECT_UNSUPPORTED_CLAIM, REJECT_OVERBROAD_CLAIM, REJECT_SECRET_OR_PROMPT, REJECT_POLICY_DENIED, REJECT_REGRESSION_UNRESOLVED, REJECT_PROMOTION_REJECTED, REJECT_FAILED_VALIDATION, REJECT_SENSITIVE_DATA}

CANDIDATE_TYPE_BEHAVIOR_RULE = "BEHAVIOR_RULE"
CANDIDATE_TYPE_VALIDATION_PATTERN = "VALIDATION_PATTERN"
CANDIDATE_TYPE_FAILURE_PATTERN = "FAILURE_PATTERN"
CANDIDATE_TYPE_DOC_PATTERN = "DOC_PATTERN"
CANDIDATE_TYPE_PROMOTION_PATTERN = "PROMOTION_PATTERN"
CANDIDATE_TYPE_REGRESSION_PATTERN = "REGRESSION_PATTERN"
CANDIDATE_TYPE_BLOCKED_UNSAFE = "BLOCKED_UNSAFE"

ALL_CANDIDATE_TYPES = {CANDIDATE_TYPE_BEHAVIOR_RULE, CANDIDATE_TYPE_VALIDATION_PATTERN, CANDIDATE_TYPE_FAILURE_PATTERN, CANDIDATE_TYPE_DOC_PATTERN, CANDIDATE_TYPE_PROMOTION_PATTERN, CANDIDATE_TYPE_REGRESSION_PATTERN, CANDIDATE_TYPE_BLOCKED_UNSAFE}

SCOPE_COMPONENT = "component"
SCOPE_LAYER = "layer"
SCOPE_REPOSITORY = "repository"
SCOPE_TASK_TYPE = "task_type"
SCOPE_VALIDATION_PATTERN = "validation_pattern"
SCOPE_FAILURE_PATTERN = "failure_pattern"
SCOPE_DOCUMENTATION_PATTERN = "documentation_pattern"
SCOPE_PROMOTION_PATTERN = "promotion_pattern"
SCOPE_REGRESSION_PATTERN = "regression_pattern"

ALL_CANDIDATE_SCOPES = {SCOPE_COMPONENT, SCOPE_LAYER, SCOPE_REPOSITORY, SCOPE_TASK_TYPE, SCOPE_VALIDATION_PATTERN, SCOPE_FAILURE_PATTERN, SCOPE_DOCUMENTATION_PATTERN, SCOPE_PROMOTION_PATTERN, SCOPE_REGRESSION_PATTERN}

REGRESSION_LINK_CONFIRMED = "CONFIRMED"
REGRESSION_LINK_SUSPECTED = "SUSPECTED"
REGRESSION_LINK_LOW_CONFIDENCE = "LOW_CONFIDENCE"
REGRESSION_LINK_REJECTED = "REJECTED"
REGRESSION_LINK_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"

ALL_REGRESSION_LINK_STATUSES = {REGRESSION_LINK_CONFIRMED, REGRESSION_LINK_SUSPECTED, REGRESSION_LINK_LOW_CONFIDENCE, REGRESSION_LINK_REJECTED, REGRESSION_LINK_NEEDS_MORE_EVIDENCE}

PROPOSAL_CREATED = "CREATED"
PROPOSAL_POLICY_BLOCKED = "POLICY_BLOCKED"
PROPOSAL_NEEDS_APPROVAL = "NEEDS_APPROVAL"
PROPOSAL_SUBMITTED = "SUBMITTED"
PROPOSAL_DEFERRED = "DEFERRED"

ALL_PROPOSAL_STATUSES = {PROPOSAL_CREATED, PROPOSAL_POLICY_BLOCKED, PROPOSAL_NEEDS_APPROVAL, PROPOSAL_SUBMITTED, PROPOSAL_DEFERRED}

DEPENDENCY_AVAILABLE = "AVAILABLE"
DEPENDENCY_MISSING = "MISSING"
DEPENDENCY_UNSTABLE = "UNSTABLE"
DEPENDENCY_CONTEXT_PROVIDED = "CONTEXT_PROVIDED"
DEPENDENCY_BLOCKED = "BLOCKED"

ALL_DEPENDENCY_STATUSES = {DEPENDENCY_AVAILABLE, DEPENDENCY_MISSING, DEPENDENCY_UNSTABLE, DEPENDENCY_CONTEXT_PROVIDED, DEPENDENCY_BLOCKED}

ANTI_POISONING_PROMPT_INJECTION = "PROMPT_INJECTION"
ANTI_POISONING_POLICY_WEAKENING = "POLICY_WEAKENING"
ANTI_POISONING_SANDBOX_BYPASS = "SANDBOX_BYPASS"
ANTI_POISONING_TEST_SKIPPING = "TEST_SKIPPING"
ANTI_POISONING_SECRET = "SECRET"
ANTI_POISONING_RAW_PROMPT = "RAW_PROMPT"
ANTI_POISONING_SENSITIVE_DATA = "SENSITIVE_DATA"
ANTI_POISONING_MODEL_ONLY_CLAIM = "MODEL_ONLY_CLAIM"
ANTI_POISONING_OVERBROAD = "OVERBROAD"
ANTI_POISONING_CONTRADICTS_EVIDENCE = "CONTRADICTS_EVIDENCE"

ALL_ANTI_POISONING_FLAGS = {ANTI_POISONING_PROMPT_INJECTION, ANTI_POISONING_POLICY_WEAKENING, ANTI_POISONING_SANDBOX_BYPASS, ANTI_POISONING_TEST_SKIPPING, ANTI_POISONING_SECRET, ANTI_POISONING_RAW_PROMPT, ANTI_POISONING_SENSITIVE_DATA, ANTI_POISONING_MODEL_ONLY_CLAIM, ANTI_POISONING_OVERBROAD, ANTI_POISONING_CONTRADICTS_EVIDENCE}

_LEARNING_SCHEMA_VERSION = "1.0"

_SECRET_PATTERNS = [
    re.compile(r'api[-_]?key', re.IGNORECASE),
    re.compile(r'secret', re.IGNORECASE),
    re.compile(r'token', re.IGNORECASE),
    re.compile(r'credential', re.IGNORECASE),
    re.compile(r'password', re.IGNORECASE),
    re.compile(r'-----BEGIN.*KEY-----'),
    re.compile(r'sk-[a-zA-Z0-9]{20,}'),
    re.compile(r'ghp_[a-zA-Z0-9]{36}'),
    re.compile(r'gho_[a-zA-Z0-9]{36}'),
    re.compile(r'xox[bpras]-[a-zA-Z0-9]{10,}'),
    re.compile(r'AKIA[0-9A-Z]{16}'),
]

_RAW_PROMPT_MARKERS = [
    "system prompt", "user prompt", "assistant prompt",
    "<<<system>>>", "<<<user>>>", "<<<assistant>>>",
    "you are an ai", "you are a helpful",
    "your task is to", "you must",
]

_POLICY_WEAKENING_PATTERNS = [
    re.compile(r'ignore\s+(all\s+)?(policy|rule|safety|restriction)', re.IGNORECASE),
    re.compile(r'bypass\s+(all\s+)?(policy|safety|approval|review|restriction|sandbox)', re.IGNORECASE),
    re.compile(r'skip\s+(all\s+)?(test|validation|check|evidence)', re.IGNORECASE),
    re.compile(r'approve\s+(yourself|your.own|self.?approve)', re.IGNORECASE),
    re.compile(r'never\s+ask\s+for\s+(approval|review|permission)', re.IGNORECASE),
    re.compile(r'disable\s+(safety|policy|sandbox|review)', re.IGNORECASE),
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "lr") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:16]}"


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if isinstance(val, list):
                result[f] = [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in val]
            elif isinstance(val, dict):
                result[f] = {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in val.items()}
            else:
                result[f] = val
        return result
    if isinstance(obj, dict):
        return {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in obj]
    return obj


def clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def stable_hash_dict(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def redact_learning_text(text: str) -> str:
    if not text:
        return text
    result = text
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    for marker in _RAW_PROMPT_MARKERS:
        if marker.lower() in result.lower():
            result = result.replace(marker, "[REDACTED]")
    return result


def scan_anti_poisoning(text: str) -> list[str]:
    flags: list[str] = []
    if not text:
        return flags
    for pattern in _POLICY_WEAKENING_PATTERNS:
        if pattern.search(text):
            flags.append(ANTI_POISONING_POLICY_WEAKENING)
            break
    for pattern in _SECRET_PATTERNS:
        if pattern.search(text):
            if ANTI_POISONING_SECRET not in flags:
                flags.append(ANTI_POISONING_SECRET)
    for marker in _RAW_PROMPT_MARKERS:
        if marker.lower() in text.lower():
            if ANTI_POISONING_RAW_PROMPT not in flags:
                flags.append(ANTI_POISONING_RAW_PROMPT)
            break
    if len(text) > 500:
        flags.append(ANTI_POISONING_OVERBROAD)
    return flags


@dataclass
class OutcomeEvent:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "outcome_event.schema.json"
    event_id: str = ""
    created_at: str = ""
    source_component: str = ""
    session_id: str | None = None
    run_id: str | None = None
    task_id: str | None = None
    commit_before: str | None = None
    commit_after: str | None = None
    outcome_status: str = ""
    summary: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    validation_refs: list[str] = field(default_factory=list)
    promotion_refs: list[str] = field(default_factory=list)
    documentation_refs: list[str] = field(default_factory=list)
    monitoring_refs: list[str] = field(default_factory=list)
    policy_refs: list[str] = field(default_factory=list)
    sandbox_refs: list[str] = field(default_factory=list)
    user_feedback_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class OutcomeReview:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "outcome_review.schema.json"
    review_id: str = ""
    created_at: str = ""
    source_component: str = "LongTermLearningOutcomeReview"
    event_id: str = ""
    outcome_status: str = ""
    review_status: str = ""
    success_classification: str | None = None
    failure_classification: str | None = None
    regression_detected: bool = False
    learning_allowed: bool = False
    learning_blockers: list[str] = field(default_factory=list)
    evidence_quality: str = EVIDENCE_MISSING
    confidence: float = 0.0
    summary: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class LearningSignal:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "learning_signal.schema.json"
    signal_id: str = ""
    created_at: str = ""
    source_component: str = "LearningSignalExtractor"
    review_id: str = ""
    signal_type: str = ""
    claim: str = ""
    supporting_evidence_refs: list[str] = field(default_factory=list)
    contradicting_evidence_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0
    eligible_for_memory: bool = False
    requires_human_review: bool = True
    anti_poisoning_flags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class MemoryCandidate:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "memory_candidate.schema.json"
    candidate_id: str = ""
    created_at: str = ""
    source_component: str = "MemoryCandidateBuilder"
    signal_id: str = ""
    candidate_text: str = ""
    candidate_type: str = ""
    scope: str = ""
    status: str = MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW
    requires_human_approval: bool = True
    policy_decision_id: str | None = None
    supporting_evidence_refs: list[str] = field(default_factory=list)
    contradicting_evidence_refs: list[str] = field(default_factory=list)
    rejection_reason: str | None = None
    hash_of_candidate_text: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class LearningPolicyDecision:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "learning_policy_decision.schema.json"
    decision_id: str = ""
    created_at: str = ""
    source_component: str = "LearningPolicy"
    candidate_id: str | None = None
    signal_id: str | None = None
    decision: str = LEARNING_BLOCK
    reason: str = ""
    required_checks: list[str] = field(default_factory=list)
    missing_checks: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    policy_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class RegressionLink:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "regression_link.schema.json"
    regression_link_id: str = ""
    created_at: str = ""
    source_component: str = "RegressionLinker"
    event_id: str = ""
    review_id: str = ""
    suspected_commit: str | None = None
    suspected_change_refs: list[str] = field(default_factory=list)
    failing_test_refs: list[str] = field(default_factory=list)
    prior_passing_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0
    status: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class FollowUpTaskProposal:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "follow_up_task_proposal.schema.json"
    proposal_id: str = ""
    created_at: str = ""
    source_component: str = "LearningSchedulerAdapter"
    review_id: str = ""
    reason: str = ""
    proposed_task_type: str = ""
    proposed_summary: str = ""
    requires_scheduler_approval: bool = True
    scheduler_decision_ref: str | None = None
    status: str = PROPOSAL_CREATED
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class OutcomeReviewReport:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "outcome_review_report.schema.json"
    report_id: str = ""
    created_at: str = ""
    source_component: str = "LearningReporter"
    event_id: str = ""
    review_id: str = ""
    outcome_status: str = ""
    signals: list[dict] = field(default_factory=list)
    memory_candidates: list[dict] = field(default_factory=list)
    policy_decisions: list[dict] = field(default_factory=list)
    regression_links: list[dict] = field(default_factory=list)
    follow_up_task_proposals: list[dict] = field(default_factory=list)
    final_learning_verdict: str = VERDICT_NO_LEARNING_ALLOWED
    summary: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class LearningAuditEvent:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "learning_audit_event.schema.json"
    audit_id: str = ""
    created_at: str = ""
    source_component: str = ""
    event_type: str = ""
    entity_type: str = ""
    entity_id: str = ""
    status: str = ""
    message: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class LearningAdapterResult:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "learning_adapter_result.schema.json"
    adapter_name: str = ""
    created_at: str = ""
    dependency_status: str = DEPENDENCY_MISSING
    status: str = ""
    summary: str = ""
    data: dict = field(default_factory=dict)
    evidence_refs: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class LearningLockRecord:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "learning_lock.schema.json"
    lock_id: str = ""
    created_at: str = ""
    review_key: str = ""
    lock_path: str = ""
    owner_session_id: str | None = None
    expires_at: str = ""
    status: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class LearningReviewIndex:
    schema_version: str = _LEARNING_SCHEMA_VERSION
    schema_id: str = "learning_review_index.schema.json"
    index_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    source_component: str = "LearningReviewIndex"
    review_keys: list[str] = field(default_factory=list)
    candidate_hashes: list[str] = field(default_factory=list)
    approved_candidate_hashes: list[str] = field(default_factory=list)
    blocked_candidate_hashes: list[str] = field(default_factory=list)
    latest_report_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)
