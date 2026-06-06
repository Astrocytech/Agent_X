import pytest
from agentx_evolve.context.context_models import InstructionHierarchy, HI_OVERRIDE, HI_APPEND


class TestInstructionHierarchyConstants:
    def test_hi_override_value(self):
        assert HI_OVERRIDE == "OVERRIDE"

    def test_hi_append_value(self):
        assert HI_APPEND == "APPEND"


class TestInstructionHierarchy:
    def test_empty_hierarchy(self):
        h = InstructionHierarchy()
        assert h.instructions == []
        assert h.highest_priority() is None

    def test_higher_priority_overrides_lower(self):
        h = InstructionHierarchy()
        h.add("low instruction", priority=1)
        h.add("high instruction", priority=10)
        assert h.highest_priority() == "high instruction"

    def test_instructions_merge_by_priority(self):
        h = InstructionHierarchy()
        h.add("first", priority=5)
        h.add("second", priority=10)
        h.add("third", priority=1)
        merged = h.merge()
        assert merged[0] == "second"
        assert merged[1] == "first"
        assert merged[2] == "third"

    def test_merge_deduplicates(self):
        h = InstructionHierarchy()
        h.add("duplicate", priority=10)
        h.add("duplicate", priority=5)
        merged = h.merge()
        assert merged == ["duplicate"]

    def test_append_mode(self):
        h = InstructionHierarchy()
        h.add("instr_a", priority=5, merge_mode=HI_APPEND)
        h.add("instr_b", priority=10, merge_mode=HI_OVERRIDE)
        assert len(h.instructions) == 2
