import pathlib

from agentx_evolve.runtime.config import ConfigResolver
from agentx_evolve.runtime.results import EXIT_PASS, EXIT_BLOCKED
from agentx_evolve.workflows.self_upgrade import SelfUpgradeWorkflow


class TestSelfUpgradeWorkflow:
    def test_plan_mock(self, tmp_path):
        concept = tmp_path / "concept.md"
        concept.write_text("## Test change\n\nAdd a comment to config.py")
        config = ConfigResolver().resolve([
            "--concept-file", str(concept),
            "--mode", "plan",
            "--dry-run", "--mock",
        ])
        config.run_root = str(tmp_path / "runs")
        workflow = SelfUpgradeWorkflow(config)
        result = workflow.run()

        assert result.status == "PASS"
        assert result.exit_code == EXIT_PASS
        assert "plan" in result.message

    def test_apply_dry_run_mock(self, tmp_path):
        concept = tmp_path / "concept.md"
        concept.write_text("## Test apply\n\nRefactor README")
        config = ConfigResolver().resolve([
            "--concept-file", str(concept),
            "--mode", "apply",
            "--dry-run", "--mock",
        ])
        config.run_root = str(tmp_path / "runs2")
        workflow = SelfUpgradeWorkflow(config)
        result = workflow.run()

        assert result.status in ("PASS", "FAIL")
        assert isinstance(result.message, str)
        run_dir = pathlib.Path(result.run_dir)
        assert (run_dir / "applied_patch.diff").exists()

    def test_missing_concept_file_blocks(self, tmp_path):
        config = ConfigResolver().resolve(["--mock"])
        config.run_root = str(tmp_path / "runs3")
        workflow = SelfUpgradeWorkflow(config)
        result = workflow.run()

        assert result.status == "BLOCKED"
        assert result.exit_code == EXIT_BLOCKED
        assert "missing" in result.message.lower()

    def test_nonexistent_concept_file_blocks(self, tmp_path):
        config = ConfigResolver().resolve([
            "--concept-file", "/nonexistent/path.md",
            "--mock",
        ])
        config.run_root = str(tmp_path / "runs4")
        workflow = SelfUpgradeWorkflow(config)
        result = workflow.run()

        assert result.status == "BLOCKED"
        assert "not found" in result.message.lower()

    def test_artifacts_written(self, tmp_path):
        concept = tmp_path / "concept.md"
        concept.write_text("## Test\n\nAdd logging")
        config = ConfigResolver().resolve([
            "--concept-file", str(concept),
            "--mode", "plan", "--dry-run", "--mock",
        ])
        config.run_root = str(tmp_path / "runs5")
        workflow = SelfUpgradeWorkflow(config)
        result = workflow.run()

        run_dir = pathlib.Path(result.run_dir)
        required = [
            "run_metadata.json", "resolved_config.json", "preflight.json",
            "request.json",
            "packed_context.json", "model_messages.jsonl", "model_response.json",
            "structured_plan.json", "proposed_patch.diff",
            "validation_report.json", "evidence_manifest.json",
            "final_verdict.json", "implementation_ledger.json",
        ]
        for name in required:
            assert (run_dir / name).exists(), f"missing {name}"
