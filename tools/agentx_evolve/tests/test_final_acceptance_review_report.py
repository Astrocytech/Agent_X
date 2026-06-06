from pathlib import Path

from tools.agentx_evolve.final_acceptance.review_report import (
    build_review_report, write_review_report,
)
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceDeviation,
    VERDICT_ACCEPTED, VERDICT_NOT_ACCEPTED,
)
from tools.agentx_evolve.final_acceptance.artifact_writer import runtime_root


class TestBuildReviewReport:
    def test_minimal(self):
        report = build_review_report(
            repo_root=Path("/tmp"),
            reviewed_commit=None,
            reviewed_branch=None,
            acceptance_mode="TEST",
            bootstrap_self=False,
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            blockers=[],
            high_issues=[],
            non_blocking_followups=[],
            deviations=[],
            commands_run=[],
            layer_statuses={},
            git_status_start="",
            git_status_end="",
        )
        assert report["schema_version"] == "1.0"
        assert report["final_verdict"] == VERDICT_ACCEPTED
        assert report["working_tree_start_status"] == "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY"

    def test_with_git_changes(self):
        report = build_review_report(
            repo_root=Path("/tmp"),
            reviewed_commit="abc123",
            reviewed_branch="feature/test",
            acceptance_mode="PRODUCTION_ACCEPTANCE",
            bootstrap_self=True,
            final_verdict=VERDICT_NOT_ACCEPTED,
            implementation_rating=0.5,
            blockers=["Blocker 1"],
            high_issues=["High 1"],
            non_blocking_followups=["Note 1"],
            deviations=[],
            commands_run=[{"command_name": "test", "status": "FAIL"}],
            layer_statuses={"L1": "FAIL"},
            git_status_start=" M modified.py",
            git_status_end="",
        )
        assert report["working_tree_start_status"] == "HAS_CHANGES"
        assert report["working_tree_end_status"] == "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY"
        assert report["blockers"] == ["Blocker 1"]
        assert report["high_issues"] == ["High 1"]
        assert report["non_blocking_followups"] == ["Note 1"]

    def test_with_deviations(self):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D001", area="security", description="Deviation desc",
                reason="Acceptable risk", accepted_status="ACCEPTED",
            ),
        ]
        report = build_review_report(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST", bootstrap_self=False,
            final_verdict=VERDICT_ACCEPTED, implementation_rating=1.0,
            blockers=[], high_issues=[], non_blocking_followups=[],
            deviations=devs,
            commands_run=[], layer_statuses={},
            git_status_start="", git_status_end="",
        )
        assert len(report["deviation_register"]) == 1
        assert report["deviation_register"][0]["deviation_id"] == "D001"
        assert report["deviation_register"][0]["area"] == "security"

    def test_empty_deviations(self):
        report = build_review_report(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST", bootstrap_self=False,
            final_verdict=VERDICT_ACCEPTED, implementation_rating=1.0,
            blockers=[], high_issues=[], non_blocking_followups=[],
            deviations=[],
            commands_run=[], layer_statuses={},
            git_status_start="", git_status_end="",
        )
        assert report["deviation_register"] == []

    def test_commands_run(self):
        report = build_review_report(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST", bootstrap_self=False,
            final_verdict=VERDICT_ACCEPTED, implementation_rating=1.0,
            blockers=[], high_issues=[], non_blocking_followups=[],
            deviations=[],
            commands_run=[{"command_name": "pytest", "status": "PASS"}],
            layer_statuses={},
            git_status_start="", git_status_end="",
        )
        assert report["commands_run"] == [{"command_name": "pytest", "status": "PASS"}]

    def test_release_ready_status(self):
        report = build_review_report(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST", bootstrap_self=False,
            final_verdict=VERDICT_ACCEPTED, implementation_rating=1.0,
            blockers=[], high_issues=[], non_blocking_followups=[],
            deviations=[], commands_run=[], layer_statuses={},
            git_status_start="", git_status_end="",
            release_ready_status="RELEASE_READY",
        )
        assert report["release_ready_status"] == "RELEASE_READY"

    def test_acceptance_scope_id(self):
        report = build_review_report(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST", bootstrap_self=False,
            final_verdict=VERDICT_ACCEPTED, implementation_rating=1.0,
            blockers=[], high_issues=[], non_blocking_followups=[],
            deviations=[], commands_run=[], layer_statuses={},
            git_status_start="", git_status_end="",
            acceptance_scope_id="SCOPE-001",
        )
        assert report["acceptance_scope_id"] == "SCOPE-001"


class TestWriteReviewReport:
    def test_writes_file(self, tmp_path: Path):
        report = build_review_report(
            repo_root=tmp_path,
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST", bootstrap_self=False,
            final_verdict=VERDICT_ACCEPTED, implementation_rating=1.0,
            blockers=[], high_issues=[], non_blocking_followups=[],
            deviations=[], commands_run=[], layer_statuses={},
            git_status_start="", git_status_end="",
        )
        path = write_review_report(report, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_review_report.json"

    def test_written_to_runtime_root(self, tmp_path: Path):
        report = build_review_report(
            repo_root=tmp_path,
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST", bootstrap_self=False,
            final_verdict=VERDICT_ACCEPTED, implementation_rating=1.0,
            blockers=[], high_issues=[], non_blocking_followups=[],
            deviations=[], commands_run=[], layer_statuses={},
            git_status_start="", git_status_end="",
        )
        path = write_review_report(report, tmp_path)
        assert runtime_root(tmp_path) in path.parents
