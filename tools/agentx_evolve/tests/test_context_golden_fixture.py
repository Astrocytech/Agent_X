import pytest
from agentx_evolve.context.context_models import GoldenFixture, FixtureResult, FR_PASS, FR_FAIL


class TestGoldenFixtureConstants:
    def test_fr_pass_value(self):
        assert FR_PASS == "PASS"

    def test_fr_fail_value(self):
        assert FR_FAIL == "FAIL"


class TestFixtureResult:
    def test_defaults(self):
        result = FixtureResult()
        assert result.status == FR_PASS
        assert result.deviations == []

    def test_failure_result(self):
        result = FixtureResult(status=FR_FAIL, deviations=["mismatch"])
        assert result.status == FR_FAIL
        assert "mismatch" in result.deviations


class TestGoldenFixture:
    def test_validate_known_good_input(self):
        fixture = GoldenFixture(
            fixture_id="gf_001",
            name="test_fixture",
            expected_output={"a": 1, "b": "hello"},
        )
        result = fixture.validate({"a": 1, "b": "hello"})
        assert result.status == FR_PASS
        assert result.deviations == []

    def test_fixture_detects_deviation(self):
        fixture = GoldenFixture(
            fixture_id="gf_002",
            expected_output={"x": 10, "y": 20},
        )
        result = fixture.validate({"x": 10, "y": 99})
        assert result.status == FR_FAIL
        assert len(result.deviations) == 1

    def test_fixture_detects_missing_key(self):
        fixture = GoldenFixture(
            fixture_id="gf_003",
            expected_output={"a": 1, "b": 2},
        )
        result = fixture.validate({"a": 1})
        assert result.status == FR_FAIL

    def test_fixture_extra_keys_ignored(self):
        fixture = GoldenFixture(
            fixture_id="gf_004",
            expected_output={"a": 1},
        )
        result = fixture.validate({"a": 1, "extra": "ignored"})
        assert result.status == FR_PASS
