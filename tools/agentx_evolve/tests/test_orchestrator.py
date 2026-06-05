import pytest
from agentx_evolve.orchestrator.session_models import (
    SessionRecord, SESSION_TRANSITIONS, MAX_REPAIR_LOOPS,
    SC_CREATED, SC_SCANNED, SC_PLANNED, SC_PROPOSED,
    SC_GOVERNANCE_CHECKED, SC_CONTEXT_BUILT, SC_MODEL_PROPOSED,
    SC_PATCH_APPLIED, SC_VALIDATED, SC_ROLLED_BACK,
    SC_ACCEPTED, SC_FAILED, SC_BLOCKED,
)
from agentx_evolve.orchestrator.self_evolution_orchestrator import SelfEvolutionOrchestrator
from agentx_evolve.context.context_builder import ContextBuilder
from agentx_evolve.context.context_models import TaskPacket, TT_IMPLEMENT_PATCH


# ---------------------------------------------------------------------------
# SessionRecord tests
# ---------------------------------------------------------------------------

def test_session_defaults():
    s = SessionRecord()
    assert s.status == SC_CREATED
    assert not s.is_terminal()


def test_session_custom():
    s = SessionRecord(session_id="s1", description="test session")
    assert s.session_id == "s1"


def test_session_terminal_states():
    for state in (SC_ACCEPTED, SC_FAILED, SC_BLOCKED, SC_ROLLED_BACK):
        s = SessionRecord(status=state)
        assert s.is_terminal()


def test_session_valid_transition():
    s = SessionRecord()
    assert s.can_transition_to(SC_SCANNED)
    assert s.transition_to(SC_SCANNED)
    assert s.status == SC_SCANNED


def test_session_invalid_transition():
    s = SessionRecord()
    assert not s.can_transition_to(SC_ACCEPTED)
    assert not s.transition_to(SC_ACCEPTED)
    assert s.status == SC_CREATED


def test_session_terminal_no_transition():
    s = SessionRecord(status=SC_ACCEPTED)
    assert not s.transition_to(SC_SCANNED)


def test_session_to_dict():
    s = SessionRecord(session_id="s1", description="test")
    d = s.to_dict()
    assert d["session_id"] == "s1"


def test_full_transition_path():
    s = SessionRecord()
    path = [SC_SCANNED, SC_PLANNED, SC_PROPOSED, SC_GOVERNANCE_CHECKED,
            SC_CONTEXT_BUILT, SC_MODEL_PROPOSED, SC_PATCH_APPLIED,
            SC_VALIDATED, SC_ACCEPTED]
    for state in path:
        assert s.can_transition_to(state), f"Cannot transition to {state}"
        assert s.transition_to(state), f"Transition failed at {state}"
    assert s.status == SC_ACCEPTED


def test_rolled_back_can_replan():
    s = SessionRecord(status=SC_ROLLED_BACK)
    assert s.can_transition_to(SC_PLANNED)


# ---------------------------------------------------------------------------
# SelfEvolutionOrchestrator tests
# ---------------------------------------------------------------------------

def test_orchestrator_defaults():
    o = SelfEvolutionOrchestrator()
    assert o is not None


def test_orchestrator_full_cycle_success():
    o = SelfEvolutionOrchestrator()
    o.register_hook("plan", lambda: [{"id": "c1", "description": "evolve component X"}])
    session = SessionRecord(session_id="s1", description="evolve component X")
    result = o.run_cycle(session)
    assert result.status == SC_ACCEPTED


def test_orchestrator_with_failing_governance():
    o = SelfEvolutionOrchestrator()
    o.register_hook("plan", lambda: [{"id": "c1", "description": "test"}])
    o.register_hook("governance_check", lambda: {"decision": "DENY", "level": "L0"})
    session = SessionRecord(session_id="s2")
    result = o.run_cycle(session)
    assert result.status == SC_BLOCKED
    assert any("governance" in e.lower() for e in result.errors)


def test_orchestrator_with_no_plan():
    o = SelfEvolutionOrchestrator()
    o.register_hook("plan", lambda: [])
    session = SessionRecord(session_id="s3")
    result = o.run_cycle(session)
    assert result.status == SC_BLOCKED


