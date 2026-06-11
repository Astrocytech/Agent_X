from agentx_evolve.transactions.transaction_manager import MvpTransactionManager


class TestMvpTransactionManager:
    def setup_method(self):
        self.mgr = MvpTransactionManager()

    def test_begin_and_commit(self):
        txn = self.mgr.begin("txn-1", "run-1", "act-1", "now")
        assert txn.status == "open"
        self.mgr.stage({"change": "write_report"})
        committed = self.mgr.commit("later")
        assert committed.status == "committed"
        assert len(committed.evidence) == 1

    def test_begin_and_abort(self):
        self.mgr.begin("txn-2", "run-1", "act-1", "now")
        aborted = self.mgr.abort("later", "something went wrong")
        assert aborted.status == "aborted"
        assert aborted.aborted_at == "later"

    def test_double_begin_fails(self):
        self.mgr.begin("txn-3", "run-1", "act-1", "now")
        try:
            self.mgr.begin("txn-4", "run-1", "act-1", "now")
            assert False, "Should have raised"
        except RuntimeError:
            pass

    def test_commit_without_begin_fails(self):
        try:
            self.mgr.commit("now")
            assert False, "Should have raised"
        except RuntimeError:
            pass

    def test_abort_without_begin_fails(self):
        try:
            self.mgr.abort("now")
            assert False, "Should have raised"
        except RuntimeError:
            pass

    def test_history_by_run(self):
        self.mgr.begin("txn-5", "run-1", "act-1", "now")
        self.mgr.commit("later")
        self.mgr.begin("txn-6", "run-1", "act-2", "now")
        self.mgr.commit("later")
        hist = self.mgr.history_for_run("run-1")
        assert len(hist) == 2
