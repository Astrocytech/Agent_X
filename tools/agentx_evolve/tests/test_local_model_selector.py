import pytest
from agentx_evolve.model_runtime.model_selector import (
    check_model_eligibility, select_local_model, rank_eligible_models,
)
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelEligibilityDecision, LocalModelSelectionConstraints,
    ELIGIBILITY_ELIGIBLE, ELIGIBILITY_INELIGIBLE, ELIGIBILITY_BLOCKED,
)


def test_model_selector_ranking_is_deterministic():
    d1 = LocalModelEligibilityDecision(decision_id="d1", timestamp="t1", selected_model_id="a", eligibility=ELIGIBILITY_ELIGIBLE)
    d2 = LocalModelEligibilityDecision(decision_id="d2", timestamp="t2", selected_model_id="b", eligibility=ELIGIBILITY_ELIGIBLE)
    constraints = LocalModelSelectionConstraints()
    ranked = rank_eligible_models([d2, d1], constraints)
    assert ranked[0].selected_model_id == "a"
    assert ranked[1].selected_model_id == "b"


def test_check_eligibility_returns_decision():
    decision = check_model_eligibility("test-model", {"task_type": "chat", "context_tokens": 1024}, {}, {})
    assert decision.selected_model_id == "test-model"
    assert decision.eligibility == ELIGIBILITY_INELIGIBLE


def test_select_local_model_empty_repository():
    decision = select_local_model({}, {}, {})
    assert decision.eligibility == ELIGIBILITY_BLOCKED
