import pytest
from agentx_evolve.worker.worker_models import (
    WorkerOutput, Change, ReplacementBlock,
    WO_PROPOSED, WO_NEEDS_MORE_CONTEXT, WO_FAILED,
    CT_UPDATE, CT_CREATE, CT_DELETE,
    ALL_WORKER_STATUSES, ALL_CHANGE_TYPES,
)
from agentx_evolve.worker.llm_implementation_worker import (
    LLMImplementationWorker, EditPlanGenerator,
    PatchCandidateGenerator, TestCandidateGenerator, ValidationFixGenerator,
)
from agentx_evolve.context.context_models import (
    TaskPacket, TaskPacketBuilder,
    TT_IMPLEMENT_PATCH, TT_FIX_VALIDATION, TT_WRITE_TEST, TT_EXPLAIN_FAILURE,
)


# ---------------------------------------------------------------------------
# WorkerOutput tests
# ---------------------------------------------------------------------------

def test_worker_output_defaults():
    w = WorkerOutput()
    assert w.schema_version == "1.0"
    assert w.status == WO_PROPOSED
    assert w.allowed_files_only


def test_worker_output_custom():
    w = WorkerOutput(status=WO_FAILED, errors=["something wrong"])
    assert w.status == WO_FAILED


def test_worker_output_has_changes():
    w = WorkerOutput()
    assert not w.has_changes()
    w.changes.append(Change(target_file="a.py"))
    assert w.has_changes()


def test_worker_output_target_files():
    w = WorkerOutput()
    w.changes.append(Change(target_file="a.py"))
    w.changes.append(Change(target_file="b.py"))
    w.changes.append(Change(target_file="a.py"))
    assert w.target_files() == ["a.py", "b.py"]


def test_worker_output_to_dict():
    w = WorkerOutput(worker_output_id="wo-1", task_packet_id="tp-1")
    d = w.to_dict()
    assert d["worker_output_id"] == "wo-1"


# ---------------------------------------------------------------------------
# Change tests
# ---------------------------------------------------------------------------

def test_change_defaults():
    c = Change()
    assert c.change_type == CT_UPDATE


def test_change_custom():
    c = Change(target_file="a.py", change_type=CT_CREATE, instructions="create file")
    assert c.target_file == "a.py"
    assert c.change_type == CT_CREATE


def test_change_to_dict():
    c = Change(target_file="a.py")
    d = c.to_dict()
    assert d["target_file"] == "a.py"


# ---------------------------------------------------------------------------
# ReplacementBlock tests
# ---------------------------------------------------------------------------

def test_replacement_block():
    r = ReplacementBlock(old_string="foo", new_string="bar")
    assert r.old_string == "foo"
    assert r.new_string == "bar"


def test_replacement_block_to_dict():
    r = ReplacementBlock(old_string="a", new_string="b")
    d = r.to_dict()
    assert d["old_string"] == "a"


# ---------------------------------------------------------------------------
# Constants tests
# ---------------------------------------------------------------------------

def test_all_worker_statuses():
    assert WO_PROPOSED in ALL_WORKER_STATUSES
    assert WO_NEEDS_MORE_CONTEXT in ALL_WORKER_STATUSES
    assert WO_FAILED in ALL_WORKER_STATUSES


def test_all_change_types():
    assert CT_UPDATE in ALL_CHANGE_TYPES
    assert CT_CREATE in ALL_CHANGE_TYPES
    assert CT_DELETE in ALL_CHANGE_TYPES


# ---------------------------------------------------------------------------
# EditPlanGenerator tests
# ---------------------------------------------------------------------------

def test_edit_plan_generator():
    g = EditPlanGenerator()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix parser bug",
                        allowed_files=["src/parser.py"])
    plan = g.generate(packet)
    assert "Edit Plan" in plan
    assert "src/parser.py" in plan
    assert "fix parser bug" in plan


def test_edit_plan_generator_with_forbidden():
    g = EditPlanGenerator()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix",
                        allowed_files=["a.py"], forbidden_files=["b.py"])
    plan = g.generate(packet)
    assert "b.py" in plan


# ---------------------------------------------------------------------------
# PatchCandidateGenerator tests
# ---------------------------------------------------------------------------

def test_patch_candidate_generator():
    g = PatchCandidateGenerator()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix",
                        allowed_files=["a.py", "b.py"])
    output = g.generate(packet, "plan text")
    assert output.status == WO_PROPOSED
    assert len(output.changes) == 2


