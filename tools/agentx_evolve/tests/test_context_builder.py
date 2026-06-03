import pytest
from agentx_evolve.context.context_models import (
    TaskPacket, TaskPacketBuilder, Snippet, ArtifactRef, ValidationPlan,
    TT_IMPLEMENT_PATCH, TT_FIX_VALIDATION, TT_WRITE_TEST, TT_EXPLAIN_FAILURE,
    ALL_TASK_TYPES,
)
from agentx_evolve.context.context_source_loader import (
    select_files, select_artifacts,
    FileMatch, FileSelectionResult, ArtifactMatch, ArtifactSelectionResult,
)
from agentx_evolve.context.task_pack_builder import inject_schema, list_available_schemas
from agentx_evolve.context.validation_error_summarizer import (
    summarize_test_output, ValidationErrorEntry, ValidationErrorSummary,
)
from agentx_evolve.context.budget_estimator import estimate_context_item_budget, estimate_context_pack_budget
from agentx_evolve.context.context_models import ContextItem
from agentx_evolve.context.context_builder import ContextBuilder


# ---------------------------------------------------------------------------
# TaskPacket tests
# ---------------------------------------------------------------------------

def test_task_packet_defaults():
    p = TaskPacket()
    assert p.schema_version == "1.0"
    assert p.task_type == TT_IMPLEMENT_PATCH
    assert p.warnings == []
    assert p.errors == []


def test_task_packet_custom():
    p = TaskPacket(task_type=TT_WRITE_TEST, objective="write tests", token_budget=4096)
    assert p.task_type == TT_WRITE_TEST
    assert p.objective == "write tests"


def test_task_packet_token_headroom():
    p = TaskPacket(token_budget=100, token_used=30)
    assert p.token_headroom() == 70


def test_task_packet_within_budget():
    p = TaskPacket(token_budget=100, token_used=80)
    assert p.is_within_budget()


def test_task_packet_over_budget():
    p = TaskPacket(token_budget=100, token_used=120)
    assert not p.is_within_budget()


def test_task_packet_to_dict():
    p = TaskPacket(task_packet_id="tp-abc", objective="test")
    d = p.to_dict()
    assert d["task_packet_id"] == "tp-abc"
    assert d["objective"] == "test"


# ---------------------------------------------------------------------------
# TaskPacketBuilder tests
# ---------------------------------------------------------------------------

def test_builder_builds_minimal():
    b = TaskPacketBuilder()
    p = b.with_objective("do thing").build()
    assert p.objective == "do thing"
    assert p.task_packet_id.startswith("tp-")


def test_builder_with_task_type():
    b = TaskPacketBuilder()
    p = b.with_task_type(TT_FIX_VALIDATION).with_objective("fix").build()
    assert p.task_type == TT_FIX_VALIDATION


def test_builder_with_unknown_task_type():
    b = TaskPacketBuilder()
    b.with_task_type("UNKNOWN")
    assert any("Unknown task type" in e for e in b._packet.errors)


def test_builder_chain():
    b = TaskPacketBuilder()
    b.with_task_type(TT_WRITE_TEST).with_objective("write").with_token_budget(2048)
    b.with_allowed_files(["a.py", "b.py"])
    b.with_forbidden_files(["secret.py"])
    b.with_constraints(["no network"])
    p = b.build()
    assert p.token_budget == 2048
    assert p.allowed_files == ["a.py", "b.py"]
    assert p.forbidden_files == ["secret.py"]
    assert "no network" in p.constraints


def test_builder_warns_no_objective():
    b = TaskPacketBuilder()
    p = b.build()
    assert "Task packet has no objective" in p.warnings


def test_builder_with_governance():
    b = TaskPacketBuilder()
    p = b.with_objective("x").with_governance_result({"decision": "ALLOW"}).build()
    assert p.governance_result == {"decision": "ALLOW"}


def test_builder_with_validation_plan():
    b = TaskPacketBuilder()
    plan = ValidationPlan(run_tests=True, expected_files=["a.py"])
    p = b.with_objective("x").with_validation_plan(plan).build()
    assert p.validation_plan is not None
    assert p.validation_plan.run_tests


# ---------------------------------------------------------------------------
# Snippet tests
# ---------------------------------------------------------------------------

def test_snippet_defaults():
    s = Snippet()
    assert s.content == ""
    assert s.relevance_score == 1.0


def test_snippet_custom():
    s = Snippet(file_path="a.py", content="print(1)", language="python")
    assert s.file_path == "a.py"


