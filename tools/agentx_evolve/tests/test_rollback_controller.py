from agentx_evolve.rollback.rollback_controller import MvpRollbackController


class TestMvpRollbackController:
    def setup_method(self):
        self.controller = MvpRollbackController()

    def test_record_rollback(self):
        result = self.controller.record_rollback("act-1", "run-1", "rb-1")
        assert result.status == "recorded"
        assert result.action_id == "act-1"

    def test_rollback_has_evidence(self):
        result = self.controller.record_rollback("act-1", "run-1", "rb-1",
                                                  original_failure="invariant violation")
        assert len(result.evidence) > 0
        assert result.original_failure == "invariant violation"

    def test_finalize_rollback(self):
        self.controller.record_rollback("act-1", "run-1", "rb-1")
        finalized = self.controller.finalize("rb-1", "completed",
                                              [{"event": "cleanup_done"}])
        assert finalized is not None
        assert finalized.status == "completed"
        assert len(finalized.evidence) == 2

    def test_history(self):
        self.controller.record_rollback("act-1", "run-1", "rb-1")
        self.controller.record_rollback("act-2", "run-1", "rb-2")
        assert len(self.controller.history) == 2
