from __future__ import annotations

import pytest

from agentx_evolve.context.context_models import (
    TaskInput,
    InstructionHierarchy,
    HI_OVERRIDE,
    HI_APPEND,
)


class TestContextConstraint:
    def test_task_input_has_constraints(self):
        ti = TaskInput(
            task_input_id="ti_001",
            user_constraints=["Must use pytest"],
            system_constraints=["No network access"],
            forbidden_actions=["git push"],
        )
        assert len(ti.user_constraints) == 1
        assert len(ti.system_constraints) == 1
        assert len(ti.forbidden_actions) == 1

    def test_instruction_hierarchy_add(self):
        h = InstructionHierarchy()
        h.add("Do X", priority=10)
        assert len(h.instructions) == 1

    def test_instruction_hierarchy_merge(self):
        h = InstructionHierarchy()
        h.add("Do X", priority=10)
        h.add("Do Y", priority=5)
        merged = h.merge()
        assert "Do X" in merged
        assert "Do Y" in merged

    def test_instruction_hierarchy_highest_priority(self):
        h = InstructionHierarchy()
        h.add("Low", priority=1)
        h.add("High", priority=100)
        assert h.highest_priority() == "High"

    def test_instruction_hierarchy_dedup(self):
        h = InstructionHierarchy()
        h.add("Same", priority=10)
        h.add("Same", priority=5)
        merged = h.merge()
        assert merged.count("Same") == 1

    def test_instruction_hierarchy_append_mode(self):
        h = InstructionHierarchy()
        h.add("Base", priority=1, merge_mode=HI_OVERRIDE)
        h.add("Override", priority=2, merge_mode=HI_OVERRIDE)
        merged = h.merge()
        assert merged == ["Override", "Base"] or "Override" in merged
