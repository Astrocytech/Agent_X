import pytest
from agentx_evolve.final_acceptance.acceptance_models import (
    LayerCompletionMatrix, LCM_PASS, LCM_FAIL,
)


class TestLayerCompletionMatrixConstants:
    def test_lcm_pass_value(self):
        assert LCM_PASS == "PASS"

    def test_lcm_fail_value(self):
        assert LCM_FAIL == "FAIL"


class TestLayerCompletionMatrix:
    def test_defaults_pass(self):
        matrix = LayerCompletionMatrix()
        assert matrix.status == LCM_PASS
        assert matrix.total_checks == 0
        assert matrix.passed_checks == 0
        assert matrix.failed_checks == 0

    def test_tracks_fail_per_layer(self):
        matrix = LayerCompletionMatrix(
            layer_id="L1", layer_name="Backup", status=LCM_FAIL,
        )
        assert matrix.layer_id == "L1"
        assert matrix.status == LCM_FAIL

    def test_summary_computes_totals(self):
        matrix = LayerCompletionMatrix(
            layer_id="L2",
            layer_name="Context",
            total_checks=10,
            passed_checks=7,
            failed_checks=3,
        )
        s = matrix.summary
        assert s["total"] == 10
        assert s["passed"] == 7
        assert s["failed"] == 3

    def test_summary_when_all_pass(self):
        matrix = LayerCompletionMatrix(
            layer_id="L3",
            total_checks=5,
            passed_checks=5,
            failed_checks=0,
        )
        s = matrix.summary
        assert s["passed"] == 5
        assert s["failed"] == 0

    def test_custom_layer_name(self):
        matrix = LayerCompletionMatrix(
            layer_id="L4", layer_name="Final Acceptance",
        )
        assert matrix.layer_name == "Final Acceptance"
