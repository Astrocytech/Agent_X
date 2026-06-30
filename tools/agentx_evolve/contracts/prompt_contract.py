from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PromptContract:
    contract_id: str
    version: str = "1.0.0"
    purpose: str = ""
    allowed_goal_types: list[str] = field(default_factory=list)
    required_context_fields: list[str] = field(default_factory=list)
    forbidden_context_fields: list[str] = field(default_factory=list)
    allowed_output_schema: dict[str, Any] = field(default_factory=dict)
    forbidden_claims: list[str] = field(default_factory=list)
    allowed_action_proposals: list[str] = field(default_factory=list)
    allowed_tool_proposals: list[str] = field(default_factory=list)
    refusal_format: str = ""
    blocked_format: str = ""
    evidence_requirements: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "version": self.version,
            "purpose": self.purpose,
            "allowed_goal_types": self.allowed_goal_types,
            "required_context_fields": self.required_context_fields,
            "forbidden_context_fields": self.forbidden_context_fields,
            "allowed_output_schema": self.allowed_output_schema,
            "forbidden_claims": self.forbidden_claims,
            "allowed_action_proposals": self.allowed_action_proposals,
            "allowed_tool_proposals": self.allowed_tool_proposals,
            "refusal_format": self.refusal_format,
            "blocked_format": self.blocked_format,
            "evidence_requirements": self.evidence_requirements,
        }

    def matches_goal_type(self, goal_type: str) -> bool:
        return not self.allowed_goal_types or goal_type in self.allowed_goal_types
