import pytest
from agentx_evolve.recovery.recovery_playbook import (
    RA_RETRY, RA_ROLLBACK, is_idempotent,
)
from agentx_evolve.recovery.failure_models import RecoveryAction


class TestIdempotencyConstants:
    def test_ra_retry_value(self):
        assert RA_RETRY == "RETRY"

    def test_ra_rollback_value(self):
        assert RA_ROLLBACK == "ROLLBACK"


class TestIsIdempotent:
    def test_retry_is_idempotent(self):
        assert is_idempotent(RA_RETRY) is True

    def test_rollback_is_idempotent(self):
        assert is_idempotent(RA_ROLLBACK) is True

    def test_destructive_action_not_idempotent(self):
        assert is_idempotent("BLOCK_SESSION") is False
        assert is_idempotent("ENTER_SAFE_MODE") is False

    def test_no_action_is_idempotent(self):
        assert is_idempotent("NO_ACTION") is True


class TestRecoveryAction:
    def test_retry_action_defaults(self):
        action = RecoveryAction(action_type=RA_RETRY)
        assert action.action_type == RA_RETRY
        assert action.action_status == "PROPOSED"

    def test_rollback_action_defaults(self):
        action = RecoveryAction(action_type=RA_ROLLBACK)
        assert action.action_type == RA_ROLLBACK
        assert action.max_attempts == 1
