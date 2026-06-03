from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict,
    TaskRecord, QueueState, TaskClaim, DependencyResolution,
    SchedulerEvent,
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED,
    SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_CANCELLED,
    SCHEDULER_EVENT_CLAIMED,
)
from .queue_store import QueueStore
from .scheduler_validation import validate_task_record


DEFAULT_QUEUE_DIR = ".agentx-init/scheduler/queue"


def _queue_store(repo_root: str | Path) -> QueueStore:
    return QueueStore(Path(repo_root) / DEFAULT_QUEUE_DIR)


def create_task(arguments: dict, context: dict | None = None) -> TaskRecord:
    now = utc_now_iso()
    task_id = arguments.get("task_id", new_id("task"))
    session_id = arguments.get("session_id", context.get("session_id", "") if context else "")
    task = TaskRecord(
        record_id=new_id("rec"),
        task_id=task_id,
        session_id=session_id,
        status=arguments.get("status", SCHEDULER_STATUS_QUEUED),
        priority=arguments.get("priority", 50),
        payload_ref=arguments.get("payload_ref", ""),
        dependency_ids=arguments.get("dependency_ids", []),
        retry_count=arguments.get("retry_count", 0),
        max_retries=arguments.get("max_retries", 3),
        created_at=now,
        updated_at=now,
    )
    return task


def validate_task(task: TaskRecord) -> list[str]:
    return validate_task_record(to_dict(task))


def enqueue_task(task: TaskRecord, repo_root: str | Path) -> QueueState:
    store = _queue_store(repo_root)
    store.append_task(task)
    state, quarantined = store.build_snapshot()
    return state


def get_queue_state(repo_root: str | Path) -> QueueState:
    store = _queue_store(repo_root)
    snapshot = store.load_snapshot()
    if snapshot is not None:
        return snapshot
    state, quarantined = store.build_snapshot()
    return state


def claim_next_task(session: str, repo_root: str | Path) -> TaskClaim:
    store = _queue_store(repo_root)
    tasks, quarantined = store.replay_tasks()
    effective = {}
    for t in sorted(tasks, key=lambda x: (x.append_sequence, x.updated_at or "", x.record_id)):
        effective[t.task_id] = t

    from .lease_manager import LeaseManager
    lease_dir = Path(repo_root) / ".agentx-init/scheduler/leases"
    lease_mgr = LeaseManager(lease_dir)
    active_leases = lease_mgr._get_active_leases()

    candidate = None
    for t in sorted(effective.values(), key=lambda x: (x.created_at or "")):
        if t.status != SCHEDULER_STATUS_QUEUED:
            continue
        if t.task_id in active_leases:
            continue
        deps_blocked = False
        for dep_id in t.dependency_ids:
            dep_task = effective.get(dep_id)
            if dep_task is None or dep_task.status != SCHEDULER_STATUS_COMPLETED:
                deps_blocked = True
                break
        if deps_blocked:
            continue
        candidate = t
        break

    if candidate is None:
        return TaskClaim(
            claim_id=new_id("cl"),
            task_id="",
            session_id=session,
            lease_id="",
        )

    lease_result = lease_mgr.create_lease(candidate.task_id, session)
    claim = TaskClaim(
        claim_id=lease_result.get("claim_id", new_id("cl")),
        task_id=candidate.task_id,
        session_id=session,
        lease_id=lease_result.get("lease_id", ""),
        expires_at=lease_result.get("expires_at", utc_now_iso()),
    )

    event = SchedulerEvent(
        event_id=new_id("evt"),
        event_type=SCHEDULER_EVENT_CLAIMED,
        task_id=candidate.task_id,
        session_id=session,
        claim_id=claim.claim_id,
        lease_id=claim.lease_id,
        details={"claim_status": "ACTIVE"},
    )
    from .scheduler_evidence import SchedulerEvidenceWriter
    evidence_dir = Path(repo_root) / ".agentx-init/scheduler"
    writer = SchedulerEvidenceWriter(evidence_dir)
    writer._write_json(evidence_dir / "scheduler_event.jsonl", to_dict(event))

    return claim


def claim_task(task_id: str, session: str, repo_root: str | Path) -> TaskClaim:
    store = _queue_store(repo_root)
    tasks, quarantined = store.replay_tasks()
    effective = {}
    for t in sorted(tasks, key=lambda x: (x.append_sequence, x.updated_at or "", x.record_id)):
        effective[t.task_id] = t

    task = effective.get(task_id)
    if task is None:
        return TaskClaim(
            claim_id=new_id("cl"),
            task_id=task_id,
            session_id=session,
            lease_id="",
        )

    from .lease_manager import LeaseManager
    lease_dir = Path(repo_root) / ".agentx-init/scheduler/leases"
    lease_mgr = LeaseManager(lease_dir)
    active_leases = lease_mgr._get_active_leases()
    if task_id in active_leases:
        return TaskClaim(
            claim_id=new_id("cl"),
            task_id=task_id,
            session_id=session,
            lease_id="",
        )

    lease_result = lease_mgr.create_lease(task_id, session)
    claim = TaskClaim(
        claim_id=lease_result.get("claim_id", new_id("cl")),
        task_id=task_id,
        session_id=session,
        lease_id=lease_result.get("lease_id", ""),
        expires_at=lease_result.get("expires_at", utc_now_iso()),
    )

    event = SchedulerEvent(
        event_id=new_id("evt"),
        event_type=SCHEDULER_EVENT_CLAIMED,
        task_id=task_id,
        session_id=session,
        claim_id=claim.claim_id,
        lease_id=claim.lease_id,
        details={"claim_status": "ACTIVE"},
    )
    from .scheduler_evidence import SchedulerEvidenceWriter
    evidence_dir = Path(repo_root) / ".agentx-init/scheduler"
    writer = SchedulerEvidenceWriter(evidence_dir)
    writer._write_json(evidence_dir / "scheduler_event.jsonl", to_dict(event))

    return claim


def evaluate_dependencies(task_id: str, repo_root: str | Path) -> list[DependencyResolution]:
    store = _queue_store(repo_root)
    tasks, quarantined = store.replay_tasks()
    effective = {}
    for t in sorted(tasks, key=lambda x: (x.append_sequence, x.updated_at or "", x.record_id)):
        effective[t.task_id] = t

    task = effective.get(task_id)
    if task is None:
        return []

    resolutions = []
    for dep_id in task.dependency_ids:
        dep_task = effective.get(dep_id)
        satisfied = dep_task is not None and dep_task.status == SCHEDULER_STATUS_COMPLETED
        resolution = DependencyResolution(
            dependency_id=new_id("dep"),
            task_id=task_id,
            depends_on_task_id=dep_id,
            satisfied=satisfied,
            satisfied_at=utc_now_iso() if satisfied else None,
            details={
                "dep_status": dep_task.status if dep_task else "not_found",
            },
        )
        resolutions.append(resolution)
    return resolutions
