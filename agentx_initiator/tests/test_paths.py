from pathlib import Path
from agentx_initiator.core import paths


def test_repo_root_exists():
    root = paths.repo_root()
    assert root.exists()
    assert (root / "L0").exists()


def test_state_dir():
    sd = paths.state_dir()
    assert ".agentx-init" in str(sd)


def test_memory_file():
    mf = paths.memory_file("test.jsonl")
    assert "memory" in str(mf)
    assert mf.name == "test.jsonl"


def test_snapshot_file():
    sf = paths.snapshot_file("test.json")
    assert "snapshots" in str(sf)
    assert sf.name == "test.json"


def test_ensure_state_dirs():
    paths.ensure_state_dirs()
    assert paths.state_dir().exists()
    assert (paths.state_dir() / "config").exists()
    assert (paths.state_dir() / "memory").exists()
