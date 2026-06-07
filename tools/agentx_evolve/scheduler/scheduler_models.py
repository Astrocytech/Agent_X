import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEDULER_STATUS_QUEUED = "QUEUED"
SCHEDULER_STATUS_CLAIMED = "CLAIMED"
SCHEDULER_STATUS_RUNNING = "RUNNING"
SCHEDULER_STATUS_COMPLETED = "COMPLETED"
SCHEDULER_STATUS_FAILED = "FAILED"
SCHEDULER_STATUS_CANCELLED = "CANCELLED"
SCHEDULER_STATUS_BLOCKED = "BLOCKED"
SCHEDULER_STATUS_PENDING_REVIEW = "PENDING_REVIEW"

SCHEDULER_CLAIM_STATUS_ACTIVE = "ACTIVE"
SCHEDULER_CLAIM_STATUS_RELEASED = "RELEASED"
SCHEDULER_CLAIM_STATUS_EXPIRED = "EXPIRED"
SCHEDULER_CLAIM_STATUS_FAILED = "FAILED"

SCHEDULER_LOCK_STATUS_ACTIVE = "ACTIVE"
SCHEDULER_LOCK_STATUS_STALE = "STALE"
SCHEDULER_LOCK_STATUS_RELEASED = "RELEASED"

SCHEDULER_LEASE_STATUS_ACTIVE = "ACTIVE"
SCHEDULER_LEASE_STATUS_RELEASED = "RELEASED"
SCHEDULER_LEASE_STATUS_EXPIRED = "EXPIRED"
SCHEDULER_LEASE_STATUS_FAILED = "FAILED"

SCHEDULER_SESSION_STATUS_ACTIVE = "ACTIVE"
SCHEDULER_SESSION_STATUS_HEARTBEAT = "HEARTBEAT"
SCHEDULER_SESSION_STATUS_CLOSED = "CLOSED"
SCHEDULER_SESSION_STATUS_STALE = "STALE"
SCHEDULER_SESSION_STATUS_FAILED = "FAILED"

SCHEDULER_POLICY_ALLOW = "ALLOW"
SCHEDULER_POLICY_DENY = "DENY"
SCHEDULER_POLICY_BLOCKED = "BLOCKED"
SCHEDULER_POLICY_NOT_APPLICABLE = "NOT_APPLICABLE"

TASK_PRIORITY_LOW = 0
TASK_PRIORITY_MEDIUM = 50
TASK_PRIORITY_HIGH = 80
TASK_PRIORITY_CRITICAL = 100

SCHEDULER_EVENT_QUEUED = "TASK_QUEUED"
SCHEDULER_EVENT_CLAIMED = "TASK_CLAIMED"
SCHEDULER_EVENT_RUNNING = "TASK_RUNNING"
SCHEDULER_EVENT_COMPLETED = "TASK_COMPLETED"
SCHEDULER_EVENT_FAILED = "TASK_FAILED"
SCHEDULER_EVENT_CANCELLED = "TASK_CANCELLED"
SCHEDULER_EVENT_BLOCKED = "TASK_BLOCKED"
SCHEDULER_EVENT_RECOVERED = "TASK_RECOVERED"
SCHEDULER_EVENT_LOCK_ACQUIRED = "LOCK_ACQUIRED"
SCHEDULER_EVENT_LOCK_RELEASED = "LOCK_RELEASED"
SCHEDULER_EVENT_LOCK_STALE = "LOCK_STALE"
SCHEDULER_EVENT_LEASE_ACQUIRED = "LEASE_ACQUIRED"
SCHEDULER_EVENT_LEASE_RELEASED = "LEASE_RELEASED"
SCHEDULER_EVENT_LEASE_EXPIRED = "LEASE_EXPIRED"
SCHEDULER_EVENT_HEARTBEAT = "SESSION_HEARTBEAT"
SCHEDULER_EVENT_SNAPSHOT = "QUEUE_SNAPSHOT"
SCHEDULER_EVENT_CORRUPTION = "QUEUE_CORRUPTION_DETECTED"
SCHEDULER_EVENT_QUARANTINE = "RECORD_QUARANTINED"
SCHEDULER_EVENT_POLICY_DENIED = "POLICY_DENIED"
SCHEDULER_EVENT_RETRY_SCHEDULED = "RETRY_SCHEDULED"
SCHEDULER_EVENT_DEAD_LETTER = "DEAD_LETTER"
SCHEDULER_EVENT_DEPENDENCY_BLOCKED = "DEPENDENCY_BLOCKED"

