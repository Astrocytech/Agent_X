from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PolicyRequest:
    request_id: str = ""
    caller_role: str = ""
    tool_name: str = ""
    requested_effect: str = ""
    target: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
