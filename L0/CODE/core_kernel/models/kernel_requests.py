"""Deprecated — use KernelTurnRequestV1 from core_kernel.contracts.kernel_turn_request_v1 instead."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class KernelTurnRequest:
    """Deprecated: use KernelTurnRequestV1 (goal-based) from kernel_turn_request_v1."""
    user_input: str
    session_id: str
    profile_id: str = "generalist"
    context: dict[str, Any] = field(default_factory=dict)
