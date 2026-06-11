from agentx_evolve.review.review_interface import MvpReviewInterface, MvpReviewPacket, RCT_APPROVED, RCT_REJECTED


class TestMvpReviewInterface:
    def setup_method(self):
        self.ri = MvpReviewInterface()

    def test_create_packet(self):
        p = MvpReviewPacket(review_id="rev-1", action_id="act-1", run_id="run-1",
                            created_at="now")
        self.ri.create_packet(p)
        assert self.ri.get_packet("rev-1") is not None

    def test_record_approval_decision(self):
        p = MvpReviewPacket(review_id="rev-2", action_id="act-1", run_id="run-1",
                            created_at="now")
        self.ri.create_packet(p)
        result = self.ri.record_decision("rev-2", RCT_APPROVED, "Looks good",
                                          "reviewer-1", "later")
        assert result is not None
        assert result.decision == RCT_APPROVED
        assert result.reviewer_identity == "reviewer-1"

    def test_record_rejection(self):
        p = MvpReviewPacket(review_id="rev-3", action_id="act-1", run_id="run-1",
                            created_at="now")
        self.ri.create_packet(p)
        result = self.ri.record_decision("rev-3", RCT_REJECTED, "Not good",
                                          "reviewer-1", "later")
        assert result.decision == RCT_REJECTED

    def test_is_finalized(self):
        p = MvpReviewPacket(review_id="rev-4", action_id="act-1", run_id="run-1",
                            created_at="now")
        self.ri.create_packet(p)
        assert not self.ri.is_finalized("rev-4")
        self.ri.record_decision("rev-4", RCT_APPROVED, "ok", "r1", "now")
        assert self.ri.is_finalized("rev-4")

    def test_list_by_run(self):
        self.ri.create_packet(MvpReviewPacket(review_id="r1", run_id="run-1"))
        self.ri.create_packet(MvpReviewPacket(review_id="r2", run_id="run-1"))
        self.ri.create_packet(MvpReviewPacket(review_id="r3", run_id="run-2"))
        assert len(self.ri.list_by_run("run-1")) == 2
