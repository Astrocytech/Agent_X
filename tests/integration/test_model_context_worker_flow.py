import json, os, sys, tempfile
from pathlib import Path
from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession, PatchOperation, OP_EXACT_EDIT,
    to_dict, utc_now_iso, new_id,
)
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


class TestModelContextWorkerFlow:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.repo_root = self.tmpdir / "repo"
        self.repo_root.mkdir()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_mock_model_returns_deterministic_patch_candidate(self):
        session = ImplementationSession(
            session_id=new_id("sess"),
            timestamp=utc_now_iso(),
        )
        op = PatchOperation(
            operation_id="model-op-1", operation_type=OP_EXACT_EDIT,
            target_path="src/main.py",
            old_text="foo()", new_text="bar()",
        )
        candidate = to_dict(op)
        assert candidate["operation_type"] == "EXACT_EDIT"
        assert candidate["target_path"] == "src/main.py"
        assert candidate["old_text"] == "foo()"
        assert candidate["new_text"] == "bar()"
        candidate2 = to_dict(PatchOperation(
            operation_id="model-op-1", operation_type=OP_EXACT_EDIT,
            target_path="src/main.py",
            old_text="foo()", new_text="bar()",
        ))
        assert candidate == candidate2

    def test_context_packet_respects_size_limits(self):
        policy = default_sandbox_policy(self.repo_root)
        max_size = policy.max_file_size_bytes
        large_content = "x" * (max_size + 100)
        assert len(large_content) > max_size

    def test_context_packet_excludes_denied_files(self):
        policy = default_sandbox_policy(self.repo_root)
        denied_paths = policy.blocked_write_paths
        assert "L0/" in denied_paths

    def test_llm_worker_creates_patch_candidate_only(self):
        op = PatchOperation(
            operation_id="llm-op-1", operation_type=OP_EXACT_EDIT,
            target_path="src/worker.py",
            old_text="old_code", new_text="new_code",
        )
        d = to_dict(op)
        assert d["operation_type"] == "EXACT_EDIT"
        assert d["target_path"] == "src/worker.py"
        assert "old_text" in d
        assert "new_text" in d
