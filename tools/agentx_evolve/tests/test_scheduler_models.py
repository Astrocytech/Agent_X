import pytest
from agentx_evolve.scheduler.scheduler_models import (
    utc_now_iso, new_id, sha256_bytes, to_dict,
    TaskRecord, SessionRecord, QueueState, TaskClaim,
    SchedulerEvent, SchedulerAudit, SchedulerPolicyDecision,
    DeadLetterRecord, DependencyResolution,
    SchedulerEvidenceManifest, SchedulerReviewReport, SchedulerCompletionRecord,
    SchedulerConfig,
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED,
    SCHEDULER_STATUS_RUNNING, SCHEDULER_STATUS_COMPLETED,
    SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_CANCELLED,
    SCHEDULER_STATUS_BLOCKED, SCHEDULER_STATUS_PENDING_REVIEW,
    SCHEDULER_SESSION_STATUS_ACTIVE, SCHEDULER_SESSION_STATUS_CLOSED,
    SCHEDULER_CLAIM_STATUS_ACTIVE,
    SCHEDULER_LEASE_STATUS_ACTIVE,
    SCHEDULER_LOCK_STATUS_ACTIVE,
    SCHEDULER_POLICY_ALLOW, SCHEDULER_POLICY_DENY,
    SCHEDULER_VALID_TRANSITIONS,
    TASK_PRIORITY_LOW, TASK_PRIORITY_MEDIUM, TASK_PRIORITY_HIGH, TASK_PRIORITY_CRITICAL,
    compute_task_record_hash, compute_session_record_hash, canonical_json,
)


def test_utc_now_iso_format():
    now = utc_now_iso()
    assert now.endswith("Z")
    assert "T" in now


def test_new_id_prefix():
    nid = new_id("test")
    assert nid.startswith("test_")


def test_sha256_bytes():
    h = sha256_bytes("hello")
    assert isinstance(h, str)
    assert len(h) == 64


def test_task_record_defaults():
    t = TaskRecord(record_id="r1", task_id="t1", session_id="s1")
    assert t.status == SCHEDULER_STATUS_QUEUED
    assert t.priority == TASK_PRIORITY_MEDIUM
    assert t.revision == 1
    assert t.retry_count == 0


def test_task_record_to_dict():
    t = TaskRecord(record_id="r1", task_id="t1", session_id="s1")
    d = to_dict(t)
    assert d["record_id"] == "r1"
    assert d["task_id"] == "t1"
    assert d["schema_id"] == "task_record.schema.json"


def test_session_record():
    s = SessionRecord(record_id="sr1", session_id="ses1")
    assert s.status == SCHEDULER_SESSION_STATUS_ACTIVE
    d = to_dict(s)
    assert d["session_id"] == "ses1"


def test_queue_state():
    q = QueueState(queue_id="q1", total_tasks=5, by_status={"QUEUED": 5})
    d = to_dict(q)
    assert d["total_tasks"] == 5
    assert d["queue_id"] == "q1"


def test_task_claim():
    c = TaskClaim(claim_id="c1", task_id="t1", session_id="s1", lease_id="l1")
    assert c.claim_status == SCHEDULER_CLAIM_STATUS_ACTIVE


def test_scheduler_event():
    e = SchedulerEvent(event_id="e1", event_type="TASK_QUEUED")
    assert e.component_id == "AGENTX_TASK_QUEUE_SESSION_SCHEDULER"


def test_scheduler_audit():
    a = SchedulerAudit(audit_id="a1", action="create_task", performed_by="test", outcome="ALLOW")
    assert a.outcome == "ALLOW"


def test_policy_decision():
    d = SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "test", "fallback")
    assert d.decision == SCHEDULER_POLICY_ALLOW


def test_dead_letter_record():
    dl = DeadLetterRecord(dead_letter_id="dl1", task_id="t1", session_id="s1", reason="max retries")
    assert dl.reason == "max retries"


def test_dependency_resolution():
    dep = DependencyResolution(dependency_id="dep1", task_id="t1", depends_on_task_id="t0")
    assert dep.satisfied is False


def test_evidence_manifest_defaults():
    m = SchedulerEvidenceManifest()
    assert m.final_decision == "DONE"


def test_review_report_defaults():
    r = SchedulerReviewReport()
    assert r.implementation_rating == 10.0
    assert r.final_verdict == "DONE"


def test_completion_record_defaults():
    c = SchedulerCompletionRecord()
    assert c.implementation_score == 10.0
    assert c.canonical_scheduler_subdirectory == "tools/agentx_evolve/scheduler/"


def test_scheduler_config():
    cfg = SchedulerConfig()
    assert cfg.max_retries_default == 3
    assert cfg.lease_duration_seconds == 300
    assert cfg.config_id.startswith("cfg_")


def test_valid_transitions():
    assert SCHEDULER_STATUS_COMPLETED in SCHEDULER_VALID_TRANSITIONS[SCHEDULER_STATUS_RUNNING]
    assert SCHEDULER_STATUS_RUNNING not in SCHEDULER_VALID_TRANSITIONS[SCHEDULER_STATUS_COMPLETED]
    assert SCHEDULER_STATUS_QUEUED in SCHEDULER_VALID_TRANSITIONS[SCHEDULER_STATUS_BLOCKED]


def test_compute_task_record_hash():
    t = TaskRecord(record_id="r1", task_id="t1", session_id="s1")
    d = to_dict(t)
    h = compute_task_record_hash(d)
    assert isinstance(h, str)
    assert len(h) == 64


def test_compute_session_record_hash():
    s = SessionRecord(record_id="sr1", session_id="ses1")
    d = to_dict(s)
    h = compute_session_record_hash(d)
    assert isinstance(h, str)
    assert len(h) == 64


def test_canonical_json():
    data = {"b": 2, "a": 1}
    cj = canonical_json(data)
    assert '"a":1' in cj
    assert '"b":2' in cj


def test_priority_constants():
    assert TASK_PRIORITY_LOW < TASK_PRIORITY_MEDIUM
    assert TASK_PRIORITY_MEDIUM < TASK_PRIORITY_HIGH
    assert TASK_PRIORITY_HIGH < TASK_PRIORITY_CRITICAL


def test_scheduler_status_values_complete():
    all_statuses = {
        SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED,
        SCHEDULER_STATUS_RUNNING, SCHEDULER_STATUS_COMPLETED,
        SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_CANCELLED,
        SCHEDULER_STATUS_BLOCKED, SCHEDULER_STATUS_PENDING_REVIEW,
    }
    from agentx_evolve.scheduler.scheduler_models import SCHEDULER_STATUS_VALUES
    assert all_statuses == SCHEDULER_STATUS_VALUES
