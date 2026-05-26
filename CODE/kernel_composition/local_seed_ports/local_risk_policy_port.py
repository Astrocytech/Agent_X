"""LocalRiskPolicyPort — assesses tool risk, denies unknown tools by default."""

from __future__ import annotations

import json
from typing import Any

from core_kernel.contracts.governance_contracts import RiskAssessment


_KNOWN_LOW_RISK_TOOLS = {"seed.emit_answer"}


class LocalRiskPolicyPort:
    runtime_safety_class = "production_seed_port"

    def assess(
        self, tool_name: str, args: dict[str, Any], context: dict[str, Any]
    ) -> RiskAssessment:
        tool_args_hash = str(hash(json.dumps(args, sort_keys=True)))
        if tool_name in _KNOWN_LOW_RISK_TOOLS:
            return RiskAssessment(
                tool_name=tool_name,
                tool_args_hash=tool_args_hash,
                risk_level="low",
                approval_required=False,
                matched_rules=(),
                protected_path_touched=False,
            )
        return RiskAssessment(
            tool_name=tool_name,
            tool_args_hash=tool_args_hash,
            risk_level="high",
            approval_required=True,
            matched_rules=(),
            protected_path_touched=False,
            reason=f"Unknown tool '{tool_name}' — denied by default",
        )
