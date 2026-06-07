import pathlib

from agentx_evolve.runtime.config import ConfigResolver
from agentx_evolve.runtime.results import EXIT_PASS, EXIT_BLOCKED
from agentx_evolve.workflows.init_agent import InitAgentWorkflow


class TestInitAgentWorkflow:
    def test_init_agent(self, tmp_path):
        dest = tmp_path / "Agent_Test"
        config = ConfigResolver().resolve([
            "--name", "Agent_Test",
            "--dest", str(dest),
            "--mock",
        ])
        config.run_root = str(tmp_path / "runs")
        workflow = InitAgentWorkflow(config)
        result = workflow.run()

        assert result.status == "PASS"
        assert result.exit_code == EXIT_PASS
        assert dest.exists()
        assert "Agent_Test" in result.message

    def test_missing_name_blocks(self, tmp_path):
        config = ConfigResolver().resolve(["--dest", str(tmp_path / "x")])
        config.run_root = str(tmp_path / "runs2")
        workflow = InitAgentWorkflow(config)
        result = workflow.run()

        assert result.status == "BLOCKED"
        assert result.exit_code == EXIT_BLOCKED
        assert "missing --name" in result.message.lower() or "name" in result.message.lower()

    def test_missing_dest_blocks(self, tmp_path):
        config = ConfigResolver().resolve(["--name", "Test"])
        config.run_root = str(tmp_path / "runs3")
        workflow = InitAgentWorkflow(config)
        result = workflow.run()

        assert result.status == "BLOCKED"
        assert "missing --dest" in result.message.lower() or "dest" in result.message.lower()

    def test_nonempty_dest_blocks(self, tmp_path):
        dest = tmp_path / "existing"
        dest.mkdir()
        (dest / "some_file.txt").write_text("hello")

        config = ConfigResolver().resolve([
            "--name", "Agent_Test",
            "--dest", str(dest),
            "--mock",
        ])
        config.run_root = str(tmp_path / "runs4")
        workflow = InitAgentWorkflow(config)
        result = workflow.run()

        assert result.status == "BLOCKED"
        assert "not empty" in result.message.lower()

    def test_copies_seed_files(self, tmp_path):
        dest = tmp_path / "Agent_Seeded"
        config = ConfigResolver().resolve([
            "--name", "Agent_Seeded",
            "--dest", str(dest),
            "--mock",
        ])
        config.run_root = str(tmp_path / "runs5")
        workflow = InitAgentWorkflow(config)
        result = workflow.run()

        assert result.status == "PASS"
        assert dest.exists()

        l0_dir = dest / "L0"
        assert l0_dir.exists(), "L0 directory should be copied"

    def test_artifacts_written(self, tmp_path):
        dest = tmp_path / "Agent_Artifacts"
        config = ConfigResolver().resolve([
            "--name", "Agent_Artifacts",
            "--dest", str(dest),
            "--mock",
        ])
        config.run_root = str(tmp_path / "runs6")
        workflow = InitAgentWorkflow(config)
        result = workflow.run()

        run_dir = pathlib.Path(result.run_dir)
        for name in ["run_metadata.json", "resolved_config.json", "preflight.json",
                      "packed_context.json", "validation_report.json",
                      "evidence_manifest.json", "final_verdict.json",
                      "implementation_ledger.json"]:
            assert (run_dir / name).exists(), f"missing {name}"
