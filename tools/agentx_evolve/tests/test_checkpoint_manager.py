from agentx_evolve.checkpoints.checkpoint_manager import MvpCheckpointManager


class TestMvpCheckpointManager:
    def setup_method(self):
        self.manager = MvpCheckpointManager()

    def test_create_checkpoint(self):
        cp = self.manager.create_checkpoint("run-1", {"step": 1, "data": "hello"})
        assert cp.checkpoint_id
        assert cp.run_id == "run-1"
        assert cp.state_snapshot == {"step": 1, "data": "hello"}
        assert cp.created_at
        assert cp.hash

    def test_restore_checkpoint(self):
        self.manager.create_checkpoint("run-1", {"step": 1})
        cps = self.manager.list_for_run("run-1")
        snapshot = self.manager.restore(cps[0].checkpoint_id)
        assert snapshot == {"step": 1}

    def test_list_for_run(self):
        self.manager.create_checkpoint("run-1", {"step": 1})
        self.manager.create_checkpoint("run-1", {"step": 2})
        self.manager.create_checkpoint("run-2", {"step": 1})
        run1 = self.manager.list_for_run("run-1")
        assert len(run1) == 2
        run2 = self.manager.list_for_run("run-2")
        assert len(run2) == 1

    def test_get_latest(self):
        self.manager.create_checkpoint("run-1", {"step": 1}, description="first")
        self.manager.create_checkpoint("run-1", {"step": 2}, description="second")
        latest = self.manager.get_latest("run-1")
        assert latest is not None
        assert latest.description == "second"
        assert latest.state_snapshot == {"step": 2}

    def test_validate_checkpoint(self):
        cp = self.manager.create_checkpoint("run-1", {"step": 1})
        assert self.manager.validate(cp.checkpoint_id) is True
        self.manager._checkpoints[cp.checkpoint_id].state_snapshot = {"step": 99}
        assert self.manager.validate(cp.checkpoint_id) is False

    def test_branch_from_checkpoint(self):
        original = self.manager.create_checkpoint("run-1", {"step": 1, "data": "x"})
        branch = self.manager.branch(original.checkpoint_id, "run-2")
        assert branch is not None
        assert branch.run_id == "run-2"
        assert branch.parent_id == original.checkpoint_id
        assert branch.state_snapshot == {"step": 1, "data": "x"}
        assert self.manager.list_for_run("run-2") == [branch]

    def test_nonexistent_checkpoint_returns_none(self):
        assert self.manager.restore("fake-id") is None
        assert self.manager.validate("fake-id") is False
        assert self.manager.branch("fake-id", "run-2") is None
        assert self.manager.get_latest("nonexistent-run") is None
