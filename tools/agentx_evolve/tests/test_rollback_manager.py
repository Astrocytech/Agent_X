from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession,
    RollbackSnapshot,
    new_id,
    utc_now_iso,
)
from agentx_evolve.patch_execution.rollback_manager import (
    create_rollback_snapshot,
    rollback_session,
    verify_rollback,
)


class TestCreateRollbackSnapshot:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )
        self.src_dir = self.repo_root / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_snapshot_existing_file(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("print('hello')")
        result = create_rollback_snapshot(
            self.session, self.repo_root, ["src/main.py"]
        )
        assert result.status == "CREATED"
        assert len(result.files) == 1
        assert result.files[0]["existed_before"] is True
        assert result.files[0]["before_hash"] is not None
        assert result.session_id == self.session.session_id

    def test_snapshot_nonexistent_file(self) -> None:
        result = create_rollback_snapshot(
            self.session, self.repo_root, ["src/nonexistent.py"]
        )
        assert result.status == "CREATED"
        assert result.files[0]["existed_before"] is False
        assert result.files[0]["before_hash"] is None

    def test_snapshot_root_created_on_disk(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("content")
        result = create_rollback_snapshot(
            self.session, self.repo_root, ["src/main.py"]
        )
        snap_root = Path(result.snapshot_root)
        assert snap_root.exists()
        assert (snap_root / "src/main.py").exists()

    def test_snapshot_multiple_files(self) -> None:
        (self.src_dir / "a.py").write_text("a")
        (self.src_dir / "b.py").write_text("b")
        result = create_rollback_snapshot(
            self.session, self.repo_root, ["src/a.py", "src/b.py"]
        )
        assert len(result.files) == 2

    def test_empty_target_paths(self) -> None:
        result = create_rollback_snapshot(self.session, self.repo_root, [])
        assert result.status == "CREATED"
        assert len(result.files) == 0

    def test_snapshot_id_starts_with_snap(self) -> None:
        result = create_rollback_snapshot(
            self.session, self.repo_root, ["src/main.py"]
        )
        assert result.snapshot_id.startswith("SNAP")


class TestRollbackSession:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )
        self.src_dir = self.repo_root / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.main_py = self.src_dir / "main.py"
        self.main_py.write_text("original content")
        self.snapshot = create_rollback_snapshot(
            self.session, self.repo_root, ["src/main.py"]
        )

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_rollback_restores_original_content(self) -> None:
        self.main_py.write_text("modified content")
        record = rollback_session(
            self.session, self.snapshot, self.repo_root, trigger="TEST"
        )
        assert self.main_py.read_text() == "original content"
        assert "src/main.py" in record.restored_files

    def test_rollback_removes_created_files(self) -> None:
        (self.src_dir / "new.py").write_text("new file")
        record = rollback_session(
            self.session,
            self.snapshot,
            self.repo_root,
            trigger="TEST",
            created_paths=["src/new.py"],
        )
        assert not (self.src_dir / "new.py").exists()
        assert "src/new.py" in record.removed_created_files

    def test_rollback_record_has_correct_ids(self) -> None:
        record = rollback_session(
            self.session, self.snapshot, self.repo_root, trigger="VALIDATION_FAILED"
        )
        assert record.session_id == self.session.session_id
        assert record.snapshot_id == self.snapshot.snapshot_id
        assert record.trigger == "VALIDATION_FAILED"

    def test_rollback_record_status_rolled_back(self) -> None:
        record = rollback_session(
            self.session, self.snapshot, self.repo_root, trigger="TEST"
        )
        assert record.status == "ROLLED_BACK"


class TestVerifyRollback:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())
        self.session = ImplementationSession(
            session_id=new_id("IMP"),
            target_paths=["src/main.py"],
            timestamp=utc_now_iso(),
        )
        self.src_dir = self.repo_root / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_verify_after_rollback_returns_verified(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("original")
        snap = create_rollback_snapshot(
            self.session, self.repo_root, ["src/main.py"]
        )
        main_py.write_text("modified")
        rollback_session(self.session, snap, self.repo_root, trigger="TEST")
        result = verify_rollback(snap, self.repo_root)
        assert result["status"] == "VERIFIED"

    def test_verify_fails_if_not_restored(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("original")
        snap = create_rollback_snapshot(
            self.session, self.repo_root, ["src/main.py"]
        )
        main_py.write_text("still modified")
        result = verify_rollback(snap, self.repo_root)
        assert result["status"] == "FAILED"
        assert result["mismatch_count"] >= 1

    def test_verify_nonexistent_file_after_snapshot(self) -> None:
        snap = create_rollback_snapshot(
            self.session, self.repo_root, ["src/nope.py"]
        )
        result = verify_rollback(snap, self.repo_root)
        assert result["status"] == "VERIFIED"

    def test_verify_detects_created_file_still_present(self) -> None:
        main_py = self.src_dir / "main.py"
        main_py.write_text("original")
        snap = create_rollback_snapshot(
            self.session, self.repo_root, ["src/main.py"]
        )
        rollback_session(self.session, snap, self.repo_root, trigger="TEST")
        (self.src_dir / "leftover.py").write_text("oops")
        result = verify_rollback(snap, self.repo_root, created_paths=["src/leftover.py"])
        assert result["status"] == "FAILED"