def test_patch_candidate_insufficient_context():
    g = PatchCandidateGenerator()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix")
    from agentx_evolve.models.model_models import ModelResponse, MODEL_STATUS_RETRYABLE
    resp = ModelResponse(status=MODEL_STATUS_RETRYABLE)
    output = g.generate(packet, "plan", resp)
    assert output.status == WO_NEEDS_MORE_CONTEXT


# ---------------------------------------------------------------------------
# TestCandidateGenerator tests
# ---------------------------------------------------------------------------

def test_test_candidate_generator():
    g = TestCandidateGenerator()
    packet = TaskPacket(task_type=TT_WRITE_TEST, objective="write tests",
                        allowed_files=["src/parser.py"])
    output = g.generate(packet, "plan")
    assert output.status == WO_PROPOSED
    assert len(output.changes) == 1
    assert "test_" in output.changes[0].target_file


def test_test_candidate_no_files():
    g = TestCandidateGenerator()
    packet = TaskPacket(task_type=TT_WRITE_TEST, objective="write tests")
    output = g.generate(packet, "plan")
    assert len(output.changes) == 0


# ---------------------------------------------------------------------------
# ValidationFixGenerator tests
# ---------------------------------------------------------------------------

def test_validation_fix_generator():
    g = ValidationFixGenerator()
    packet = TaskPacket(task_type=TT_FIX_VALIDATION, objective="fix tests",
                        allowed_files=["src/main.py"])
    output = g.generate(packet, "plan", test_output="FAILED test_main")
    assert output.status == WO_PROPOSED
    assert len(output.changes) == 1
    assert any("failures" in w.lower() for w in output.warnings)


def test_validation_fix_no_failures():
    g = ValidationFixGenerator()
    packet = TaskPacket(task_type=TT_FIX_VALIDATION, objective="fix",
                        allowed_files=["src/main.py"])
    output = g.generate(packet, "plan", test_output="All tests passed!")
    assert len(output.changes) == 1


# ---------------------------------------------------------------------------
# LLMImplementationWorker integration tests
# ---------------------------------------------------------------------------

def test_worker_processes_patch_task():
    worker = LLMImplementationWorker()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix parser",
                        allowed_files=["src/parser.py"])
    output = worker.process(packet)
    assert output.status in (WO_PROPOSED, WO_NEEDS_MORE_CONTEXT, WO_FAILED)
    assert output.task_packet_id == packet.task_packet_id


def test_worker_processes_fix_validation():
    worker = LLMImplementationWorker()
    packet = TaskPacket(task_type=TT_FIX_VALIDATION, objective="fix tests",
                        allowed_files=["src/main.py"])
    output = worker.process(packet, test_output="FAILED test_foo")
    assert output.status == WO_PROPOSED


def test_worker_processes_write_test():
    worker = LLMImplementationWorker()
    packet = TaskPacket(task_type=TT_WRITE_TEST, objective="write tests",
                        allowed_files=["src/parser.py"])
    output = worker.process(packet)
    assert output.status == WO_PROPOSED
    assert any("test_" in c.target_file for c in output.changes)


def test_worker_respects_forbidden_files():
    worker = LLMImplementationWorker()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix",
                        allowed_files=["a.py"], forbidden_files=["a.py"])
    output = worker.process(packet)
    assert output.status == WO_FAILED
    assert any("forbidden" in e.lower() for e in output.errors)


def test_worker_no_changes_for_empty_packet():
    worker = LLMImplementationWorker()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix")
    output = worker.process(packet)
    assert output is not None


def test_worker_handles_explain_failure():
    worker = LLMImplementationWorker()
    packet = TaskPacket(task_type=TT_EXPLAIN_FAILURE, objective="explain failure",
                        allowed_files=["src/main.py"])
    output = worker.process(packet)
    assert output.status in (WO_PROPOSED, WO_NEEDS_MORE_CONTEXT)


def test_worker_propagates_packet_errors():
    worker = LLMImplementationWorker()
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix")
    packet.errors.append("packet error")
    output = worker.process(packet)
    assert any("packet error" in e for e in output.errors)


def test_worker_with_custom_registry():
    from agentx_evolve.models.model_models import ModelRegistry
    registry = ModelRegistry()
    worker = LLMImplementationWorker(registry=registry)
    packet = TaskPacket(task_type=TT_IMPLEMENT_PATCH, objective="fix",
                        allowed_files=["a.py"])
    output = worker.process(packet)
    assert output is not None
