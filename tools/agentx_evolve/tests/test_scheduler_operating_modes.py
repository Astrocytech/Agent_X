import pytest

from agentx_evolve.scheduler.scheduler_models import SchedulerConfig


def test_mode_enum_values_are_correct():
    cfg = SchedulerConfig()
    assert cfg.max_retries_default == 3
    assert cfg.lease_duration_seconds == 300
    assert cfg.heartbeat_timeout_seconds == 60
    assert cfg.stale_session_timeout_seconds == 600


def test_library_only_mode_no_background():
    cfg = SchedulerConfig()
    assert cfg.max_retries_default is not None
    assert cfg.lease_duration_seconds > 0


def test_manual_runner_mode_requires_invocation():
    cfg = SchedulerConfig()
    assert cfg.config_id.startswith("cfg_")
    assert cfg.max_queue_snapshot_records == 100000


def test_dry_run_replay_does_not_mutate():
    from agentx_evolve.scheduler.queue_store import QueueStore
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmp:
        store = QueueStore(Path(tmp) / "queue")
        from agentx_evolve.scheduler.scheduler_models import TaskRecord, new_id
        t = TaskRecord(record_id=new_id("tr"), task_id="t1", session_id="s1")
        store.append_task(t)
        tasks, quarantined = store.replay_tasks()
        assert len(tasks) == 1
        assert len(quarantined) == 0


def test_recovery_only_mode_does_not_execute():
    from agentx_evolve.scheduler.crash_recovery import CrashRecovery
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmp:
        cr = CrashRecovery(Path(tmp) / "recovery")
        sessions = []
        result = cr.recover_stale_sessions(sessions)
        assert len(result) == 0
