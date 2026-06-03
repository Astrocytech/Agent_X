import pytest
import hashlib
from pathlib import Path
from agentx_evolve.evaluation.mutation_guard import (
    capture_source_state, compare_source_state, assert_no_source_mutation,
)
from agentx_evolve.evaluation.evaluation_errors import EVAL_SOURCE_MUTATION_DETECTED


def test_capture_source_state_no_git(tmp_path):
    state = capture_source_state(tmp_path)
    assert "files" in state
    assert state["git_status"] is None
    assert state["errors"] is None or isinstance(state["errors"], list)


def test_capture_source_state_with_python_files(tmp_path):
    tools_dir = tmp_path / "tools" / "agentx_evolve"
    tools_dir.mkdir(parents=True)
    (tools_dir / "module.py").write_text("x = 1")
    state = capture_source_state(tmp_path)
    assert any("module.py" in k for k in state["files"])


def test_capture_source_state_skips_non_python(tmp_path):
    tools_dir = tmp_path / "tools" / "agentx_evolve"
    tools_dir.mkdir(parents=True)
    (tools_dir / "readme.md").write_text("# doc")
    state = capture_source_state(tmp_path)
    assert not any("readme" in k for k in state["files"])


def test_capture_source_state_empty_tools_dir(tmp_path):
    (tmp_path / "tools" / "agentx_evolve").mkdir(parents=True)
    state = capture_source_state(tmp_path)
    assert len(state["files"]) == 0


def test_compare_source_state_no_changes(tmp_path):
    before = {"files": {"a.py": "hash1"}, "git_status": None}
    after = {"files": {"a.py": "hash1"}, "git_status": None}
    result = compare_source_state(before, after, tmp_path)
    assert not result["source_mutated"]
    assert len(result["changes"]) == 0


def test_compare_source_state_modified(tmp_path):
    before = {"files": {"a.py": "oldhash"}, "git_status": None}
    after = {"files": {"a.py": "newhash"}, "git_status": None}
    result = compare_source_state(before, after, tmp_path)
    assert result["source_mutated"]
    assert any(c["change"] == "MODIFIED" for c in result["changes"])


def test_compare_source_state_created(tmp_path):
    before = {"files": {}, "git_status": None}
    after = {"files": {"a.py": "hash"}, "git_status": None}
    result = compare_source_state(before, after, tmp_path)
    assert result["source_mutated"]
    assert any(c["change"] == "CREATED" for c in result["changes"])


def test_compare_source_state_deleted(tmp_path):
    before = {"files": {"a.py": "hash"}, "git_status": None}
    after = {"files": {}, "git_status": None}
    result = compare_source_state(before, after, tmp_path)
    assert result["source_mutated"]
    assert any(c["change"] == "DELETED" for c in result["changes"])


def test_compare_source_state_git_status_preserved(tmp_path):
    before = {"files": {}, "git_status": " M modified.py"}
    after = {"files": {}, "git_status": "?? new.py"}
    result = compare_source_state(before, after, tmp_path)
    assert result["git_status_before"] == " M modified.py"
    assert result["git_status_after"] == "?? new.py"


def test_assert_no_source_mutation_pass(tmp_path):
    before = {"files": {"a.py": "hash"}, "git_status": None}
    after = {"files": {"a.py": "hash"}, "git_status": None}
    assert_no_source_mutation(before, after, tmp_path)


def test_assert_no_source_mutation_raises(tmp_path):
    before = {"files": {"a.py": "hash"}, "git_status": None}
    after = {"files": {"a.py": "different"}, "git_status": None}
    with pytest.raises(RuntimeError) as exc:
        assert_no_source_mutation(before, after, tmp_path)
    assert EVAL_SOURCE_MUTATION_DETECTED in str(exc.value)


def test_capture_state_hashes_are_sha256(tmp_path):
    tools_dir = tmp_path / "tools" / "agentx_evolve"
    tools_dir.mkdir(parents=True)
    (tools_dir / "m.py").write_text("content")
    state = capture_source_state(tmp_path)
    for k, v in state["files"].items():
        assert len(v) == 64
