import json, os, sys, tempfile
from pathlib import Path


class TestNegativeMakefileOmitsSuitesRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_makefile_missing_required_targets_detected(self):
        makefile = self.tmpdir / "Makefile"
        makefile.write_text("""test-smoke:\n\tpython -m pytest tests/smoke\n""")
        content = makefile.read_text()
        required = ["test-system", "test-regression", "test-live"]
        missing = [t for t in required if t not in content]
        assert len(missing) > 0
        assert "test-system" in missing

    def test_makefile_omitting_test_suite_audit_fails(self):
        makefile = self.tmpdir / "Makefile"
        makefile.write_text(".PHONY: test-smoke\ntest-smoke:\n\tpython -m pytest tests/smoke\n")
        lines = makefile.read_text()
        expected_suites = {"test-smoke", "test-integration", "test-system", "test-evolve", "test-initiator"}
        declared = {line.split(":")[0].strip() for line in lines.splitlines() if ":" in line and not line.startswith("\t") and not line.startswith(".")}
        missing = expected_suites - declared
        assert "test-evolve" in missing or "test-integration" in missing

    def test_makefile_audit_adds_blocker(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L2": STATUS_PASS},
            blockers=["Makefile audit: missing required target 'test-system'"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("Makefile" in b for b in blockers)
