from agentx_evolve.worker.worker_models import (
    WorkerOutput, Change, ReplacementBlock,
    WO_SCHEMA_VERSION, WO_PROPOSED, WO_NEEDS_MORE_CONTEXT, WO_FAILED,
    ALL_WORKER_STATUSES, CT_UPDATE, CT_CREATE, CT_DELETE, ALL_CHANGE_TYPES,
)


def test_wo_schema_version():
    assert WO_SCHEMA_VERSION == "1.0"


def test_wo_proposed_constant():
    assert WO_PROPOSED == "PROPOSED"


def test_wo_needs_more_context_constant():
    assert WO_NEEDS_MORE_CONTEXT == "NEEDS_MORE_CONTEXT"


def test_wo_failed_constant():
    assert WO_FAILED == "FAILED"


def test_all_worker_statuses_contains_all():
    assert WO_PROPOSED in ALL_WORKER_STATUSES
    assert WO_NEEDS_MORE_CONTEXT in ALL_WORKER_STATUSES
    assert WO_FAILED in ALL_WORKER_STATUSES
    assert len(ALL_WORKER_STATUSES) == 3


def test_change_type_constants():
    assert CT_UPDATE == "UPDATE"
    assert CT_CREATE == "CREATE"
    assert CT_DELETE == "DELETE"


def test_all_change_types_contains_all():
    assert CT_UPDATE in ALL_CHANGE_TYPES
    assert CT_CREATE in ALL_CHANGE_TYPES
    assert CT_DELETE in ALL_CHANGE_TYPES
    assert len(ALL_CHANGE_TYPES) == 3


def test_worker_output_defaults():
    w = WorkerOutput()
    assert w.schema_version == WO_SCHEMA_VERSION
    assert w.status == WO_PROPOSED
    assert w.allowed_files_only is True
    assert w.changes == []
    assert w.tests_to_run == []
    assert w.warnings == []
    assert w.errors == []


def test_worker_output_custom():
    w = WorkerOutput(
        worker_output_id="wo-001",
        task_packet_id="tp-001",
        status=WO_FAILED,
        edit_plan="plan text",
        explanation="explanation text",
    )
    assert w.worker_output_id == "wo-001"
    assert w.task_packet_id == "tp-001"
    assert w.status == WO_FAILED
    assert w.edit_plan == "plan text"
    assert w.explanation == "explanation text"


def test_worker_output_has_changes_empty():
    w = WorkerOutput()
    assert w.has_changes() is False


def test_worker_output_has_changes_with_changes():
    w = WorkerOutput()
    w.changes.append(Change(target_file="a.py"))
    assert w.has_changes() is True


def test_worker_output_target_files():
    w = WorkerOutput()
    w.changes.append(Change(target_file="b.py"))
    w.changes.append(Change(target_file="a.py"))
    w.changes.append(Change(target_file="b.py"))
    assert w.target_files() == ["a.py", "b.py"]


def test_worker_output_target_files_empty():
    w = WorkerOutput()
    assert w.target_files() == []


def test_worker_output_to_dict():
    w = WorkerOutput(worker_output_id="wo-001", task_packet_id="tp-001")
    d = w.to_dict()
    assert isinstance(d, dict)
    assert d.get("worker_output_id") == "wo-001"
    assert d.get("task_packet_id") == "tp-001"
    assert "schema_version" in d


def test_worker_output_to_dict_includes_changes():
    w = WorkerOutput()
    w.changes.append(Change(target_file="a.py", change_type=CT_UPDATE))
    d = w.to_dict()
    assert "changes" in d
    assert len(d["changes"]) == 1
    assert d["changes"][0]["target_file"] == "a.py"


def test_change_defaults():
    c = Change()
    assert c.change_type == CT_UPDATE
    assert c.target_file == ""
    assert c.instructions == ""
    assert c.replacement_blocks == []
    assert c.warnings == []
    assert c.errors == []


def test_change_custom():
    c = Change(
        target_file="/path/to/file.py",
        change_type=CT_CREATE,
        instructions="Create new file",
    )
    assert c.target_file == "/path/to/file.py"
    assert c.change_type == CT_CREATE
    assert c.instructions == "Create new file"


def test_change_to_dict():
    c = Change(target_file="a.py", change_type=CT_DELETE)
    d = c.to_dict()
    assert d["target_file"] == "a.py"
    assert d["change_type"] == CT_DELETE


def test_change_to_dict_with_replacement():
    r = ReplacementBlock(old_string="foo", new_string="bar", description="rename")
    c = Change(target_file="a.py", replacement_blocks=[r])
    d = c.to_dict()
    assert len(d["replacement_blocks"]) == 1
    assert d["replacement_blocks"][0]["old_string"] == "foo"


def test_replacement_block_defaults():
    r = ReplacementBlock()
    assert r.old_string == ""
    assert r.new_string == ""
    assert r.description == ""
    assert r.warnings == []


def test_replacement_block_custom():
    r = ReplacementBlock(
        old_string="old code",
        new_string="new code",
        description="refactor function",
        warnings=["needs review"],
    )
    assert r.old_string == "old code"
    assert r.new_string == "new code"
    assert r.description == "refactor function"
    assert r.warnings == ["needs review"]


def test_replacement_block_to_dict():
    r = ReplacementBlock(old_string="a", new_string="b")
    d = r.to_dict()
    assert d["old_string"] == "a"
    assert d["new_string"] == "b"
    assert "description" in d
