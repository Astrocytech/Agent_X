import pytest
import hashlib
from agentx_initiator.core.source_guard import capture_source_state, verify_no_source_mutation


def test_capture_source_state(tmp_path):
    (tmp_path / "file.py").write_text("print('hello')")
    state = capture_source_state(tmp_path)
    assert len(state) == 1
    k = list(state.keys())[0]
    assert state[k] == hashlib.sha256(b"print('hello')").hexdigest()


def test_verify_no_mutation_pass(tmp_path):
    (tmp_path / "file.py").write_text("print('hello')")
    before = capture_source_state(tmp_path)
    after = capture_source_state(tmp_path)
    result = verify_no_source_mutation(before, after)
    assert result.passed
    assert result.mutated_paths == []


def test_verify_no_mutation_fail(tmp_path):
    (tmp_path / "file.py").write_text("print('hello')")
    before = capture_source_state(tmp_path)
    (tmp_path / "file.py").write_text("print('modified')")
    after = capture_source_state(tmp_path)
    result = verify_no_source_mutation(before, after)
    assert not result.passed
    assert len(result.mutated_paths) > 0
