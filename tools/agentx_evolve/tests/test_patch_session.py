from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from agentx_evolve.patch_execution.patch_session import (
    create_implementation_session,
    update_implementation_session,
)
from agentx_evolve.patch_execution.patch_models import ImplementationSession


class TestCreateImplementationSession:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_creates_session_with_defaults(self) -> None:
        session = create_implementation_session(
            repo_root=self.repo_root,
            target_paths=["src/main.py"],
        )
        assert session.session_id.startswith("IMP")
        assert session.target_paths == ["src/main.py"]
        assert session.status == "SESSION_INITIALIZED"
        assert session.lifecycle_state == "PENDING_INIT"
        assert session.timestamp != ""

    def test_creates_session_with_all_params(self) -> None:
        session = create_implementation_session(
            repo_root=self.repo_root,
            target_paths=["src/main.py", "src/utils.py"],
            proposal_id="prop_1",
            governance_decision_id="gov_1",
            policy_decision_id="pol_1",
        )
        assert session.proposal_id == "prop_1"
        assert session.governance_decision_id == "gov_1"
        assert session.policy_decision_id == "pol_1"

    def test_raises_value_error_for_empty_target_paths(self) -> None:
        try:
            create_implementation_session(
                repo_root=self.repo_root,
                target_paths=[],
            )
            assert False, "should have raised ValueError"
        except ValueError:
            pass

    def test_writes_session_file_to_disk(self) -> None:
        session = create_implementation_session(
            repo_root=self.repo_root,
            target_paths=["src/main.py"],
        )
        session_path = (
            self.repo_root
            / ".agentx-init/implementation/sessions"
            / f"{session.session_id}.json"
        )
        assert session_path.exists()
        data = json.loads(session_path.read_text(encoding="utf-8"))
        assert data["session_id"] == session.session_id

    def test_writes_latest_session_file(self) -> None:
        session = create_implementation_session(
            repo_root=self.repo_root,
            target_paths=["src/main.py"],
        )
        latest_path = (
            self.repo_root / ".agentx-init/implementation/latest_implementation_session.json"
        )
        assert latest_path.exists()
        data = json.loads(latest_path.read_text(encoding="utf-8"))
        assert data["data"]["session_id"] == session.session_id

    def test_appends_history_jsonl(self) -> None:
        create_implementation_session(
            repo_root=self.repo_root,
            target_paths=["src/main.py"],
        )
        history_path = (
            self.repo_root / ".agentx-init/implementation/implementation_history.jsonl"
        )
        assert history_path.exists()
        lines = history_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) >= 1


class TestUpdateImplementationSession:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())
        self.session = create_implementation_session(
            repo_root=self.repo_root,
            target_paths=["src/main.py"],
        )

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_updates_status_and_lifecycle_state(self) -> None:
        updated = update_implementation_session(
            session=self.session,
            repo_root=self.repo_root,
            status="DRY_RUNNING",
        )
        assert updated.status == "DRY_RUNNING"
        assert updated.lifecycle_state == "DRY_RUN"

    def test_sets_lifecycle_to_unknown_for_unmapped_status(self) -> None:
        updated = update_implementation_session(
            session=self.session,
            repo_root=self.repo_root,
            status="NONEXISTENT_STATUS",
        )
        assert updated.lifecycle_state == "UNKNOWN"

    def test_updates_timestamp(self) -> None:
        old_ts = self.session.timestamp
        updated = update_implementation_session(
            session=self.session,
            repo_root=self.repo_root,
            status="ACCEPTED",
        )
        assert updated.timestamp != ""
        assert updated.timestamp != old_ts or old_ts == ""

    def test_updates_final_decision(self) -> None:
        updated = update_implementation_session(
            session=self.session,
            repo_root=self.repo_root,
            status="FINALIZED",
            final_decision="ACCEPT",
        )
        assert updated.final_decision == "ACCEPT"

    def test_updates_tracker_fields(self) -> None:
        updated = update_implementation_session(
            session=self.session,
            repo_root=self.repo_root,
            status="PATCH_APPLIED",
            rollback_snapshot_id="rs_1",
            patch_application_id="pa_1",
            source_change_guard_id="scg_1",
            validation_result_id="vr_1",
            rollback_record_id="rr_1",
        )
        assert updated.rollback_snapshot_id == "rs_1"
        assert updated.patch_application_id == "pa_1"
        assert updated.source_change_guard_id == "scg_1"
        assert updated.validation_result_id == "vr_1"
        assert updated.rollback_record_id == "rr_1"

    def test_updates_changed_paths(self) -> None:
        updated = update_implementation_session(
            session=self.session,
            repo_root=self.repo_root,
            status="PATCH_APPLIED",
            changed_paths=["src/main.py", "src/utils.py"],
        )
        assert updated.changed_paths == ["src/main.py", "src/utils.py"]

    def test_updates_warnings_and_errors(self) -> None:
        updated = update_implementation_session(
            session=self.session,
            repo_root=self.repo_root,
            status="FAILED",
            warnings=["something odd"],
            errors=["something wrong"],
        )
        assert updated.warnings == ["something odd"]
        assert updated.errors == ["something wrong"]

    def test_update_rewrites_latest_file(self) -> None:
        update_implementation_session(
            session=self.session,
            repo_root=self.repo_root,
            status="ACCEPTED",
        )
        latest_path = (
            self.repo_root / ".agentx-init/implementation/latest_implementation_session.json"
        )
        data = json.loads(latest_path.read_text(encoding="utf-8"))
        assert data["data"]["status"] == "ACCEPTED"

    def test_update_appends_to_history(self) -> None:
        update_implementation_session(
            session=self.session,
            repo_root=self.repo_root,
            status="ACCEPTED",
        )
        history_path = (
            self.repo_root / ".agentx-init/implementation/implementation_history.jsonl"
        )
        lines = history_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) >= 2