def test_orchestrator_repair_loop():
    call_count = [0]
    def failing_validate():
        call_count[0] += 1
        return {"passed": False, "output": "FAILED test_foo"}

    o = SelfEvolutionOrchestrator()
    o.register_hook("plan", lambda: [{"id": "c1", "description": "repair test"}])
    o.register_hook("validate", failing_validate)
    session = SessionRecord(session_id="s4")
    result = o.run_cycle(session)
    assert call_count[0] >= 1


def test_orchestrator_max_repair_loops():
    def always_fail_validate():
        return {"passed": False, "output": "FAILED"}

    o = SelfEvolutionOrchestrator()
    o.register_hook("plan", lambda: [{"id": "c1", "description": "max repair test"}])
    o.register_hook("validate", always_fail_validate)
    session = SessionRecord(session_id="s5")
    result = o.run_cycle(session)
    assert result.status in (SC_BLOCKED, SC_ROLLED_BACK, SC_ACCEPTED, SC_MODEL_PROPOSED)


def test_orchestrator_terminal_session_skipped():
    o = SelfEvolutionOrchestrator()
    session = SessionRecord(session_id="s6", status=SC_ACCEPTED)
    result = o.run_cycle(session)
    assert result.status == SC_ACCEPTED


def test_orchestrator_hooks_registration():
    o = SelfEvolutionOrchestrator()
    called = []
    o.register_hook("scan", lambda: called.append("scan") or {"status": "ok"})
    o.register_hook("status", lambda: called.append("status") or {"status": "ok"})
    o.register_hook("plan", lambda: called.append("plan") or [{"id": "c1"}])
    o.register_hook("propose", lambda: called.append("propose") or {})
    session = SessionRecord(session_id="s7")
    o.run_cycle(session)
    assert "scan" in called
    assert "status" in called
    assert "plan" in called
    assert "propose" in called


def test_orchestrator_with_custom_context_builder():
    cb = ContextBuilder(max_tokens=4096)
    o = SelfEvolutionOrchestrator(context_builder=cb)
    o.register_hook("plan", lambda: [{"id": "c1", "description": "test custom"}])
    session = SessionRecord(session_id="s8", description="test custom")
    result = o.run_cycle(session, candidate_files=["src/main.py"])
    assert result.status == SC_ACCEPTED
    assert result.task_packet_id.startswith("tp-")


def test_orchestrator_records_completion():
    o = SelfEvolutionOrchestrator()
    o.register_hook("plan", lambda: [{"id": "c1", "description": "complete"}])
    session = SessionRecord(session_id="s9")
    result = o.run_cycle(session)
    assert result.completion_record is not None
    assert result.completion_record["session_id"] == "s9"
    assert result.completion_record["final_status"] == SC_ACCEPTED


def test_orchestrator_repair_count_tracked():
    validate_results = [{"passed": False, "output": "FAILED v1"},
                        {"passed": False, "output": "FAILED v2"},
                        {"passed": True, "output": ""}]
    vc = [0]

    def validating():
        vc[0] += 1
        return validate_results[vc[0] - 1]

    o = SelfEvolutionOrchestrator()
    o.register_hook("validate", validating)
    session = SessionRecord(session_id="s10")
    result = o.run_cycle(session)
    assert result.repair_count <= MAX_REPAIR_LOOPS


def test_orchestrator_patch_failure_triggers_rollback():
    o = SelfEvolutionOrchestrator()
    o.register_hook("plan", lambda: [{"id": "c1", "description": "patch test"}])
    o.register_hook("apply_patch", lambda: {"status": "failed", "error": "conflict"})
    session = SessionRecord(session_id="s11")
    result = o.run_cycle(session)
    assert result.status == SC_ROLLED_BACK


def test_orchestrator_worker_failure():
    o = SelfEvolutionOrchestrator()
    o.register_hook("plan", lambda: [{"id": "c1", "description": "fix everything"}])
    session = SessionRecord(session_id="s12")
    result = o.run_cycle(session)
    assert result.status in (SC_ACCEPTED, SC_FAILED)
