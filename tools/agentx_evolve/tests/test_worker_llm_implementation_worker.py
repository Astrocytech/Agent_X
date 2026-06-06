import pytest
from agentx_evolve.worker.llm_implementation_worker import (
    EditPlanGenerator,
    PatchCandidateGenerator,
    TestCandidateGenerator,
    ValidationFixGenerator,
    LLMImplementationWorker,
)
from agentx_evolve.worker.worker_models import (
    WorkerOutput,
    WO_PROPOSED, WO_NEEDS_MORE_CONTEXT, WO_FAILED,
    CT_UPDATE, CT_CREATE,
)
from agentx_evolve.context.context_models import TaskPacket, TT_IMPLEMENT_PATCH, TT_FIX_VALIDATION, TT_WRITE_TEST, TT_EXPLAIN_FAILURE
from agentx_evolve.model.model_models import ModelResponse, MD_SUCCESS, MD_INSUFFICIENT_CONTEXT


# ---------------------------------------------------------------------------
# EditPlanGenerator
# ---------------------------------------------------------------------------

def test_edit_plan_generator_basic():
    g = EditPlanGenerator()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix parser")
    plan = g.generate(packet)
    assert "Edit Plan" in plan
    assert "fix parser" in plan


def test_edit_plan_generator_with_allowed_files():
    g = EditPlanGenerator()
    packet = TaskPacket(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix parser",
        allowed_files=["src/parser.py", "src/utils.py"],
    )
    plan = g.generate(packet)
    assert "Allowed Files" in plan
    assert "src/parser.py" in plan
    assert "src/utils.py" in plan


def test_edit_plan_generator_with_forbidden_files():
    g = EditPlanGenerator()
    packet = TaskPacket(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix",
        allowed_files=["a.py"],
        forbidden_files=["b.py"],
    )
    plan = g.generate(packet)
    assert "b.py" in plan


def test_edit_plan_generator_no_allowed_files():
    g = EditPlanGenerator()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix")
    plan = g.generate(packet)
    assert "Allowed Files" not in plan


# ---------------------------------------------------------------------------
# PatchCandidateGenerator
# ---------------------------------------------------------------------------

def test_patch_candidate_generator_basic():
    g = PatchCandidateGenerator()
    packet = TaskPacket(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix bug",
        allowed_files=["a.py", "b.py"],
    )
    output = g.generate(packet, "plan text")
    assert output.status == WO_PROPOSED
    assert len(output.changes) == 2
    assert all(c.change_type == CT_UPDATE for c in output.changes)


def test_patch_candidate_with_model_response_success():
    g = PatchCandidateGenerator()
    packet = TaskPacket(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix",
        allowed_files=["a.py"],
    )
    resp = ModelResponse(status=MD_SUCCESS, content="patch content")
    output = g.generate(packet, "plan", resp)
    assert output.status == WO_PROPOSED
    assert len(output.changes) == 1


def test_patch_candidate_insufficient_context():
    g = PatchCandidateGenerator()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix")
    resp = ModelResponse(status=MD_INSUFFICIENT_CONTEXT)
    output = g.generate(packet, "plan", resp)
    assert output.status == WO_NEEDS_MORE_CONTEXT
    assert len(output.changes) == 0


def test_patch_candidate_no_allowed_files():
    g = PatchCandidateGenerator()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix")
    output = g.generate(packet, "plan")
    assert output.status == WO_PROPOSED
    assert len(output.changes) == 0


# ---------------------------------------------------------------------------
# TestCandidateGenerator
# ---------------------------------------------------------------------------

def test_test_candidate_generator_basic():
    g = TestCandidateGenerator()
    packet = TaskPacket(
        task_type=TT_WRITE_TEST,
        objective="write tests",
        allowed_files=["src/parser.py"],
    )
    output = g.generate(packet, "plan")
    assert output.status == WO_PROPOSED
    assert len(output.changes) == 1
    assert "test_" in output.changes[0].target_file
    assert output.changes[0].change_type == CT_CREATE


def test_test_candidate_generator_no_files():
    g = TestCandidateGenerator()
    packet = TaskPacket(task_type=TT_WRITE_TEST, objective="write tests")
    output = g.generate(packet, "plan")
    assert len(output.changes) == 0
    assert output.tests_to_run == []


def test_test_candidate_generator_multiple_files():
    g = TestCandidateGenerator()
    packet = TaskPacket(
        task_type=TT_WRITE_TEST,
        objective="write tests",
        allowed_files=["src/a.py", "src/b.py"],
    )
    output = g.generate(packet, "plan")
    assert len(output.changes) == 2
    assert len(output.tests_to_run) == 2


# ---------------------------------------------------------------------------
# ValidationFixGenerator
# ---------------------------------------------------------------------------

