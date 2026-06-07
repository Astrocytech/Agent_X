import pathlib

from agentx_evolve.runtime.config import ConfigResolver
from agentx_evolve.runtime.results import EXIT_PASS, EXIT_BLOCKED
from agentx_evolve.workflows.evolve_agent import EvolveAgentWorkflow


class TestEvolveAgentWorkflow:
    def test_plan_mock(self, tmp_path):
        agent_dir = tmp_path / "target_agent"
        agent_dir.mkdir()
        (agent_dir / "README.md").write_text("# Existing Agent")

        concept = tmp_path / "upgrade.md"
        concept.write_text("## Add config file\n\nCreate agent.cfg")

        config = ConfigResolver().resolve([
            "--agent-dir", str(agent_dir),
            "--concept-file", str(concept),
            "--mode", "plan", "--dry-run", "--mock",
        ])
        config.run_root = str(tmp_path / "runs")
        workflow = EvolveAgentWorkflow(config)
        result = workflow.run()

        assert result.status == "PASS"
        assert result.exit_code == EXIT_PASS
        assert "plan" in result.message.lower()

    def test_missing_agent_dir_blocks(self, tmp_path):
        config = ConfigResolver().resolve([
            "--concept-file", str(tmp_path / "c.md"),
            "--mock",
        ])
        config.run_root = str(tmp_path / "runs2")
        workflow = EvolveAgentWorkflow(config)
        result = workflow.run()

        assert result.status == "BLOCKED"
        assert "missing --agent-dir" in result.message.lower()

    def test_nonexistent_agent_dir_blocks(self, tmp_path):
        concept = tmp_path / "c.md"
        concept.write_text("test")
        config = ConfigResolver().resolve([
            "--agent-dir", str(tmp_path / "nonexistent"),
            "--concept-file", str(concept),
            "--mock",
        ])
        config.run_root = str(tmp_path / "runs3")
        workflow = EvolveAgentWorkflow(config)
        result = workflow.run()

        assert result.status == "BLOCKED"
        assert "not found" in result.message.lower()

    def test_missing_concept_file_blocks(self, tmp_path):
        agent_dir = tmp_path / "target"
        agent_dir.mkdir()
        config = ConfigResolver().resolve([
            "--agent-dir", str(agent_dir),
            "--mock",
        ])
        config.run_root = str(tmp_path / "runs4")
        workflow = EvolveAgentWorkflow(config)
        result = workflow.run()

        assert result.status == "BLOCKED"
        assert "missing --concept-file" in result.message.lower()

    def test_apply_dry_run_mock(self, tmp_path):
        agent_dir = tmp_path / "target_agent2"
        agent_dir.mkdir()
        concept = tmp_path / "upgrade2.md"
        concept.write_text("## Add README\n\nCreate README.md")

        config = ConfigResolver().resolve([
            "--agent-dir", str(agent_dir),
            "--concept-file", str(concept),
            "--mode", "apply", "--dry-run", "--mock",
        ])
        config.run_root = str(tmp_path / "runs5")
        workflow = EvolveAgentWorkflow(config)
        result = workflow.run()

        assert result.status == "PASS"
        run_dir = pathlib.Path(result.run_dir)
        assert (run_dir / "applied_patch.diff").exists()

    def test_target_boundary_enforced(self, tmp_path):
        agent_dir = tmp_path / "boundary_agent"
        agent_dir.mkdir()
        concept = tmp_path / "bad_upgrade.md"
        concept.write_text("## Bad change\n\nModify controller")

        config = ConfigResolver().resolve([
            "--agent-dir", str(agent_dir),
            "--concept-file", str(concept),
            "--mode", "plan", "--dry-run", "--mock",
        ])
        config.run_root = str(tmp_path / "runs6")

        from agentx_evolve.runtime.plan_parser import PlanParseError
        from agentx_evolve.providers.mock_provider import MockProvider
        workflow = EvolveAgentWorkflow(config)
        plan = MockProvider().complete_structured([
            {"role": "user", "content": "Say READY"},
        ])
        plan["actions"] = [
            {"type": "patch", "description": "bad", "target": "../../controller/x.py"},
        ]
        plan["patches"] = [
            {"format": "unified_diff", "content": "diff --git a/foo b/bar\n--- a/foo\n+++ b/bar\n@@ -1 +1 @@\n-old\n+new\n"},
        ]

        from pathlib import Path as P
        try:
            EvolveAgentWorkflow._enforce_target_boundary(plan, agent_dir)
            assert False, "should have raised"
        except PlanParseError:
            pass

    def test_artifacts_written(self, tmp_path):
        agent_dir = tmp_path / "artifacts_agent"
        agent_dir.mkdir()
        concept = tmp_path / "artifacts_upgrade.md"
        concept.write_text("## Test\n\nMinor change")

        config = ConfigResolver().resolve([
            "--agent-dir", str(agent_dir),
            "--concept-file", str(concept),
            "--mode", "plan", "--dry-run", "--mock",
        ])
        config.run_root = str(tmp_path / "runs7")
        workflow = EvolveAgentWorkflow(config)
        result = workflow.run()

        run_dir = pathlib.Path(result.run_dir)
        for name in ["run_metadata.json", "resolved_config.json", "preflight.json",
                      "request.json",
                      "packed_context.json", "model_messages.jsonl", "model_response.json",
                      "structured_plan.json", "proposed_patch.diff",
                      "validation_report.json", "evidence_manifest.json",
                      "final_verdict.json", "implementation_ledger.json"]:
            assert (run_dir / name).exists(), f"missing {name}"
