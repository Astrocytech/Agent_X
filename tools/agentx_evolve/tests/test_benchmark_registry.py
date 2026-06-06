from pathlib import Path
import pytest
from agentx_evolve.evaluation.benchmark_registry import BenchmarkRegistry


def test_registry_register_and_lookup(tmp_path):
    suite = tmp_path / "smoke_suite.json"
    suite.write_text("{}")
    reg = BenchmarkRegistry()
    reg.register("smoke", suite)
    assert reg.lookup("smoke") == suite.resolve()


def test_registry_lookup_missing_returns_none(tmp_path):
    reg = BenchmarkRegistry()
    assert reg.lookup("nonexistent") is None


def test_registry_is_registered(tmp_path):
    suite = tmp_path / "suite.json"
    suite.write_text("{}")
    reg = BenchmarkRegistry()
    reg.register("test", suite)
    assert reg.is_registered("test")
    assert not reg.is_registered("other")


def test_registry_list_suites_deterministic(tmp_path):
    reg = BenchmarkRegistry()
    paths = []
    for name in ["z_suite", "a_suite", "m_suite"]:
        p = tmp_path / f"{name}.json"
        p.write_text("{}")
        reg.register(name, p)
        paths.append(p)
    listed = reg.list_suites()
    assert list(listed.keys()) == ["a_suite", "m_suite", "z_suite"]


def test_registry_rejects_nonexistent_path(tmp_path):
    reg = BenchmarkRegistry()
    with pytest.raises(FileNotFoundError):
        reg.register("missing", tmp_path / "nope.json")


def test_registry_rejects_non_json_path(tmp_path):
    reg = BenchmarkRegistry()
    p = tmp_path / "suite.txt"
    p.write_text("{}")
    with pytest.raises(ValueError, match="JSON"):
        reg.register("bad", p)


def test_registry_len(tmp_path):
    reg = BenchmarkRegistry()
    assert len(reg) == 0
    for i in range(3):
        p = tmp_path / f"s{i}.json"
        p.write_text("{}")
        reg.register(f"s{i}", p)
    assert len(reg) == 3


def test_registry_list_suites_empty():
    reg = BenchmarkRegistry()
    assert reg.list_suites() == {}
