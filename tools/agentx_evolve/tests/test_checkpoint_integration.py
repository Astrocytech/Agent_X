import os
import tempfile

from agentx_evolve.checkpoints.checkpoint_manager import MvpCheckpointManager


class TestCheckpointPersistence:
    def test_persists_to_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = MvpCheckpointManager(base_path=tmp)
            cp = mgr.create_checkpoint("run-disk", {"step": 1, "data": "hello"})
            json_path = os.path.join(tmp, f"{cp.checkpoint_id}.json")
            assert os.path.isfile(json_path)
            with open(json_path) as f:
                import json
                d = json.load(f)
            assert d["checkpoint_id"] == cp.checkpoint_id
            assert d["run_id"] == "run-disk"

    def test_restores_from_disk_after_cache_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr1 = MvpCheckpointManager(base_path=tmp)
            cp = mgr1.create_checkpoint("run-restore", {"step": 1})
            cp_id = cp.checkpoint_id

            mgr2 = MvpCheckpointManager(base_path=tmp)
            snapshot = mgr2.restore(cp_id)
            assert snapshot == {"step": 1}

    def test_lists_from_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr1 = MvpCheckpointManager(base_path=tmp)
            mgr1.create_checkpoint("run-list", {"step": 1}, description="first")
            mgr1.create_checkpoint("run-list", {"step": 2}, description="second")
            mgr1.create_checkpoint("run-other", {"step": 1})

            mgr2 = MvpCheckpointManager(base_path=tmp)
            run_list = mgr2.list_for_run("run-list")
            assert len(run_list) == 2
            descriptions = {cp.description for cp in run_list}
            assert "first" in descriptions
            assert "second" in descriptions

    def test_validate_across_instances(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr1 = MvpCheckpointManager(base_path=tmp)
            cp = mgr1.create_checkpoint("run-valid", {"step": 1})
            cp_id = cp.checkpoint_id

            mgr2 = MvpCheckpointManager(base_path=tmp)
            assert mgr2.validate(cp_id) is True

    def test_branch_from_disk_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr1 = MvpCheckpointManager(base_path=tmp)
            orig = mgr1.create_checkpoint("run-orig", {"step": 1, "data": "x"})
            cp_id = orig.checkpoint_id

            mgr2 = MvpCheckpointManager(base_path=tmp)
            branch = mgr2.branch(cp_id, "run-branch")
            assert branch is not None
            assert branch.run_id == "run-branch"
            assert branch.state_snapshot == {"step": 1, "data": "x"}
            assert os.path.isfile(os.path.join(tmp, f"{branch.checkpoint_id}.json"))

    def test_flush_persists_all(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = MvpCheckpointManager(base_path=tmp)
            mgr.create_checkpoint("run-a", {"v": 1})
            mgr.create_checkpoint("run-b", {"v": 2})
            mgr.flush()
            files = [f for f in os.listdir(tmp) if f.endswith(".json")]
            assert len(files) == 2
