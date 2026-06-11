from agentx_evolve.lifecycle.action import MvpAction, ACTION_STATES, FORBIDDEN_TRANSITIONS


class TestMvpActionLifecycle:
    def test_happy_path(self):
        action = MvpAction(action_id="act-1")
        assert action.status == "DRAFT"
        action.propose()
        assert action.status == "PROPOSED"
        action.validate()
        assert action.status == "VALIDATED"
        action.simulate()
        assert action.status == "SIMULATED"
        action.approve()
        assert action.status == "APPROVED"
        action.execute()
        assert action.status == "EXECUTED"
        action.observe()
        assert action.status == "OBSERVED"
        action.test()
        assert action.status == "TESTED"
        action.review()
        assert action.status == "REVIEWED"
        action.promote()
        assert action.status == "PROMOTED"
        action.archive()
        assert action.status == "ARCHIVED"

    def test_denial_path_rejected(self):
        action = MvpAction(action_id="act-2")
        action.propose()
        action.validate()
        action.simulate()
        action.approve()
        action.execute()
        action.observe()
        action.test()
        action.review()
        action.reject()
        assert action.status == "REJECTED"
        action.archive()
        assert action.is_terminal()

    def test_forbidden_direct_execute(self):
        action = MvpAction(action_id="act-3")
        try:
            action.execute()
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_forbidden_direct_promote(self):
        action = MvpAction(action_id="act-4")
        action.propose()
        action.validate()
        action.simulate()
        action.approve()
        try:
            action.promote()
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_forbidden_transitions_listed(self):
        assert ("DRAFT", "EXECUTED") in FORBIDDEN_TRANSITIONS
        assert ("PROPOSED", "EXECUTED") in FORBIDDEN_TRANSITIONS

    def test_rollback_path(self):
        action = MvpAction(action_id="act-5")
        action.propose()
        action.validate()
        action.simulate()
        action.approve()
        action.execute()
        action.rollback()
        assert action.status == "ROLLED_BACK"
        action.archive()
        assert action.is_terminal()

    def test_to_dict_roundtrip(self):
        action = MvpAction(action_id="act-6")
        action.propose()
        d = action.to_dict()
        assert d["state"] == "PROPOSED"
        restored = MvpAction.from_dict(d)
        assert restored.status == "PROPOSED"
