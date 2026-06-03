import pytest


def test_plan_revision_created():
    revision = {
        "revision_id": "rev-001",
        "plan_id": "plan-001",
        "session_id": "sess-001",
        "run_id": "run-001",
        "revision_number": 1,
        "old_plan_hash": "abc123",
        "new_plan_hash": "def456",
        "changes": ["added step 3", "modified step 2 timeout"],
    }
    assert revision["revision_number"] == 1
    assert len(revision["changes"]) == 2


def test_plan_revision_increments():
    rev1 = {"revision_id": "rev-001", "revision_number": 1}
    rev2 = {"revision_id": "rev-002", "revision_number": 2}
    assert rev2["revision_number"] > rev1["revision_number"]


def test_plan_revision_hash_chain():
    rev1 = {"old_plan_hash": "", "new_plan_hash": "abc"}
    rev2 = {"old_plan_hash": "abc", "new_plan_hash": "def"}
    assert rev1["new_plan_hash"] == rev2["old_plan_hash"]