CENTRAL_STATUS_PASS = "PASS"
CENTRAL_STATUS_FAIL = "FAIL"
CENTRAL_STATUS_BLOCKED = "BLOCKED"
CENTRAL_STATUS_NOT_CHECKED = "NOT_CHECKED"
CENTRAL_STATUS_NOT_RUN = "NOT_RUN"

SCHEDULER_VALID_TRANSITIONS = {
    SCHEDULER_STATUS_QUEUED: [SCHEDULER_STATUS_CLAIMED, SCHEDULER_STATUS_CANCELLED, SCHEDULER_STATUS_BLOCKED],
    SCHEDULER_STATUS_CLAIMED: [SCHEDULER_STATUS_RUNNING, SCHEDULER_STATUS_CANCELLED, SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_BLOCKED],
    SCHEDULER_STATUS_RUNNING: [SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_BLOCKED],
    SCHEDULER_STATUS_COMPLETED: [],
    SCHEDULER_STATUS_FAILED: [SCHEDULER_STATUS_QUEUED],
    SCHEDULER_STATUS_CANCELLED: [],
    SCHEDULER_STATUS_BLOCKED: [SCHEDULER_STATUS_QUEUED],
    SCHEDULER_STATUS_PENDING_REVIEW: [SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CANCELLED],
}

SCHEDULER_STATUS_VALUES = frozenset([
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED, SCHEDULER_STATUS_RUNNING,
    SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_CANCELLED,
    SCHEDULER_STATUS_BLOCKED, SCHEDULER_STATUS_PENDING_REVIEW,
])

SCHEDULER_TERMINAL_STATUSES = frozenset([
    SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_CANCELLED,
])

SCHEDULER_SESSION_STATUS_VALUES = frozenset([
    SCHEDULER_SESSION_STATUS_ACTIVE, SCHEDULER_SESSION_STATUS_HEARTBEAT,
    SCHEDULER_SESSION_STATUS_CLOSED, SCHEDULER_SESSION_STATUS_STALE,
    SCHEDULER_SESSION_STATUS_FAILED,
])

SCHEDULER_ACTIVE_SESSION_STATUSES = frozenset([
    SCHEDULER_SESSION_STATUS_ACTIVE, SCHEDULER_SESSION_STATUS_HEARTBEAT,
])

SCHEDULER_CLAIM_STATUS_VALUES = frozenset([
    SCHEDULER_CLAIM_STATUS_ACTIVE, SCHEDULER_CLAIM_STATUS_RELEASED,
    SCHEDULER_CLAIM_STATUS_EXPIRED, SCHEDULER_CLAIM_STATUS_FAILED,
])

SCHEDULER_LEASE_STATUS_VALUES = frozenset([
    SCHEDULER_LEASE_STATUS_ACTIVE, SCHEDULER_LEASE_STATUS_RELEASED,
    SCHEDULER_LEASE_STATUS_EXPIRED, SCHEDULER_LEASE_STATUS_FAILED,
])

SCHEDULER_LOCK_STATUS_VALUES = frozenset([
    SCHEDULER_LOCK_STATUS_ACTIVE, SCHEDULER_LOCK_STATUS_STALE,
    SCHEDULER_LOCK_STATUS_RELEASED,
])


def utc_now_iso() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond:06d}Z"


def new_id(prefix: str = "sched") -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def sha256_bytes(content: str | bytes) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def canonical_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def compute_task_record_hash(record_dict: dict) -> str:
    excluded = {"task_record_hash"}
    data = {k: v for k, v in record_dict.items() if k not in excluded}
    return sha256_bytes(canonical_json(data))


def compute_session_record_hash(record_dict: dict) -> str:
    excluded = {"session_record_hash"}
    data = {k: v for k, v in record_dict.items() if k not in excluded}
    return sha256_bytes(canonical_json(data))


def to_dict(obj: Any) -> dict:
    result: dict = {}
    for cls in type(obj).__mro__:
        for slot in getattr(cls, "__slots__", ()):
            if hasattr(obj, slot):
                val = getattr(obj, slot)
                if val is not None:
                    result[slot] = val
    return result


