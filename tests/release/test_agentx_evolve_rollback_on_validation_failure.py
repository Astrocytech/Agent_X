import json, os, sys, tempfile
from pathlib import Path


class TestAgentxEvolveRollbackOnValidationFailure:
    """Test that a patch with invalid content triggers rollback."""

    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_create_rollback_snapshot_and_record(self):
        from agentx_evolve.patch_execution.patch_models import (
            ImplementationSession, RollbackSnapshot, RollbackRecord,
            new_id, utc_now_iso,
        )
        from agentx_evolve.patch_execution.rollback_manager import (
            create_rollback_snapshot, rollback_session,
        )
        from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat

        compat = InitiatorPatchCompat(repo_root=self.tmpdir)

        test_file = self.tmpdir / "test_mutation.py"
        test_file.write_text("original content\n")

        session = ImplementationSession(
            session_id=new_id("session"),
            timestamp=utc_now_iso(),
        )

        snapshot = create_rollback_snapshot(
            session=session,
            repo_root=self.tmpdir,
            target_paths=["test_mutation.py"],
            compat=compat,
        )
        assert snapshot.snapshot_id.startswith("SNAP-")
        assert snapshot.status == "CREATED"
        assert len(snapshot.files) == 1
        assert snapshot.files[0]["path"] == "test_mutation.py"

        test_file.write_text("mutated content\n")

        rollback_record = rollback_session(
            session=session,
            snapshot=snapshot,
            repo_root=self.tmpdir,
            trigger="VALIDATION_FAILED",
            compat=compat,
        )
        assert rollback_record.trigger == "VALIDATION_FAILED"
        assert rollback_record.status == "ROLLED_BACK"
        assert "test_mutation.py" in rollback_record.restored_files

        restored = test_file.read_text()
        assert restored == "original content\n"

    def test_snapshot_dir_exists_after_creation(self):
        from agentx_evolve.patch_execution.patch_models import (
            ImplementationSession, new_id, utc_now_iso,
        )
        from agentx_evolve.patch_execution.rollback_manager import create_rollback_snapshot
        from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat

        compat = InitiatorPatchCompat(repo_root=self.tmpdir)
        (self.tmpdir / "some_file.txt").write_text("data")

        session = ImplementationSession(
            session_id=new_id("session"),
            timestamp=utc_now_iso(),
        )

        snapshot = create_rollback_snapshot(
            session=session,
            repo_root=self.tmpdir,
            target_paths=["some_file.txt"],
            compat=compat,
        )
        snap_dir = self.tmpdir / ".agentx-init" / "implementation" / "rollback_snapshots" / snapshot.snapshot_id
        assert snap_dir.is_dir()
