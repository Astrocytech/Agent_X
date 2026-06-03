import pytest

from agentx_evolve.backup.backup_models import (
    RESTORE_MODE_DRY_RUN,
    RestorePlan,
    RestoreTransactionRecord,
)
from agentx_evolve.backup.restore_transaction import (
    _orig_complete_restore_transaction as complete_restore_transaction,
    _orig_record_restore_transaction_step as record_restore_transaction_step,
    _orig_start_restore_transaction as start_restore_transaction,
)


class TestRestoreTransaction:
    def test_start_creates_transaction(self):
        plan = RestorePlan(
            restore_plan_id="plan1", restore_request_id="req1",
            backup_id="b1", created_at="2025-01-01T00:00:00.000000Z",
            restore_mode=RESTORE_MODE_DRY_RUN,
        )
        tx = start_restore_transaction(plan)
        assert tx.transaction_id.startswith("tx_")
        assert tx.status == "STARTED"
        assert tx.restore_plan_id == "plan1"

    def test_record_step_adds_paths(self):
        plan = RestorePlan(
            restore_plan_id="plan1", restore_request_id="req1",
            backup_id="b1", created_at="2025-01-01T00:00:00.000000Z",
            restore_mode=RESTORE_MODE_DRY_RUN,
        )
        tx = start_restore_transaction(plan)
        tx = record_restore_transaction_step(tx, "copy", restored_path="/tmp/f1.txt")
        assert "/tmp/f1.txt" in tx.restored_paths
        tx = record_restore_transaction_step(tx, "skip", skipped_path="/tmp/f2.txt")
        assert "/tmp/f2.txt" in tx.skipped_paths
        tx = record_restore_transaction_step(tx, "touch", touched_path="/tmp/f3.txt")
        assert "/tmp/f3.txt" in tx.touched_paths

    def test_record_step_with_errors(self):
        plan = RestorePlan(
            restore_plan_id="plan1", restore_request_id="req1",
            backup_id="b1", created_at="2025-01-01T00:00:00.000000Z",
            restore_mode=RESTORE_MODE_DRY_RUN,
        )
        tx = start_restore_transaction(plan)
        tx = record_restore_transaction_step(tx, "fail", errors=["disk full"])
        assert tx.status == "FAILED"
        assert "disk full" in tx.errors

    def test_complete_transaction(self):
        plan = RestorePlan(
            restore_plan_id="plan1", restore_request_id="req1",
            backup_id="b1", created_at="2025-01-01T00:00:00.000000Z",
            restore_mode=RESTORE_MODE_DRY_RUN,
        )
        tx = start_restore_transaction(plan)
        tx = complete_restore_transaction(tx, status="COMPLETED", rollback_notes=["All good"])
        assert tx.status == "COMPLETED"
        assert tx.completed_at is not None
        assert tx.rollback_available is True
