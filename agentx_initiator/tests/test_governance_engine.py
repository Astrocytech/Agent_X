import pytest
from agentx_initiator.core.governance_engine import run_governance_checks


pytestmark = pytest.mark.skip(reason="PM2 governance_engine not active in Product Milestone 1")


def test_governance_checks_return_list():
    results = run_governance_checks()
    assert isinstance(results, list)
    assert len(results) > 0


def test_each_check_has_required_fields():
    results = run_governance_checks()
    for r in results:
        assert "check" in r
        assert "passed" in r
        assert "detail" in r