# ---------------------------------------------------------------------------
# ArtifactRef tests
# ---------------------------------------------------------------------------

def test_artifact_ref():
    a = ArtifactRef(artifact_id="a1", artifact_type="test_output", description="test results")
    assert a.artifact_id == "a1"


# ---------------------------------------------------------------------------
# ValidationPlan tests
# ---------------------------------------------------------------------------

def test_validation_plan_defaults():
    v = ValidationPlan()
    assert v.run_tests


def test_validation_plan_to_dict():
    v = ValidationPlan(run_tests=False)
    d = v.to_dict()
    assert d["run_tests"] is False


# ---------------------------------------------------------------------------
# File selection tests
# ---------------------------------------------------------------------------

def test_file_selector_defaults():
    result = select_files("fix bug in parser", "IMPLEMENT_PATCH",
                          candidate_files=["src/parser.py", "src/main.py", "tests/test_parser.py"])
    assert len(result.allowed) == 3
    assert "src/parser.py" in result.allowed


def test_file_selector_scoring():
    result = select_files("parser bug", "IMPLEMENT_PATCH",
                          candidate_files=["src/parser.py", "README.md"])
    matches = {m.file_path: m.relevance_score for m in result.matches}
    assert matches.get("src/parser.py", 0) > matches.get("README.md", 0)


def test_file_selector_empty():
    result = select_files("task", "IMPLEMENT_PATCH")
    assert result.allowed == []
    assert result.token_estimate == 0


def test_file_selector_test_task():
    result = select_files("write unit tests", "WRITE_TEST",
                          candidate_files=["src/main.py", "tests/test_main.py"])
    matches = {m.file_path: m.relevance_score for m in result.matches}
    assert matches.get("tests/test_main.py", 0) > matches.get("src/main.py", 0)


# ---------------------------------------------------------------------------
# Artifact selection tests
# ---------------------------------------------------------------------------

def test_artifact_selector_selects_relevant():
    available = [
        {"artifact_id": "a1", "artifact_type": "test_output", "description": "parser test results"},
        {"artifact_id": "a2", "artifact_type": "log", "description": "server log"},
    ]
    result = select_artifacts("FIX_VALIDATION", "fix parser test results", available)
    ids = [m.artifact_id for m in result.selected]
    assert "a1" in ids


def test_artifact_selector_no_match():
    available = [
        {"artifact_id": "a1", "artifact_type": "log", "description": "server log"},
    ]
    result = select_artifacts("FIX_VALIDATION", "fix parser test", available)
    assert len(result.selected) == 0


# ---------------------------------------------------------------------------
# ContextBudgeter tests
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Budget estimator tests (replaces old ContextBudgeter tests)
# ---------------------------------------------------------------------------

def test_budget_estimator_short_vs_long():
    short = estimate_context_item_budget(ContextItem(source_id="s", content="hello"))
    long_t = estimate_context_item_budget(ContextItem(source_id="s", content="x" * 1000))
    assert long_t["token_estimate"] > short["token_estimate"]


def test_budget_estimator_reserved_output():
    items: list = []
    budget = estimate_context_pack_budget(items, max_context_tokens=1000, reserved_output_tokens=200)
    assert budget["available_input_tokens"] == 800


def test_budget_estimator_over_budget_flagged():
    items = [ContextItem(source_id="s", content="x" * 5000)]
    budget = estimate_context_pack_budget(items, max_context_tokens=10, reserved_output_tokens=0)
    assert budget["total_estimated_tokens"] > 10


# ---------------------------------------------------------------------------
# Schema injection tests
# ---------------------------------------------------------------------------

def test_schema_injector():
    schemas = {"IMPLEMENT_PATCH": {"type": "object", "required": ["patch"]}}
    result = inject_schema("IMPLEMENT_PATCH", schemas)
    assert result == {"type": "object", "required": ["patch"]}


def test_schema_injector_none():
    assert inject_schema("IMPLEMENT_PATCH") is None


def test_schema_injector_missing():
    schemas = {"WRITE_TEST": {}}
    assert inject_schema("IMPLEMENT_PATCH", schemas) is None


def test_schema_list_available():
    schemas = {"a": {}, "b": {}}
    assert sorted(list_available_schemas(schemas)) == ["a", "b"]


# ---------------------------------------------------------------------------
# Validation error summarizer tests
# ---------------------------------------------------------------------------

