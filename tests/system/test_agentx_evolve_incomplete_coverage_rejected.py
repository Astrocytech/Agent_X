import json, os, sys, tempfile
from pathlib import Path


class TestAgentxEvolveIncompleteCoverageRejected:
    """Test that final acceptance rejects incomplete coverage."""

    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_missing_required_layers_cause_not_accepted(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_FAIL,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_FAIL},
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("FAIL" in b for b in blockers)

    def test_not_accepted_when_layers_empty(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import VERDICT_ACCEPTED

        verdict, rating, blockers, high, followups = calculate_final_verdict()
        assert verdict == VERDICT_ACCEPTED

    def test_blockers_prevent_acceptance(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS},
            blockers=["Missing required artifact: L0/approval"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert len(blockers) == 1

    def test_high_issues_prevent_acceptance(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS},
            high_issues=["Validation command test suite failed: 3 failures"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert len(high) == 1

    def test_acceptance_requires_all_layers_pass(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS, STATUS_FAIL,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS, "L2": STATUS_FAIL},
        )
        assert verdict == VERDICT_NOT_ACCEPTED

    # === Negative scenarios 1-4: coverage row verdict types ===

    def test_mandatory_missing_coverage_row_rejected(self):
        """Scenario 1: a mandatory coverage row with MISSING verdict causes NOT_ACCEPTED."""
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"SAFETY": STATUS_PASS},
            blockers=["MISSING mandatory requirement AXE-SEC-XXX: path traversal not implemented"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("MISSING" in b for b in blockers)

    def test_mandatory_partial_coverage_row_rejected(self):
        """Scenario 2: a mandatory coverage row with PARTIAL verdict causes NOT_ACCEPTED."""
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"SAFETY": STATUS_PASS},
            blockers=["PARTIAL mandatory requirement AXE-SEC-XXX: tests missing"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("PARTIAL" in b for b in blockers)

    def test_mandatory_scaffold_only_row_rejected(self):
        """Scenario 3: a mandatory coverage row with SCAFFOLD_ONLY verdict causes NOT_ACCEPTED."""
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"SAFETY": STATUS_PASS},
            blockers=["SCAFFOLD_ONLY mandatory requirement AXE-SEC-XXX: no behavioral assertions"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("SCAFFOLD_ONLY" in b for b in blockers)

    def test_mandatory_unverified_row_rejected(self):
        """Scenario 4: a mandatory coverage row with UNVERIFIED verdict causes NOT_ACCEPTED."""
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"SAFETY": STATUS_PASS},
            blockers=["UNVERIFIED mandatory requirement AXE-SEC-XXX: no direct test"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("UNVERIFIED" in b for b in blockers)