def test_validation_fix_generator_with_failures():
    g = ValidationFixGenerator()
    packet = TaskPacket(
        task_type=TT_FIX_VALIDATION,
        objective="fix tests",
        allowed_files=["src/main.py"],
    )
    output = g.generate(packet, "plan", test_output="FAILED test_main")
    assert output.status == WO_PROPOSED
    assert len(output.changes) == 1
    assert any("failures" in w.lower() for w in output.warnings)


def test_validation_fix_generator_no_failures():
    g = ValidationFixGenerator()
    packet = TaskPacket(
        task_type=TT_FIX_VALIDATION,
        objective="fix",
        allowed_files=["src/main.py"],
    )
    output = g.generate(packet, "plan", test_output="All tests passed!")
    assert len(output.changes) == 1
    assert len(output.warnings) == 0


def test_validation_fix_generator_empty_test_output():
    g = ValidationFixGenerator()
    packet = TaskPacket(
        task_type=TT_FIX_VALIDATION,
        objective="fix",
        allowed_files=["src/main.py"],
    )
    output = g.generate(packet, "plan", test_output="")
    assert len(output.changes) == 1


def test_validation_fix_generator_no_files():
    g = ValidationFixGenerator()
    packet = TaskPacket(task_type=TT_FIX_VALIDATION, objective="fix")
    output = g.generate(packet, "plan", test_output="FAILED")
    assert len(output.changes) == 0


# ---------------------------------------------------------------------------
# LLMImplementationWorker
# ---------------------------------------------------------------------------

def test_worker_processes_patch_task():
    worker = LLMImplementationWorker()
    packet = TaskPacket(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix parser",
        allowed_files=["src/parser.py"],
    )
    output = worker.process(packet)
    assert output.task_packet_id == packet.task_packet_id
    assert output.status in (WO_PROPOSED, WO_NEEDS_MORE_CONTEXT, WO_FAILED)


def test_worker_processes_fix_validation():
    worker = LLMImplementationWorker()
    packet = TaskPacket(
        task_type=TT_FIX_VALIDATION,
        objective="fix tests",
        allowed_files=["src/main.py"],
    )
    output = worker.process(packet, test_output="FAILED test_foo")
    assert output.status == WO_PROPOSED


def test_worker_processes_fix_validation_no_failures():
    worker = LLMImplementationWorker()
    packet = TaskPacket(
        task_type=TT_FIX_VALIDATION,
        objective="fix tests",
        allowed_files=["src/main.py"],
    )
    output = worker.process(packet, test_output="All OK")
    assert output.status == WO_PROPOSED


def test_worker_processes_write_test():
    worker = LLMImplementationWorker()
    packet = TaskPacket(
        task_type=TT_WRITE_TEST,
        objective="write tests",
        allowed_files=["src/parser.py"],
    )
    output = worker.process(packet)
    assert output.status == WO_PROPOSED
    assert any("test_" in c.target_file for c in output.changes)


def test_worker_respects_forbidden_files():
    worker = LLMImplementationWorker()
    packet = TaskPacket(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix",
        allowed_files=["a.py"],
        forbidden_files=["a.py"],
    )
    output = worker.process(packet)
    assert output.status == WO_FAILED
    assert any("forbidden" in e.lower() for e in output.errors)


def test_worker_no_changes_for_empty_allowed():
    worker = LLMImplementationWorker()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix")
    output = worker.process(packet)
    assert output is not None
    assert output.status in (WO_PROPOSED, WO_NEEDS_MORE_CONTEXT, WO_FAILED)


def test_worker_propagates_packet_errors():
    worker = LLMImplementationWorker()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix")
    packet.errors.append("packet error")
    output = worker.process(packet)
    assert any("packet error" in e for e in output.errors)


def test_worker_with_explain_failure():
    worker = LLMImplementationWorker()
    packet = TaskPacket(
        task_type=TT_EXPLAIN_FAILURE,
        objective="explain failure",
        allowed_files=["src/main.py"],
    )
    output = worker.process(packet)
    assert output.status in (WO_PROPOSED, WO_NEEDS_MORE_CONTEXT)


def test_worker_output_has_explanation_for_patch():
    worker = LLMImplementationWorker()
    packet = TaskPacket(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix parser",
        allowed_files=["src/parser.py"],
    )
    output = worker.process(packet)
    assert output.edit_plan != ""


def test_worker_with_custom_prompt_runner():
    from agentx_evolve.model.prompt_runner import PromptRunner
    runner = PromptRunner()
    worker = LLMImplementationWorker(prompt_runner=runner)
    packet = TaskPacket(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix",
        allowed_files=["a.py"],
    )
    output = worker.process(packet)
    assert output is not None
