import pytest

from agentx_evolve.runtime.config import ConfigResolver
from agentx_evolve.runtime.results import (
    EXIT_BLOCKED, EXIT_PROVIDER_ERROR,
    STATUS_BLOCKED,
)
from agentx_evolve.workflows.self_upgrade import SelfUpgradeWorkflow
from agentx_evolve.workflows.evolve_agent import EvolveAgentWorkflow
from agentx_evolve.workflows.init_agent import InitAgentWorkflow
from agentx_evolve.workflows.chat import ChatWorkflow
from agentx_evolve.runtime.plan_parser import StructuredPlanParser, PlanParseError
from agentx_evolve.providers.opencode_provider import OpenCodeProvider, OpenCodeProviderError
from agentx_evolve.runtime.artifacts import ArtifactWriter
from agentx_evolve.providers.mock_provider import MockProvider


class TestSafetyNegative:
    """Comprehensive safety negative test suite covering Section 21 matrix."""

    # ── Case 1: missing concept file → BLOCKED, exit 2 ──────────────────────

    def test_1_missing_concept_file_blocks(self, tmp_path):
        config = ConfigResolver().resolve(["--mock"])
        config.run_root = str(tmp_path / "runs1")
        workflow = SelfUpgradeWorkflow(config)
        result = workflow.run()

        assert result.status == STATUS_BLOCKED
        assert result.exit_code == EXIT_BLOCKED
        assert "missing --concept-file" in result.message.lower()

    # ── Case 2: invalid CLI flag → exit 3 ───────────────────────────────────

    def test_2_invalid_cli_flag_exit_code(self):
        with pytest.raises(ValueError, match="unknown flag"):
            ConfigResolver().resolve(["--bogus-flag"])



    # ── Case 3: malformed structured plan → FAIL, exit 1 ────────────────────

    def test_3_malformed_plan_missing_schema(self, tmp_path):
        plan = {"summary": "bad", "actions": [], "patches": [], "validation_commands": []}
        parser = StructuredPlanParser()
        with pytest.raises(PlanParseError, match="missing schema_version"):
            parser.parse(plan)

    def test_3_malformed_plan_malformed_json(self, tmp_path):
        parser = StructuredPlanParser()
        with pytest.raises(PlanParseError, match="malformed JSON"):
            parser.parse("{bad json")

    # ── Case 4: patch path escapes root → BLOCKED, exit 2 ──────────────────

    def test_4_patch_path_escape_root(self, tmp_path):
        agent_dir = tmp_path / "target"
        agent_dir.mkdir()
        concept = tmp_path / "c.md"
        concept.write_text("escape")

        config = ConfigResolver().resolve([
            "--agent-dir", str(agent_dir),
            "--concept-file", str(concept),
            "--mode", "plan", "--dry-run", "--mock",
        ])
        config.run_root = str(tmp_path / "runs4")
        workflow = EvolveAgentWorkflow(config)

        plan = MockProvider().complete_structured([
            {"role": "user", "content": "Say READY"},
        ])
        plan["actions"] = [
            {"type": "patch", "description": "escape via ..", "target": "../../etc/passwd"},
        ]
        plan["patches"] = [
            {"format": "unified_diff", "content": "diff --git a/foo b/bar\n--- a/foo\n+++ b/bar\n@@ -1 +1 @@\n-old\n+new\n"},
        ]

        with pytest.raises(PlanParseError, match="escape|boundary"):
            EvolveAgentWorkflow._enforce_target_boundary(plan, agent_dir)

    # ── Case 5: absolute patch path → BLOCKED, exit 2 ───────────────────────

    def test_5_absolute_patch_path(self):
        parser = StructuredPlanParser()
        plan = {
            "schema_version": "agentx.structured_plan.v1",
            "summary": "test",
            "actions": [{"type": "patch", "description": "abs", "target": "/etc/passwd"}],
            "patches": [],
            "validation_commands": [],
        }
        with pytest.raises(PlanParseError, match="absolute path"):
            parser.parse(plan)

    # ── Case 6: symlink escape → BLOCKED, exit 2 ────────────────────────────

    def test_6_symlink_escape_via_boundary(self, tmp_path):
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("sensitive")

        agent_dir = tmp_path / "target"
        agent_dir.mkdir()
        link = agent_dir / "escape_link"
        link.symlink_to(outside)

        concept = tmp_path / "c.md"
        concept.write_text("evolve with symlink")

        config = ConfigResolver().resolve([
            "--agent-dir", str(agent_dir),
            "--concept-file", str(concept),
            "--mode", "plan", "--dry-run", "--mock",
        ])
        config.run_root = str(tmp_path / "runs6")
        workflow = EvolveAgentWorkflow(config)

        plan = MockProvider().complete_structured([
            {"role": "user", "content": "Say READY"},
        ])
        plan["actions"] = [
            {"type": "patch", "description": "via symlink", "target": "escape_link/secret.txt"},
        ]
        plan["patches"] = [
            {"format": "unified_diff", "content": "diff --git a/foo b/bar\n--- a/foo\n+++ b/bar\n@@ -1 +1 @@\n-old\n+new\n"},
        ]

        with pytest.raises(PlanParseError, match="escape|boundary"):
            EvolveAgentWorkflow._enforce_target_boundary(plan, agent_dir)

    # ── Case 7: blocked command → BLOCKED, exit 2 ───────────────────────────

    def test_7_blocked_command(self):
        parser = StructuredPlanParser()
        plan = {
            "schema_version": "agentx.structured_plan.v1",
            "summary": "test",
            "actions": [{"type": "noop", "description": "t", "target": ""}],
            "patches": [],
            "validation_commands": ["rm -rf /"],
        }
        with pytest.raises(PlanParseError, match="blocked command"):
            parser.parse(plan)

    # ── Case 8: missing OpenCode API key → BLOCKED, exit 2 ──────────────────

    def test_8_missing_api_key_blocks(self):
        p = OpenCodeProvider(api_key="")
        with pytest.raises(OpenCodeProviderError) as exc:
            p._check_key()
        assert exc.value.exit_code == EXIT_BLOCKED
        assert exc.value.status == STATUS_BLOCKED

    # ── Case 9: provider timeout → FAIL, exit 4 ─────────────────────────────

    def test_9_provider_timeout(self, tmp_path):
        import urllib.error
        from unittest.mock import patch, MagicMock

        provider = OpenCodeProvider(
            api_key="sk-test", base_url="https://example.com",
            model="big-pickle",
        )
        with patch("urllib.request.urlopen") as mock:
            mock.side_effect = urllib.error.URLError("timed out")
            with pytest.raises(OpenCodeProviderError) as exc:
                provider.complete([{"role": "user", "content": "hi"}])
            assert exc.value.exit_code == EXIT_PROVIDER_ERROR
            assert "timeout" in str(exc.value).lower()

    # ── Case 10: artifact write failure → FAIL, exit 6 ──────────────────────

    def test_10_artifact_write_failure_raises_oserror(self, tmp_path):
        run_dir = tmp_path / "readonly_run"
        run_dir.mkdir()
        run_dir.chmod(0o444)
        writer = ArtifactWriter(run_dir)
        with pytest.raises((OSError, PermissionError)):
            writer.atomic_write("test.json", {"key": "value"})
        run_dir.chmod(0o755)

    def test_10_artifact_write_failure_via_chat(self, tmp_path):
        run_root = tmp_path / "readonly_root"
        run_root.mkdir()
        config = ConfigResolver().resolve([
            "--once", "Say READY", "--mock", "--json",
        ])
        config.run_root = str(run_root)
        workflow = ChatWorkflow(config)
        run_root.chmod(0o444)
        with pytest.raises((OSError, PermissionError)):
            workflow.run()
        run_root.chmod(0o755)

    # ── Case 11: existing non-empty init-agent destination → BLOCKED ─────────

    def test_11_nonempty_dest_blocks(self, tmp_path):
        dest = tmp_path / "existing"
        dest.mkdir()
        (dest / "file.txt").write_text("content")

        config = ConfigResolver().resolve([
            "--name", "Test", "--dest", str(dest), "--mock",
        ])
        config.run_root = str(tmp_path / "runs11")
        workflow = InitAgentWorkflow(config)
        result = workflow.run()

        assert result.status == STATUS_BLOCKED
        assert result.exit_code == EXIT_BLOCKED
        assert "not empty" in result.message.lower()

    # ── Case 12: evolve-agent patches controller source → BLOCKED ────────────

    def test_12_evolve_patches_controller_source(self, tmp_path):
        agent_dir = tmp_path / "target"
        agent_dir.mkdir()
        concept = tmp_path / "c.md"
        concept.write_text("bad")

        config = ConfigResolver().resolve([
            "--agent-dir", str(agent_dir),
            "--concept-file", str(concept),
            "--mode", "plan", "--dry-run", "--mock",
        ])
        config.run_root = str(tmp_path / "runs12")
        workflow = EvolveAgentWorkflow(config)

        plan = MockProvider().complete_structured([
            {"role": "user", "content": "Say READY"},
        ])
        plan["actions"] = [
            {"type": "patch", "description": "modify controller", "target": "../controller/x.py"},
        ]
        plan["patches"] = [
            {"format": "unified_diff", "content": "diff --git a/foo b/bar\n--- a/foo\n+++ b/bar\n@@ -1 +1 @@\n-old\n+new\n"},
        ]

        with pytest.raises(PlanParseError, match="escape|boundary"):
            EvolveAgentWorkflow._enforce_target_boundary(plan, agent_dir)
