from __future__ import annotations

from enum import Enum
from typing import Any


class ReplayMode(str, Enum):
    DETERMINISTIC = "deterministic"
    RECORDED_REPLAY = "recorded_replay"
    LIVE_NON_REPLAYABLE = "live_non_replayable"
    BLOCKED_IN_REPLAY = "blocked_in_replay"


class ReplayPolicy:
    @staticmethod
    def allowed_mode(adapter_type: str, is_live: bool = False, is_mock: bool = True) -> ReplayMode:
        if is_mock:
            return ReplayMode.DETERMINISTIC
        if not is_live:
            return ReplayMode.RECORDED_REPLAY
        if is_live:
            return ReplayMode.LIVE_NON_REPLAYABLE
        return ReplayMode.BLOCKED_IN_REPLAY

    @staticmethod
    def can_replay(mode: ReplayMode, replay_artifact_missing: bool = False) -> bool:
        if mode == ReplayMode.DETERMINISTIC:
            return True
        if mode == ReplayMode.RECORDED_REPLAY:
            return not replay_artifact_missing
        return False
