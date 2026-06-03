from agentx_evolve.context.context_models import (
    TaskPack, ContextPack, ContextItem, TaskInput,
    TP_READY, TP_DRAFT, TP_BLOCKED, TP_INVALID,
    COMPATIBLE, INCOMPATIBLE_OVER_CONTEXT_WINDOW, INCOMPATIBLE_MODEL_POLICY,
)
from agentx_evolve.context.task_pack_validator import (
    validate_task_pack, validate_context_pack,
)


_MISSING = object()


def _sample_input():
    return TaskInput(task_input_id="ti-1", task_title="test")


def _make_task_pack(task_pack_id="tp-1", status="DRAFT",
                    task_input=_MISSING, context_pack=None,
                    errors=None, warnings=None, evidence_refs=None):
    if task_input is _MISSING:
        task_input = _sample_input()
    return TaskPack(
        task_pack_id=task_pack_id, status=status, created_at="2026-01-01T00:00:00",
        task_input=task_input, context_pack=context_pack,
        errors=errors or [], warnings=warnings or [],
        evidence_refs=evidence_refs or [],
    )


class TestValidateTaskPack:
    def test_valid_ready(self):
        tp = _make_task_pack()
        result = validate_task_pack(tp)
        assert result["status"] == TP_READY

    def test_missing_task_input(self):
        tp = _make_task_pack()
        tp.task_input = None
        result = validate_task_pack(tp)
        assert result["status"] == TP_INVALID
        assert any("missing task_input" in e for e in result["errors"])

    def test_context_pack_over_budget(self):
        cp = ContextPack(
            context_pack_id="cp-1",
            max_context_tokens=1000,
            total_estimated_tokens=2000,
        )
        tp = _make_task_pack(context_pack=cp)
        result = validate_task_pack(tp)
        assert result["budget_valid"] is False

    def test_evidence_refs_present(self):
        tp = _make_task_pack(evidence_refs=["e1"])
        result = validate_task_pack(tp)
        assert result["evidence_refs_present"] is True

    def test_no_evidence_refs(self):
        tp = _make_task_pack(evidence_refs=[])
        result = validate_task_pack(tp)
        assert result["evidence_refs_present"] is False

    def test_model_error_detected(self):
        tp = _make_task_pack(errors=["model mismatch error"])
        result = validate_task_pack(tp)
        assert result["model_compatible"] is False

    def test_injection_error_from_context_pack(self):
        cp = ContextPack(
            context_pack_id="cp-1", errors=["injection detected"],
        )
        tp = _make_task_pack(context_pack=cp)
        result = validate_task_pack(tp)
        assert result["injection_risk_accepted"] is False

    def test_custom_validation_context(self):
        tp = _make_task_pack()
        result = validate_task_pack(tp, validation_context={"prompt_contract_id": "pc-1"})
        assert result["prompt_contract_compatible"] is True


class TestValidateContextPack:
    def test_pass_no_items(self):
        cp = ContextPack(
            context_pack_id="cp-1",
            max_context_tokens=10000,
            total_estimated_tokens=500,
        )
        result = validate_context_pack(cp)
        assert result["status"] == "PASS"
        assert result["item_count"] == 0
        assert result["within_budget"] is True

    def test_fail_over_budget(self):
        cp = ContextPack(
            context_pack_id="cp-1",
            max_context_tokens=1000,
            total_estimated_tokens=2000,
        )
        result = validate_context_pack(cp)
        assert result["status"] == "FAIL"
        assert result["within_budget"] is False

    def test_warning_on_no_items(self):
        cp = ContextPack(
            context_pack_id="cp-1",
            max_context_tokens=5000,
            total_estimated_tokens=100,
        )
        result = validate_context_pack(cp)
        assert "no included items" in " ".join(result["warnings"])

    def test_with_items_no_warning(self):
        cp = ContextPack(
            context_pack_id="cp-1",
            max_context_tokens=5000,
            total_estimated_tokens=100,
            included_items=[ContextItem(context_item_id="i1", content="test")],
        )
        result = validate_context_pack(cp)
        assert result["status"] == "PASS"
        assert result["item_count"] == 1
        assert result["within_budget"] is True
