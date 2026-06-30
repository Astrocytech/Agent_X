from __future__ import annotations

import pytest
from agentx_evolve.adapters.replay_policy import ReplayMode, ReplayPolicy


class TestReplayPolicy:
    def test_deterministic_mode_allows_replay(self):
        assert ReplayPolicy.can_replay(ReplayMode.DETERMINISTIC) is True

    def test_recorded_replay_allows_replay_when_artifact_present(self):
        assert ReplayPolicy.can_replay(ReplayMode.RECORDED_REPLAY, replay_artifact_missing=False) is True

    def test_recorded_replay_blocks_replay_when_artifact_missing(self):
        assert ReplayPolicy.can_replay(ReplayMode.RECORDED_REPLAY, replay_artifact_missing=True) is False

    def test_live_non_replayable_blocks_replay(self):
        assert ReplayPolicy.can_replay(ReplayMode.LIVE_NON_REPLAYABLE) is False

    def test_blocked_in_replay_blocks_replay(self):
        assert ReplayPolicy.can_replay(ReplayMode.BLOCKED_IN_REPLAY) is False

    def test_allowed_mode_mock_returns_deterministic(self):
        mode = ReplayPolicy.allowed_mode("model", is_live=False, is_mock=True)
        assert mode == ReplayMode.DETERMINISTIC

    def test_allowed_mode_non_live_returns_recorded_replay(self):
        mode = ReplayPolicy.allowed_mode("tool", is_live=False, is_mock=False)
        assert mode == ReplayMode.RECORDED_REPLAY

    def test_allowed_mode_live_returns_live_non_replayable(self):
        mode = ReplayPolicy.allowed_mode("tool", is_live=True, is_mock=False)
        assert mode == ReplayMode.LIVE_NON_REPLAYABLE

    def test_deterministic_mode_is_deterministic(self):
        assert ReplayMode.DETERMINISTIC.value == "deterministic"

    def test_all_replay_modes_have_values(self):
        for mode in ReplayMode:
            assert mode.value
