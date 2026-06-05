import pytest
from agentx_evolve.context.context_models import (
    ContextSource, TaskInput, ContextItem, ContextPack, TaskPack,
    utc_now_iso, new_id, stable_hash, estimate_tokens_rough, to_dict,
    SOURCE_TRUST_SYSTEM, SOURCE_TRUST_BLOCKED,
    ITEM_KIND_CONSTRAINT, ITEM_KIND_FILE_SNIPPET,
    INCLUDE, EXCLUDE_DUPLICATE,
    COMPATIBLE, INCOMPATIBLE_OVER_CONTEXT_WINDOW,
)


class TestHelpers:
    def test_utc_now_iso(self):
        val = utc_now_iso()
        assert isinstance(val, str)
        assert "T" in val

    def test_new_id(self):
        val = new_id("ctx")
        assert val.startswith("ctx-")
        assert len(val) > 10

    def test_stable_hash_string(self):
        h1 = stable_hash("hello")
        h2 = stable_hash("hello")
        assert h1 == h2
        assert len(h1) == 64

    def test_stable_hash_dict(self):
        h1 = stable_hash({"a": 1, "b": 2})
        h2 = stable_hash({"b": 2, "a": 1})
        assert h1 == h2

    def test_stable_hash_list(self):
        h1 = stable_hash([1, 2, 3])
        h2 = stable_hash([1, 2, 3])
        assert h1 == h2

    def test_estimate_tokens_rough_empty(self):
        assert estimate_tokens_rough("") == 0

    def test_estimate_tokens_rough_text(self):
        count = estimate_tokens_rough("hello world")
        assert count > 0

    def test_estimate_tokens_rough_long(self):
        short = estimate_tokens_rough("short")
        long_ = estimate_tokens_rough("a " * 1000)
        assert long_ > short


class TestContextSource:
    def test_defaults(self):
        s = ContextSource()
        assert s.schema_version == "1.0"
        assert s.schema_id == "context_source.schema.json"
        assert s.allowed_by_policy is False

    def test_custom(self):
        s = ContextSource(
            source_id="src1",
            source_type="IMPLEMENTATION_SPEC",
            source_trust_level=SOURCE_TRUST_SYSTEM,
            allowed_by_policy=True,
        )
        assert s.source_id == "src1"
        assert s.source_trust_level == SOURCE_TRUST_SYSTEM


class TestTaskInput:
    def test_defaults(self):
        t = TaskInput()
        assert t.schema_version == "1.0"
        assert t.source_component == "ContextBuilderTaskPacker"

    def test_custom(self):
        t = TaskInput(
            task_input_id="ti1",
            task_title="Test Task",
            task_description="Do something",
            forbidden_actions=["mutate source"],
        )
        assert t.task_title == "Test Task"
        assert "mutate source" in t.forbidden_actions


class TestContextItem:
    def test_defaults(self):
        item = ContextItem()
        assert item.inclusion_decision == INCLUDE
        assert item.redacted is False
        assert item.summarized is False

    def test_custom(self):
        item = ContextItem(
            context_item_id="ci1",
            item_kind=ITEM_KIND_CONSTRAINT,
            content="must not drop safety",
            priority_score=0.9,
            inclusion_decision=INCLUDE,
        )
        assert item.context_item_id == "ci1"
        assert item.priority_score == 0.9


class TestContextPack:
    def test_defaults(self):
        p = ContextPack()
        assert p.max_context_tokens == 0
        assert p.included_items == []
        assert p.excluded_items == []

    def test_custom(self):
        item = ContextItem(context_item_id="ci1", title="test", content="data", content_hash="abc")
        p = ContextPack(
            context_pack_id="cp1",
            task_input_id="ti1",
            max_context_tokens=8192,
            included_items=[item],
        )
        assert p.context_pack_id == "cp1"
        assert len(p.included_items) == 1


class TestTaskPack:
    def test_defaults(self):
        tp = TaskPack()
        assert tp.schema_version == "1.0"
        assert tp.source_component == "ContextBuilderTaskPacker"

    def test_custom(self):
        ti = TaskInput(task_input_id="ti1", task_title="test")
        cp = ContextPack(context_pack_id="cp1", task_input_id="ti1", max_context_tokens=4096)
        tp = TaskPack(
            task_pack_id="tp1",
            task_input=ti,
            context_pack=cp,
            allowed_tools=["read_file"],
        )
        assert tp.task_pack_id == "tp1"
        assert tp.task_input.task_title == "test"
        assert "read_file" in tp.allowed_tools


class TestToDict:
    def test_dataclass(self):
        s = ContextSource(source_id="src1")
        d = to_dict(s)
        assert d["source_id"] == "src1"

    def test_nested(self):
        ti = TaskInput(task_title="test")
        tp = TaskPack(task_pack_id="tp1", task_input=ti)
        d = to_dict(tp)
        assert d["task_pack_id"] == "tp1"
        assert d["task_input"]["task_title"] == "test"

    def test_plain_dict(self):
        d = to_dict({"a": 1})
        assert d["a"] == 1
