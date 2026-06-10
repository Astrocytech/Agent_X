import json, os, sys, tempfile
from pathlib import Path


class TestNegativePatchBypassesPolicyRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_patch_to_unapproved_path_blocked(self):
        from agentx_evolve.patch_execution.patch_policy import check_patch_operation_allowed
        from agentx_evolve.patch_execution.patch_models import PatchOperation, OP_WRITE_FILE

        op = PatchOperation(operation_id="op1", operation_type=OP_WRITE_FILE, target_path="L1/internal/secret.py", content="evil")
        decision = check_patch_operation_allowed(op, approved_paths=["L2/public/"])
        assert decision.decision == "BLOCK"
        assert "not in approved_paths" in decision.reason.lower()

    def test_patch_calling_lower_level_blocked(self):
        from agentx_evolve.patch_execution.patch_policy import check_patch_operation_allowed
        from agentx_evolve.patch_execution.patch_models import PatchOperation, OP_EXACT_EDIT

        op = PatchOperation(operation_id="op2", operation_type=OP_EXACT_EDIT, target_path="L0/boot.py", new_text="patched")
        decision = check_patch_operation_allowed(op, approved_paths=["tools/agentx_evolve/"])
        assert decision.decision == "BLOCK"
        assert "not in approved_paths" in decision.reason.lower()

    def test_patch_policy_bypass_detected_as_blocker(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L3": STATUS_PASS},
            blockers=["Patch policy bypass: operation on path L0/boot.py not in approved paths"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("Patch policy" in b for b in blockers)
