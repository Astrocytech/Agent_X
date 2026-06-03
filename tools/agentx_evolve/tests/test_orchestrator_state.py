import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.orchestrator_state import (
    can_transition,
    is_terminal,
    transition_state,
    create_initial_state,
    write_state_snapshot,
    load_state_snapshot,
)
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationState,
)
from pathlib import Path

from agentx_evolve.orchestrator.orchestrator_config import (
    ORCH_STATUS_CREATED,
    ORCH_STATUS_PLANNING,
    ORCH_STATUS_PLAN_READY,
    ORCH_STATUS_RUNNING,
    ORCH_STATUS_VALIDATING,
    ORCH_STATUS_READY_FOR_PROMOTION,
    ORCH_STATUS_COMPLETED,
    ORCH_STATUS_FAILED,
    ORCH_STATUS_ABORTED,
    ORCH_STATUS_STEP_BLOCKED,
    ORCH_TERMINAL_STATUSES,
    RUNTIME_ARTIFACT_ROOT,
)


class TestCanTransition:
    def test_created_can_transition_to_planning(self):
        assert can_transition(ORCH_STATUS_CREATED, ORCH_STATUS_PLANNING) is True

    def test_planning_can_transition_to_plan_ready(self):
        assert can_transition(ORCH_STATUS_PLANNING, ORCH_STATUS_PLAN_READY) is True

    def test_running_can_transition_to_validating(self):
        assert can_transition(ORCH_STATUS_RUNNING, ORCH_STATUS_VALIDATING) is True

    def test_terminal_state_cannot_transition(self):
        for terminal in ORCH_TERMINAL_STATUSES:
            assert can_transition(terminal, ORCH_STATUS_PLANNING) is False


class TestIsTerminal:
    def test_terminal_states_return_true(self):
        for state in ORCH_TERMINAL_STATUSES:
            assert is_terminal(state) is True

    def test_non_terminal_states_return_false(self):
        assert is_terminal(ORCH_STATUS_CREATED) is False
        assert is_terminal(ORCH_STATUS_RUNNING) is False


class TestTransitionState:
    def test_valid_transition_updates_state(self):
        st = OrchestrationState(current_state=ORCH_STATUS_CREATED)
        result = transition_state(st, ORCH_STATUS_PLANNING, reason="starting plan")
        assert result.current_state == ORCH_STATUS_PLANNING
        assert result.previous_state == ORCH_STATUS_CREATED
        assert result.reason == "starting plan"
        assert result.terminal is False

    def test_invalid_transition_raises_error(self):
        st = OrchestrationState(current_state=ORCH_STATUS_CREATED)
        try:
            transition_state(st, ORCH_STATUS_COMPLETED)
            assert False, "Expected ValueError"
        except ValueError:
            pass

    def test_terminal_state_raises_error(self):
        st = OrchestrationState(current_state=ORCH_STATUS_COMPLETED)
        try:
            transition_state(st, ORCH_STATUS_PLANNING)
            assert False, "Expected ValueError"
        except ValueError:
            pass

    def test_version_increments_on_transition(self):
        st = OrchestrationState(current_state=ORCH_STATUS_CREATED, state_version=1)
        result = transition_state(st, ORCH_STATUS_PLANNING)
        assert result.state_version == 2

    def test_transition_to_terminal_sets_terminal_flag(self):
        st = OrchestrationState(current_state=ORCH_STATUS_CREATED)
        result = transition_state(st, ORCH_STATUS_PLANNING)
        result2 = transition_state(result, ORCH_STATUS_PLAN_READY)
        result3 = transition_state(result2, ORCH_STATUS_RUNNING)
        result4 = transition_state(result3, ORCH_STATUS_VALIDATING)
        result5 = transition_state(result4, ORCH_STATUS_READY_FOR_PROMOTION)
        result6 = transition_state(result5, ORCH_STATUS_COMPLETED)
        assert result6.terminal is True
        assert result6.current_state == ORCH_STATUS_COMPLETED


class TestCreateInitialState:
    def test_create_initial_state(self):
        st = create_initial_state(session_id="sess-1", run_id="run-1")
        assert st.session_id == "sess-1"
        assert st.run_id == "run-1"
        assert st.current_state == ORCH_STATUS_CREATED
        assert st.terminal is False
        assert st.state_version == 1
        assert st.reason == "Session created"
        assert st.previous_state == ""


class TestStateSnapshot:
    def test_write_and_load_state_snapshot(self, tmp_path):
        st = create_initial_state(session_id="sess-2", run_id="run-2")
        result = write_state_snapshot(st, tmp_path)
        assert "path" in result
        assert "sha256" in result
        assert isinstance(result["sha256"], str)
        assert len(result["sha256"]) == 64

        loaded = load_state_snapshot("run-2", tmp_path)
        assert loaded is not None
        assert loaded.session_id == "sess-2"
        assert loaded.run_id == "run-2"
        assert loaded.current_state == ORCH_STATUS_CREATED

    def test_load_state_snapshot_returns_none_for_missing(self):
        result = load_state_snapshot("nonexistent", Path("/tmp"))
        assert result is None

    def test_state_version_increments_on_transition(self):
        st = create_initial_state(session_id="sess-3", run_id="run-3")
        assert st.state_version == 1
        transition_state(st, ORCH_STATUS_PLANNING)
        assert st.state_version == 2
        transition_state(st, ORCH_STATUS_PLAN_READY)
        assert st.state_version == 3
