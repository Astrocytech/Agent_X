import json, os, sys, tempfile
from pathlib import Path


class TestNegativeL0MutationRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_l0_write_is_blocked(self):
        from agentx_evolve.security.path_boundary import check_path_boundary
        from agentx_evolve.security.security_models import SandboxPolicy, DECISION_BLOCK

        policy = SandboxPolicy()
        decision = check_path_boundary("L0/some_file.py", self.tmpdir, "WRITE", policy)
        assert decision.decision == DECISION_BLOCK
        assert any("L0" in r for r in decision.applied_rule_ids)

    def test_l0_edit_is_blocked(self):
        from agentx_evolve.security.path_boundary import check_path_boundary
        from agentx_evolve.security.security_models import SandboxPolicy, DECISION_BLOCK

        policy = SandboxPolicy()
        decision = check_path_boundary("L0/CODE/core.py", self.tmpdir, "EDIT", policy)
        assert decision.decision == DECISION_BLOCK
        assert any("L0" in r for r in decision.applied_rule_ids)

    def test_l0_patch_precheck_is_blocked(self):
        from agentx_evolve.security.path_boundary import check_path_boundary
        from agentx_evolve.security.security_models import SandboxPolicy, DECISION_BLOCK

        policy = SandboxPolicy()
        decision = check_path_boundary("L0/", self.tmpdir, "PATCH_PRECHECK", policy)
        assert decision.decision == DECISION_BLOCK