def test_summarizer_empty():
    s = summarize_test_output("")
    assert s.total_errors == 0
    assert s.total_failures == 0


def test_summarizer_no_errors():
    s = summarize_test_output("All tests passed!")
    assert s.total_errors == 0
    assert s.total_failures == 0


def test_summarizer_with_errors():
    s = summarize_test_output("FAILED test_foo\nERROR test_bar\nSome output\nFAILED test_baz")
    assert s.total_failures == 2
    assert s.total_errors == 1


def test_summarizer_truncates():
    lines = "\n".join([f"FAILED test_{i}" for i in range(50)])
    s = summarize_test_output(lines)
    assert len(s.entries) <= 20
    assert "Truncated" in s.warnings[0]


def test_validation_error_entry():
    e = ValidationErrorEntry(test_name="test_foo", error_message="assert failed", file="a.py", line=10)
    d = e.to_dict()
    assert d["test_name"] == "test_foo"


def test_validation_error_summary_to_dict():
    s = ValidationErrorSummary(total_errors=2, total_failures=1, summary_text="2 errors, 1 failure")
    d = s.to_dict()
    assert d["total_errors"] == 2


# ---------------------------------------------------------------------------
# ContextBuilder integration tests
# ---------------------------------------------------------------------------

def test_context_builder_defaults():
    cb = ContextBuilder()
    assert cb.budgeter["max_tokens"] == 8192


def test_context_builder_build_minimal():
    cb = ContextBuilder()
    packet = cb.build_packet(task_type=TT_IMPLEMENT_PATCH, objective="fix the bug")
    assert packet.task_type == TT_IMPLEMENT_PATCH
    assert packet.objective == "fix the bug"
    assert packet.task_packet_id.startswith("tp-")


def test_context_builder_with_files():
    cb = ContextBuilder()
    packet = cb.build_packet(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix parser",
        candidate_files=["src/parser.py", "src/main.py"],
    )
    assert "src/parser.py" in packet.allowed_files
    assert packet.source_snippets is not None


def test_context_builder_with_artifacts():
    cb = ContextBuilder()
    artifacts = [
        {"artifact_id": "a1", "artifact_type": "test_output", "description": "parser test failed"},
    ]
    packet = cb.build_packet(
        task_type=TT_FIX_VALIDATION,
        objective="fix parser test",
        candidate_files=["src/parser.py"],
        available_artifacts=artifacts,
    )
    assert len(packet.relevant_artifacts) == 1


def test_context_builder_with_schema():
    cb = ContextBuilder()
    schemas = {"IMPLEMENT_PATCH": {"type": "object"}}
    packet = cb.build_packet(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix",
        schemas=schemas,
    )
    assert packet.output_schema == {"type": "object"}


def test_context_builder_with_constraints():
    cb = ContextBuilder()
    packet = cb.build_packet(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix",
        constraints=["no network access", "forbidden: write to /etc"],
    )
    assert "no network access" in packet.constraints


def test_context_builder_with_governance():
    cb = ContextBuilder()
    packet = cb.build_packet(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix",
        governance_result={"decision": "ALLOW", "level": "L1"},
    )
    assert packet.governance_result["decision"] == "ALLOW"


def test_context_builder_with_risk():
    cb = ContextBuilder()
    packet = cb.build_packet(
        task_type=TT_IMPLEMENT_PATCH,
        objective="fix",
        risk_assessment={"level": "low"},
    )
    assert packet.risk_assessment == {"level": "low"}


def test_context_builder_with_test_output():
    cb = ContextBuilder()
    packet = cb.build_packet(
        task_type=TT_FIX_VALIDATION,
        objective="fix tests",
        test_output="FAILED test_parser\nERROR test_utils",
    )
    ids = [a.artifact_id for a in packet.relevant_artifacts]
    assert "validation-errors" in ids


def test_context_builder_token_tracking():
    cb = ContextBuilder(max_tokens=100)
    packet = cb.build_packet(
        task_type=TT_IMPLEMENT_PATCH,
        objective="x",
        candidate_files=["very_long_file_" + "x" * 200],
    )
    assert packet.token_used > 0


def test_context_builder_over_budget_warning():
    cb = ContextBuilder(max_tokens=1)
    packet = cb.build_packet(
        task_type=TT_IMPLEMENT_PATCH,
        objective="x" * 100,
        candidate_files=["x" * 100],
    )
    assert any("budget" in w.lower() for w in packet.warnings)
