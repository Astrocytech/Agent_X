import pytest
from agentx_evolve.docs_sync.doc_sync import SyncPolicy, SP_CHECK_DRIFT, SP_ENFORCE_DRIFT


class TestSyncPolicyConstants:
    def test_sp_check_drift_value(self):
        assert SP_CHECK_DRIFT == "CHECK_DRIFT"

    def test_sp_enforce_drift_value(self):
        assert SP_ENFORCE_DRIFT == "ENFORCE_DRIFT"


class TestSyncPolicy:
    def test_defaults_to_check_only(self):
        policy = SyncPolicy()
        assert policy.mode == SP_CHECK_DRIFT
        assert policy.allowed_operations == []
        assert policy.blocked_operations == []

    def test_enforce_mode(self):
        policy = SyncPolicy(mode=SP_ENFORCE_DRIFT)
        assert policy.mode == SP_ENFORCE_DRIFT

    def test_allows_operation(self):
        policy = SyncPolicy(allowed_operations=["generate", "update"])
        assert policy.allows("generate") is True
        assert policy.allows("delete") is False

    def test_blocks_operation(self):
        policy = SyncPolicy(blocked_operations=["delete"])
        assert policy.blocks("delete") is True
        assert policy.blocks("update") is False

    def test_check_only_allows_nothing_by_default(self):
        policy = SyncPolicy(mode=SP_CHECK_DRIFT)
        assert policy.allows("anything") is False
