from __future__ import annotations

from agentx_evolve.context_builder.context_packet import StructuralContext, FactualItem, ContextPacket


class ContextBuilder:
    def build(self, goal_type: str = "", task_type: str = "") -> ContextPacket:
        structural = StructuralContext(
            goal_type=goal_type,
            task_type=task_type,
            runtime_mode="offline",
            allowed_actions=["read_repo_info", "list_repo_files", "read_file_content"],
            forbidden_actions=["write_file", "execute_command", "network_call"],
            required_contracts=["adapter-mvp-contract"],
            required_validators=[],
            capability_boundaries=["read-only", "offline"],
            promotion_rules=["human review required"],
            tool_policy={"allow_read_only": True, "allow_write": False, "allow_network": False},
            model_policy={"mock_only": True, "deterministic": True},
        )
        return ContextPacket(structural=structural)

    def build_with_factual(self, goal_type: str, task_type: str,
                           factual_items: list[FactualItem] | None = None) -> ContextPacket:
        packet = self.build(goal_type=goal_type, task_type=task_type)
        if factual_items:
            for item in factual_items:
                packet.add_factual(item)
        return packet
