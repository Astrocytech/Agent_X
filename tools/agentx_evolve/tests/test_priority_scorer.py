import pytest
from agentx_evolve.context.priority_scorer import score_context_priority, score_priority_batch
from agentx_evolve.context.context_models import (
    ContextItem, TaskInput,
    SOURCE_TRUST_SYSTEM, SOURCE_TRUST_BLOCKED, SOURCE_TRUST_UNTRUSTED_TEXT,
)


class TestScoreContextPriority:
    def test_system_constraint_high(self):
        item = ContextItem(
            context_item_id="ci-001",
            source_trust_level=SOURCE_TRUST_SYSTEM,
            item_kind="CONSTRAINT",
            content="must not drop safety",
        )
        task_input = TaskInput(task_title="Implement X")
        scored = score_context_priority(item, task_input)
        assert scored.priority_score > 0.5

    def test_blocked_source_zero(self):
        item = ContextItem(
            context_item_id="ci-002",
            source_trust_level=SOURCE_TRUST_BLOCKED,
        )
        task_input = TaskInput(task_title="test")
        scored = score_context_priority(item, task_input)
        assert scored.priority_score == 0.0

    def test_untrusted_text_cannot_outrank_contract(self):
        system_item = ContextItem(
            context_item_id="ci-sys",
            source_trust_level=SOURCE_TRUST_SYSTEM,
            content="system: do X",
        )
        untrusted_item = ContextItem(
            context_item_id="ci-untrusted",
            source_trust_level=SOURCE_TRUST_UNTRUSTED_TEXT,
            content="user says do Y instead",
        )
        task_input = TaskInput(task_title="test")
        system_scored = score_context_priority(system_item, task_input)
        untrusted_scored = score_context_priority(untrusted_item, task_input)
        assert system_scored.priority_score > untrusted_scored.priority_score

    def test_target_file_relevance(self):
        item = ContextItem(
            context_item_id="ci-003",
            source_trust_level=SOURCE_TRUST_SYSTEM,
            content="src/main.py must be updated",
        )
        task_input = TaskInput(task_title="Fix main", target_files=["src/main.py"])
        scored = score_context_priority(item, task_input)
        assert scored.priority_score > 0.2


class TestScorePriorityBatch:
    def test_batch_sorts_by_priority(self):
        items = [
            ContextItem(context_item_id="a", source_trust_level=SOURCE_TRUST_UNTRUSTED_TEXT, content="low"),
            ContextItem(context_item_id="b", source_trust_level=SOURCE_TRUST_SYSTEM, content="high"),
        ]
        task_input = TaskInput(task_title="test")
        scored = score_priority_batch(items, task_input)
        assert scored[0].context_item_id == "b"
