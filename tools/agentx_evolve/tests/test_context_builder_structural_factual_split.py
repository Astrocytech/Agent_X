from __future__ import annotations

import pytest
from agentx_evolve.context_builder.context_builder import ContextBuilder
from agentx_evolve.context_builder.context_packet import FactualItem, ContextPacket


class TestContextBuilderStructuralFactualSplit:
    def setup_method(self):
        self.builder = ContextBuilder()

    def test_structural_factual_fields_separated(self):
        packet = self.builder.build(goal_type="repo_summary", task_type="read_only")
        d = packet.to_dict()
        assert "structural" in d
        assert "factual" in d

    def test_structural_has_goal_type(self):
        packet = self.builder.build(goal_type="repo_summary")
        assert packet.structural.goal_type == "repo_summary"

    def test_structural_has_forbidden_actions(self):
        packet = self.builder.build()
        assert "write_file" in packet.structural.forbidden_actions

    def test_factual_item_without_provenance_rejected(self):
        packet = self.builder.build()
        item = FactualItem(content="test content")
        with pytest.raises(ValueError, match="provenance"):
            packet.add_factual(item)

    def test_factual_item_with_provenance_accepted(self):
        packet = self.builder.build()
        item = FactualItem(
            content="repo has 10 files",
            provenance={"source": "tool", "tool_name": "read_repo_info"},
        )
        packet.add_factual(item)
        assert len(packet.factual) == 1
        assert packet.factual[0].content_hash

    def test_context_packet_hash_stable(self):
        p1 = self.builder.build(goal_type="test")
        p2 = self.builder.build(goal_type="test")
        assert p1.packet_hash == p2.packet_hash

    def test_context_packet_hash_changes_with_content(self):
        p1 = self.builder.build(goal_type="test1")
        p2 = self.builder.build(goal_type="test2")
        assert p1.packet_hash != p2.packet_hash

    def test_context_packet_is_replayable(self):
        packet = self.builder.build()
        assert packet.is_replayable() is True