class TaskRecord:
    __slots__ = (
        "schema_version", "schema_id", "record_id", "task_id", "session_id",
        "status", "priority", "payload_ref", "dependency_ids", "retry_count",
        "max_retries", "next_run_at", "previous_record_hash", "task_record_hash",
        "append_sequence", "revision", "created_at", "updated_at",
        "warnings", "errors",
    )

    def __init__(
        self,
        record_id: str,
        task_id: str,
        session_id: str,
        status: str = SCHEDULER_STATUS_QUEUED,
        priority: int = TASK_PRIORITY_MEDIUM,
        payload_ref: str = "",
        dependency_ids: list[str] | None = None,
        retry_count: int = 0,
        max_retries: int = 3,
        next_run_at: str | None = None,
        previous_record_hash: str = "",
        task_record_hash: str = "",
        append_sequence: int = 0,
        revision: int = 1,
        created_at: str | None = None,
        updated_at: str | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "task_record.schema.json",
    ):
        now = utc_now_iso()
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.record_id = record_id
        self.task_id = task_id
        self.session_id = session_id
        self.status = status
        self.priority = priority
        self.payload_ref = payload_ref
        self.dependency_ids = dependency_ids or []
        self.retry_count = retry_count
        self.max_retries = max_retries
        self.next_run_at = next_run_at
        self.previous_record_hash = previous_record_hash
        self.task_record_hash = task_record_hash
        self.append_sequence = append_sequence
        self.revision = revision
        self.created_at = created_at or now
        self.updated_at = updated_at or now
        self.warnings = warnings or []
        self.errors = errors or []


class SessionRecord:
    __slots__ = (
        "schema_version", "schema_id", "record_id", "session_id", "role",
        "status", "heartbeat_at", "created_at", "updated_at", "closed_at",
        "previous_record_hash", "session_record_hash", "append_sequence",
        "revision", "warnings", "errors",
    )

    def __init__(
        self,
        record_id: str,
        session_id: str,
        role: str = "default",
        status: str = SCHEDULER_SESSION_STATUS_ACTIVE,
        heartbeat_at: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        closed_at: str | None = None,
        previous_record_hash: str = "",
        session_record_hash: str = "",
        append_sequence: int = 0,
        revision: int = 1,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "session_record.schema.json",
    ):
        now = utc_now_iso()
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.record_id = record_id
        self.session_id = session_id
        self.role = role
        self.status = status
        self.heartbeat_at = heartbeat_at
        self.created_at = created_at or now
        self.updated_at = updated_at or now
        self.closed_at = closed_at
        self.previous_record_hash = previous_record_hash
        self.session_record_hash = session_record_hash
        self.append_sequence = append_sequence
        self.revision = revision
        self.warnings = warnings or []
        self.errors = errors or []


