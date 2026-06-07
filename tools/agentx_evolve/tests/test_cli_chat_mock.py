import json
import pathlib
import sys

from agentx_evolve.runtime.config import ConfigResolver
from agentx_evolve.runtime.results import CLIResult, EXIT_PASS, EXIT_FAIL
from agentx_evolve.providers.mock_provider import MockProvider
from agentx_evolve.workflows.chat import ChatWorkflow


class TestChatMockGate:
    def test_chat_ready(self, tmp_path):
        resolver = ConfigResolver()
        config = resolver.resolve(["--once", "Say READY", "--mock", "--json"])
        config.run_root = str(tmp_path / "runs")
        workflow = ChatWorkflow(config)
        result = workflow.run()

        assert result.status == "PASS"
        assert result.exit_code == EXIT_PASS
        assert "READY" in result.message

    def test_chat_unknown_message(self, tmp_path):
        resolver = ConfigResolver()
        config = resolver.resolve(["--once", "hello world", "--mock"])
        config.run_root = str(tmp_path / "runs2")
        workflow = ChatWorkflow(config)
        result = workflow.run()

        assert result.status == "PASS"
        assert "hello world" in result.message or "Mock response" in result.message

    def test_json_output_shape(self, tmp_path):
        resolver = ConfigResolver()
        config = resolver.resolve(["--once", "Say READY", "--mock", "--json"])
        config.run_root = str(tmp_path / "runs3")
        workflow = ChatWorkflow(config)
        result = workflow.run()
        d = result.to_dict()

        assert d["schema_version"] == "agentx.cli_result.v1"
        assert d["command"] == "chat"
        assert d["status"] == "PASS"
        assert d["exit_code"] == 0
        assert isinstance(d["run_id"], str)
        assert isinstance(d["run_dir"], str)
        assert isinstance(d["artifacts"], dict)
        assert "final_verdict" in d["artifacts"]
        assert "evidence_manifest" in d["artifacts"]

    def test_artifacts_created(self, tmp_path):
        resolver = ConfigResolver()
        config = resolver.resolve(["--once", "Say READY", "--mock"])
        config.run_root = str(tmp_path / "runs4")
        workflow = ChatWorkflow(config)
        result = workflow.run()

        run_dir = pathlib.Path(result.run_dir)
        required = [
            "final_verdict.json", "evidence_manifest.json", "request.json",
            "resolved_config.json", "run_metadata.json", "preflight.json",
            "packed_context.json", "model_messages.jsonl", "model_response.json",
            "validation_report.json", "implementation_ledger.json",
        ]
        for name in required:
            path = run_dir / name
            assert path.exists(), f"missing {name}"

        verdict = json.loads((run_dir / "final_verdict.json").read_text())
        assert verdict["status"] == "PASS"

        evidence = json.loads((run_dir / "evidence_manifest.json").read_text())
        assert evidence["run_id"] == result.run_id
        assert evidence["source_mutation_detected"] is False

    def test_no_source_mutation(self, tmp_path):
        import hashlib
        resolver = ConfigResolver()
        config = resolver.resolve(["--once", "Say READY", "--mock"])
        config.run_root = str(tmp_path / "runs5")

        source_files = sorted(pathlib.Path("tools/agentx_evolve").rglob("*.py"))
        before = {}
        for f in source_files:
            before[str(f)] = hashlib.sha256(f.read_bytes()).hexdigest()

        workflow = ChatWorkflow(config)
        workflow.run()

        after = {}
        for f in source_files:
            after[str(f)] = hashlib.sha256(f.read_bytes()).hexdigest()

        for key in before:
            assert before[key] == after[key], f"source mutated: {key}"
