import tempfile

from agentx_evolve.state.state_store import MvpStateStore


class TestMvpStateStore:
    def setup_method(self):
        self._tmp = tempfile.mkdtemp(prefix="test_state_")
        self.store = MvpStateStore(self._tmp)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_create_and_query_by_run(self):
        self.store.create_record("goal", "goal-1", "run-1", {"text": "test"})
        records = self.store.query_by_run("run-1")
        assert len(records) == 1
        assert records[0]["record_id"] == "goal-1"

    def test_query_by_unknown_run_returns_empty(self):
        records = self.store.query_by_run("nonexistent")
        assert records == []

    def test_update_through_transition(self):
        self.store.create_record("action", "act-1", "run-1", {"status": "DRAFT"})
        ok = self.store.update_through_transition("run-1", "act-1", {"status": "PROPOSED"})
        assert ok
        records = self.store.query_by_run("run-1")
        assert records[0]["data"]["status"] == "PROPOSED"

    def test_snapshot_and_restore(self):
        self.store.create_record("goal", "g1", "run-1", {"text": "hello"})
        snap = self.store.snapshot("run-1")
        assert snap is not None
        assert snap["record_count"] == 1

        import shutil
        shutil.rmtree(self._tmp)
        self.store = MvpStateStore(self._tmp)
        ok = self.store.restore(snap)
        assert ok
        records = self.store.query_by_run("run-1")
        assert len(records) == 1

    def test_validate_integrity(self):
        self.store.create_record("goal", "g1", "run-1", {"text": "test"})
        issues = self.store.validate_integrity("run-1")
        assert len(issues) == 0

    def test_validate_integrity_empty(self):
        issues = self.store.validate_integrity("no-run")
        assert len(issues) > 0
