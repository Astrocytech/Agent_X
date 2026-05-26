from agentx_initiator.core.governance_engine import run_governance_checks


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