class QueueState:
    __slots__ = (
        "schema_version", "schema_id", "queue_id", "snapshot_at",
        "total_tasks", "by_status", "queue_hash", "warnings", "errors",
    )

    def __init__(
        self,
        queue_id: str,
        snapshot_at: str | None = None,
        total_tasks: int = 0,
        by_status: dict[str, int] | None = None,
        queue_hash: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "queue_state.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.queue_id = queue_id
        self.snapshot_at = snapshot_at or utc_now_iso()
        self.total_tasks = total_tasks
        self.by_status = by_status or {}
        self.queue_hash = queue_hash
        self.warnings = warnings or []
        self.errors = errors or []


class TaskClaim:
    __slots__ = (
        "schema_version", "schema_id", "claim_id", "task_id", "session_id",
        "claim_status", "lease_id", "claimed_at", "expires_at", "released_at",
        "warnings", "errors",
    )

    def __init__(
        self,
        claim_id: str,
        task_id: str,
        session_id: str,
        lease_id: str,
        claim_status: str = SCHEDULER_CLAIM_STATUS_ACTIVE,
        claimed_at: str | None = None,
        expires_at: str | None = None,
        released_at: str | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "task_claim.schema.json",
    ):
        now = utc_now_iso()
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.claim_id = claim_id
        self.task_id = task_id
        self.session_id = session_id
        self.claim_status = claim_status
        self.lease_id = lease_id
        self.claimed_at = claimed_at or now
        self.expires_at = expires_at or now
        self.released_at = released_at
        self.warnings = warnings or []
        self.errors = errors or []


class SchedulerEvent:
    __slots__ = (
        "schema_version", "schema_id", "event_id", "event_type", "timestamp",
        "component_id", "task_id", "session_id", "claim_id", "lease_id",
        "details", "warnings", "errors",
    )

    def __init__(
        self,
        event_id: str,
        event_type: str,
        task_id: str | None = None,
        session_id: str | None = None,
        claim_id: str | None = None,
        lease_id: str | None = None,
        details: dict | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "scheduler_event.schema.json",
        component_id: str = "AGENTX_TASK_QUEUE_SESSION_SCHEDULER",
        timestamp: str | None = None,
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.event_id = event_id
        self.event_type = event_type
        self.timestamp = timestamp or utc_now_iso()
        self.component_id = component_id
        self.task_id = task_id
        self.session_id = session_id
        self.claim_id = claim_id
        self.lease_id = lease_id
        self.details = details or {}
        self.warnings = warnings or []
        self.errors = errors or []


class SchedulerAudit:
    __slots__ = (
        "schema_version", "schema_id", "audit_id", "action", "performed_by",
        "timestamp", "outcome", "task_id", "session_id", "details",
        "warnings", "errors",
    )

    def __init__(
        self,
        audit_id: str,
        action: str,
        performed_by: str,
        outcome: str,
        task_id: str | None = None,
        session_id: str | None = None,
        details: dict | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "scheduler_audit.schema.json",
        timestamp: str | None = None,
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.audit_id = audit_id
        self.action = action
        self.performed_by = performed_by
        self.timestamp = timestamp or utc_now_iso()
        self.outcome = outcome
        self.task_id = task_id
        self.session_id = session_id
        self.details = details or {}
        self.warnings = warnings or []
        self.errors = errors or []


class SchedulerPolicyDecision:
    __slots__ = ("decision", "reason", "policy_source")

    def __init__(
        self,
        decision: str = SCHEDULER_POLICY_DENY,
        reason: str = "",
        policy_source: str = "default_policy",
    ):
        self.decision = decision
        self.reason = reason
        self.policy_source = policy_source


class DeadLetterRecord:
    __slots__ = (
        "schema_version", "schema_id", "dead_letter_id", "task_id",
        "session_id", "reason", "original_status", "details",
        "created_at", "warnings", "errors",
    )

    def __init__(
        self,
        dead_letter_id: str,
        task_id: str,
        session_id: str,
        reason: str,
        original_status: str = SCHEDULER_STATUS_FAILED,
        details: dict | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "dead_letter_record.schema.json",
        created_at: str | None = None,
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.dead_letter_id = dead_letter_id
        self.task_id = task_id
        self.session_id = session_id
        self.reason = reason
        self.original_status = original_status
        self.details = details or {}
        self.created_at = created_at or utc_now_iso()
        self.warnings = warnings or []
        self.errors = errors or []


class DeadLetterQueue:
    __slots__ = ("records",)
    def __init__(self, records: list[DeadLetterRecord] | None = None):
        self.records = records or []

    def add(self, record: DeadLetterRecord) -> None:
        self.records.append(record)

    def retry(self, task_id: str) -> DeadLetterRecord | None:
        for i, r in enumerate(self.records):
            if r.task_id == task_id:
                return self.records.pop(i)
        return None

    def __len__(self) -> int:
        return len(self.records)


class DependencyResolution:
    __slots__ = (
        "schema_version", "schema_id", "dependency_id", "task_id",
        "depends_on_task_id", "satisfied", "satisfied_at", "details",
        "warnings", "errors",
    )

    def __init__(
        self,
        dependency_id: str,
        task_id: str,
        depends_on_task_id: str,
        satisfied: bool = False,
        satisfied_at: str | None = None,
        details: dict | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "dependency_resolution.schema.json",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.dependency_id = dependency_id
        self.task_id = task_id
        self.depends_on_task_id = depends_on_task_id
        self.satisfied = satisfied
        self.satisfied_at = satisfied_at
        self.details = details or {}
        self.warnings = warnings or []
        self.errors = errors or []


class DependencyResolver:
    def resolve(self, task: TaskRecord, effective: dict[str, TaskRecord]) -> bool:
        if not task.dependency_ids:
            return True
        for dep_id in task.dependency_ids:
            dep = effective.get(dep_id)
            if dep is None or dep.status != SCHEDULER_STATUS_COMPLETED:
                return False
        return True


def resolve_dependencies(tasks: list[TaskRecord], effective: dict[str, TaskRecord]) -> dict[str, bool]:
    resolver = DependencyResolver()
    return {t.task_id: resolver.resolve(t, effective) for t in tasks}


class SchedulerEvidenceManifest:
    __slots__ = (
        "schema_version", "schema_id", "component_id", "validated_commit",
        "validated_at", "commands", "evidence_files", "evidence_file_hashes",
        "runtime_artifacts", "known_expected_runtime_artifacts",
        "deviation_register", "source_mutation_status", "queue_status",
        "session_status", "lock_status", "lease_status", "retry_status",
        "recovery_status", "observability_status", "hash_status", "final_decision",
    )

    def __init__(
        self,
        validated_commit: str = "",
        validated_at: str | None = None,
        commands: list[str] | None = None,
        evidence_files: list[str] | None = None,
        evidence_file_hashes: list[str] | None = None,
        runtime_artifacts: list[str] | None = None,
        known_expected_runtime_artifacts: list[str] | None = None,
        deviation_register: list[str] | None = None,
        source_mutation_status: str = CENTRAL_STATUS_PASS,
        queue_status: str = CENTRAL_STATUS_PASS,
        session_status: str = CENTRAL_STATUS_PASS,
        lock_status: str = CENTRAL_STATUS_PASS,
        lease_status: str = CENTRAL_STATUS_PASS,
        retry_status: str = CENTRAL_STATUS_PASS,
        recovery_status: str = CENTRAL_STATUS_PASS,
        observability_status: str = CENTRAL_STATUS_PASS,
        hash_status: str = CENTRAL_STATUS_PASS,
        final_decision: str = "DONE",
        schema_version: str = "1.0",
        schema_id: str = "scheduler_evidence_manifest.schema.json",
        component_id: str = "AGENTX_TASK_QUEUE_SESSION_SCHEDULER",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.component_id = component_id
        self.validated_commit = validated_commit
        self.validated_at = validated_at or utc_now_iso()
        self.commands = commands or []
        self.evidence_files = evidence_files or []
        self.evidence_file_hashes = evidence_file_hashes or []
        self.runtime_artifacts = runtime_artifacts or []
        self.known_expected_runtime_artifacts = known_expected_runtime_artifacts or []
        self.deviation_register = deviation_register or []
        self.source_mutation_status = source_mutation_status
        self.queue_status = queue_status
        self.session_status = session_status
        self.lock_status = lock_status
        self.lease_status = lease_status
        self.retry_status = retry_status
        self.recovery_status = recovery_status
        self.observability_status = observability_status
        self.hash_status = hash_status
        self.final_decision = final_decision


class SchedulerReviewReport:
    __slots__ = (
        "schema_version", "schema_id", "component_id", "review_document_id",
        "implementation_spec_id", "implementation_spec_version",
        "reviewed_commit", "reviewed_at", "commands_run", "coverage_statuses",
        "blockers", "high_issues", "non_blocking_followups",
        "deviation_register", "evidence_manifest_path",
        "evidence_manifest_sha256", "review_report_sha256",
        "completion_record_path", "completion_record_sha256",
        "implementation_rating", "final_verdict",
    )

    def __init__(
        self,
        reviewed_commit: str = "",
        reviewed_at: str | None = None,
        commands_run: list[str] | None = None,
        coverage_statuses: dict[str, str] | None = None,
        blockers: list[str] | None = None,
        high_issues: list[str] | None = None,
        non_blocking_followups: list[str] | None = None,
        deviation_register: list[str] | None = None,
        evidence_manifest_path: str = "",
        evidence_manifest_sha256: str = "",
        review_report_sha256: str = "",
        completion_record_path: str = "",
        completion_record_sha256: str = "",
        implementation_rating: float = 10.0,
        final_verdict: str = "DONE",
        schema_version: str = "1.0",
        schema_id: str = "scheduler_review_report.schema.json",
        component_id: str = "AGENTX_TASK_QUEUE_SESSION_SCHEDULER",
        review_document_id: str = "TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_REVIEW_AND_DOD",
        implementation_spec_id: str = "TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_SPEC",
        implementation_spec_version: str = "v3.0",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.component_id = component_id
        self.review_document_id = review_document_id
        self.implementation_spec_id = implementation_spec_id
        self.implementation_spec_version = implementation_spec_version
        self.reviewed_commit = reviewed_commit
        self.reviewed_at = reviewed_at or utc_now_iso()
        self.commands_run = commands_run or []
        self.coverage_statuses = coverage_statuses or {}
        self.blockers = blockers or []
        self.high_issues = high_issues or []
        self.non_blocking_followups = non_blocking_followups or []
        self.deviation_register = deviation_register or []
        self.evidence_manifest_path = evidence_manifest_path
        self.evidence_manifest_sha256 = evidence_manifest_sha256
        self.review_report_sha256 = review_report_sha256
        self.completion_record_path = completion_record_path
        self.completion_record_sha256 = completion_record_sha256
        self.implementation_rating = implementation_rating
        self.final_verdict = final_verdict


class SchedulerCompletionRecord:
    __slots__ = (
        "schema_version", "schema_id", "component_id", "component_name",
        "status", "validated_commit", "validated_at",
        "canonical_scheduler_subdirectory", "canonical_schema_subdirectory",
        "canonical_test_subdirectory", "runtime_artifact_root",
        "basis_documents", "commands_run", "files_created_or_changed",
        "schemas_created_or_changed", "tests_created_or_changed",
        "validated_capabilities", "queue_coverage_verified",
        "session_coverage_verified", "locking_coverage_verified",
        "lease_coverage_verified", "retry_coverage_verified",
        "crash_recovery_coverage_verified", "tool_adapter_integration_verified",
        "policy_integration_verified", "failure_taxonomy_integration_verified",
        "observability_integration_verified", "negative_tests_verified",
        "evidence_manifest_path", "evidence_manifest_sha256",
        "review_report_path", "review_report_sha256",
        "completion_record_sha256", "deviations_from_contract",
        "unresolved_risks", "implementation_score", "final_decision",
    )

    def __init__(
        self,
        status: str = "VALIDATED",
        validated_commit: str = "",
        validated_at: str | None = None,
        basis_documents: list[str] | None = None,
        commands_run: list[str] | None = None,
        files_created_or_changed: list[str] | None = None,
        schemas_created_or_changed: list[str] | None = None,
        tests_created_or_changed: list[str] | None = None,
        validated_capabilities: list[str] | None = None,
        queue_coverage_verified: list[str] | None = None,
        session_coverage_verified: list[str] | None = None,
        locking_coverage_verified: list[str] | None = None,
        lease_coverage_verified: list[str] | None = None,
        retry_coverage_verified: list[str] | None = None,
        crash_recovery_coverage_verified: list[str] | None = None,
        tool_adapter_integration_verified: list[str] | None = None,
        policy_integration_verified: list[str] | None = None,
        failure_taxonomy_integration_verified: list[str] | None = None,
        observability_integration_verified: list[str] | None = None,
        negative_tests_verified: list[str] | None = None,
        evidence_manifest_path: str = "",
        evidence_manifest_sha256: str = "",
        review_report_path: str = "",
        review_report_sha256: str = "",
        completion_record_sha256: str = "",
        deviations_from_contract: list[str] | None = None,
        unresolved_risks: list[str] | None = None,
        implementation_score: float = 10.0,
        final_decision: str = "DONE",
        schema_version: str = "1.0",
        schema_id: str = "scheduler_completion_record.schema.json",
        component_id: str = "AGENTX_TASK_QUEUE_SESSION_SCHEDULER",
        component_name: str = "Task Queue / Session Scheduler",
        canonical_scheduler_subdirectory: str = "tools/agentx_evolve/scheduler/",
        canonical_schema_subdirectory: str = "tools/agentx_evolve/schemas/",
        canonical_test_subdirectory: str = "tools/agentx_evolve/tests/",
        runtime_artifact_root: str = ".agentx-init/scheduler/",
    ):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.component_id = component_id
        self.component_name = component_name
        self.status = status
        self.validated_commit = validated_commit
        self.validated_at = validated_at or utc_now_iso()
        self.canonical_scheduler_subdirectory = canonical_scheduler_subdirectory
        self.canonical_schema_subdirectory = canonical_schema_subdirectory
        self.canonical_test_subdirectory = canonical_test_subdirectory
        self.runtime_artifact_root = runtime_artifact_root
        self.basis_documents = basis_documents or [
            "TASK_QUEUE_SESSION_SCHEDULER_EQC_FIC_SIB_SCHEMA_CONTRACT",
            "TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_SPEC_v3",
        ]
        self.commands_run = commands_run or []
        self.files_created_or_changed = files_created_or_changed or []
        self.schemas_created_or_changed = schemas_created_or_changed or []
        self.tests_created_or_changed = tests_created_or_changed or []
        self.validated_capabilities = validated_capabilities or []
        self.queue_coverage_verified = queue_coverage_verified or []
        self.session_coverage_verified = session_coverage_verified or []
        self.locking_coverage_verified = locking_coverage_verified or []
        self.lease_coverage_verified = lease_coverage_verified or []
        self.retry_coverage_verified = retry_coverage_verified or []
        self.crash_recovery_coverage_verified = crash_recovery_coverage_verified or []
        self.tool_adapter_integration_verified = tool_adapter_integration_verified or []
        self.policy_integration_verified = policy_integration_verified or []
        self.failure_taxonomy_integration_verified = failure_taxonomy_integration_verified or []
        self.observability_integration_verified = observability_integration_verified or []
        self.negative_tests_verified = negative_tests_verified or []
        self.evidence_manifest_path = evidence_manifest_path
        self.evidence_manifest_sha256 = evidence_manifest_sha256
        self.review_report_path = review_report_path
        self.review_report_sha256 = review_report_sha256
        self.completion_record_sha256 = completion_record_sha256
        self.deviations_from_contract = deviations_from_contract or []
        self.unresolved_risks = unresolved_risks or []
        self.implementation_score = implementation_score
        self.final_decision = final_decision


class SchedulerConfig:
    __slots__ = (
        "schema_version", "schema_id", "config_id", "queue_dir", "session_dir",
        "lease_dir", "lock_dir", "retry_dir", "crash_recovery_dir",
        "audit_dir", "event_dir", "evidence_dir", "max_retries_default",
        "lease_duration_seconds", "heartbeat_timeout_seconds",
        "stale_session_timeout_seconds", "stale_lock_timeout_seconds",
        "snapshot_interval_seconds", "max_queue_snapshot_records",
        "created_at", "updated_at", "config_hash", "warnings", "errors",
    )

    def __init__(
        self,
        config_id: str | None = None,
        queue_dir: str = ".agentx-init/scheduler/queue",
        session_dir: str = ".agentx-init/scheduler/sessions",
        lease_dir: str = ".agentx-init/scheduler/leases",
        lock_dir: str = ".agentx-init/scheduler/locks",
        retry_dir: str = ".agentx-init/scheduler/retries",
        crash_recovery_dir: str = ".agentx-init/scheduler/recovery",
        audit_dir: str = ".agentx-init/scheduler/audit",
        event_dir: str = ".agentx-init/scheduler/events",
        evidence_dir: str = ".agentx-init/scheduler",
        max_retries_default: int = 3,
        lease_duration_seconds: int = 300,
        heartbeat_timeout_seconds: int = 60,
        stale_session_timeout_seconds: int = 600,
        stale_lock_timeout_seconds: int = 600,
        snapshot_interval_seconds: int = 3600,
        max_queue_snapshot_records: int = 100000,
        created_at: str | None = None,
        updated_at: str | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        schema_version: str = "1.0",
        schema_id: str = "scheduler_config.schema.json",
    ):
        now = utc_now_iso()
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.config_id = config_id or new_id("cfg")
        self.queue_dir = queue_dir
        self.session_dir = session_dir
        self.lease_dir = lease_dir
        self.lock_dir = lock_dir
        self.retry_dir = retry_dir
        self.crash_recovery_dir = crash_recovery_dir
        self.audit_dir = audit_dir
        self.event_dir = event_dir
        self.evidence_dir = evidence_dir
        self.max_retries_default = max_retries_default
        self.lease_duration_seconds = lease_duration_seconds
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds
        self.stale_session_timeout_seconds = stale_session_timeout_seconds
        self.stale_lock_timeout_seconds = stale_lock_timeout_seconds
        self.snapshot_interval_seconds = snapshot_interval_seconds
        self.max_queue_snapshot_records = max_queue_snapshot_records
        self.created_at = created_at or now
        self.updated_at = updated_at or now
        self.config_hash = ""
        self.warnings = warnings or []
        self.errors = errors or []
