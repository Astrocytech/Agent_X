import pytest
from agentx_evolve.scheduler.scheduler_state import (
    SchedulerState, migrate_state, S_CREATED, S_RUNNING, S_COMPLETED
)


def test_state_transitions_are_valid():
    state = SchedulerState(S_CREATED)
    state.transition_to(S_RUNNING)
    assert state.state == S_RUNNING
    state.transition_to(S_COMPLETED)
    assert state.state == S_COMPLETED


def test_invalid_transitions_raise():
    state = SchedulerState(S_CREATED)
    with pytest.raises(ValueError, match="Cannot transition from CREATED to COMPLETED"):
        state.transition_to(S_COMPLETED)


def test_migrate_state_valid():
    result = migrate_state(S_CREATED, S_RUNNING)
    assert result == S_RUNNING


def test_migrate_state_invalid():
    with pytest.raises(ValueError, match="Cannot migrate from CREATED to COMPLETED"):
        migrate_state(S_CREATED, S_COMPLETED)


def test_state_default_created():
    state = SchedulerState()
    assert state.state == S_CREATED
