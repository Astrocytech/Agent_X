import pytest
from agentx_evolve.scheduler.scheduler_models import (
    DependencyResolver, resolve_dependencies,
    TaskRecord, SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_COMPLETED,
)


def test_resolver_handles_no_dependencies():
    resolver = DependencyResolver()
    task = TaskRecord(record_id="r1", task_id="t1", session_id="s1")
    effective = {"t1": task}
    assert resolver.resolve(task, effective) is True


def test_resolver_blocks_on_unmet_deps():
    resolver = DependencyResolver()
    task_a = TaskRecord(record_id="r1", task_id="t1", session_id="s1",
                        dependency_ids=["dep-1"])
    effective = {"t1": task_a}
    assert resolver.resolve(task_a, effective) is False


def test_resolver_passes_on_satisfied_deps():
    resolver = DependencyResolver()
    dep = TaskRecord(record_id="r0", task_id="dep-1", session_id="s1",
                     status=SCHEDULER_STATUS_COMPLETED)
    task = TaskRecord(record_id="r1", task_id="t1", session_id="s1",
                      dependency_ids=["dep-1"])
    effective = {"dep-1": dep, "t1": task}
    assert resolver.resolve(task, effective) is True


def test_resolve_dependencies_function():
    dep = TaskRecord(record_id="r0", task_id="dep-1", session_id="s1",
                     status=SCHEDULER_STATUS_COMPLETED)
    task = TaskRecord(record_id="r1", task_id="t1", session_id="s1",
                      dependency_ids=["dep-1"])
    effective = {"dep-1": dep, "t1": task}
    result = resolve_dependencies([task], effective)
    assert result["t1"] is True


def test_resolve_dependencies_no_deps():
    task = TaskRecord(record_id="r1", task_id="t1", session_id="s1")
    effective = {"t1": task}
    result = resolve_dependencies([task], effective)
    assert result["t1"] is True
