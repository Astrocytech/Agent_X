import pytest
from pathlib import Path
from agentx_initiator.core.path_registry import (
    PathRegistry, resolve_path, get_path, ensure_runtime_dirs,
    PATH_IDS,
)
from agentx_initiator.core.config_model import RuntimePaths


def test_path_registry_constructs_with_repo_root(tmp_path):
    repo = tmp_path / "myrepo"
    repo.mkdir()
    registry = PathRegistry(repo)
    assert registry.repo_root == repo.resolve()
    assert registry.runtime_root == repo.resolve() / ".agentx-init"


def test_path_registry_resolves_all_path_ids(tmp_path):
    repo = tmp_path / "myrepo"
    repo.mkdir()
    registry = PathRegistry(repo)
    for path_id in PATH_IDS:
        resolved = registry.resolve_path(path_id)
        assert str(resolved).startswith(str(registry.runtime_root))


def test_path_registry_blocks_escape(tmp_path):
    repo = tmp_path / "myrepo"
    repo.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    registry = PathRegistry(repo)
    assert registry.is_within_runtime(repo / ".agentx-init" / "config")
    assert not registry.is_within_runtime(outside)


def test_resolve_path_known_ids():
    for path_id in PATH_IDS:
        p = get_path(path_id)
        assert ".agentx-init" in str(p)


def test_resolve_path_unknown_id():
    with pytest.raises(ValueError, match="Unknown path id"):
        resolve_path("nonexistent_path_id")


def test_ensure_runtime_dirs_creates_directories(tmp_path):
    repo = tmp_path / "myrepo"
    repo.mkdir()
    paths = RuntimePaths(
        runtime_root=repo / ".agentx-init",
        config_dir=repo / ".agentx-init" / "config",
        logs_dir=repo / ".agentx-init" / "logs",
        memory_dir=repo / ".agentx-init" / "memory",
        reports_dir=repo / ".agentx-init" / "reports",
        cache_dir=repo / ".agentx-init" / "cache",
        snapshots_dir=repo / ".agentx-init" / "snapshots",
    )
    report = ensure_runtime_dirs(paths)
    assert report.status == "VALID"
    for d in [paths.config_dir, paths.logs_dir, paths.memory_dir,
              paths.reports_dir, paths.cache_dir, paths.snapshots_dir]:
        assert d.exists()


def test_path_registry_managed_paths_resolve(tmp_path):
    repo = tmp_path / "myrepo"
    repo.mkdir()
    registry = PathRegistry(repo)
    assert registry.resolve_path("config_file") == repo / ".agentx-init" / "config" / "config.json"
    assert registry.resolve_path("audit_events_file") == repo / ".agentx-init" / "memory" / "audit_events.jsonl"
    assert registry.resolve_path("repo_scan_latest") == repo / ".agentx-init" / "snapshots" / "repo_scan_latest.json"
    assert registry.resolve_path("command_history_file") == repo / ".agentx-init" / "logs" / "command_history.jsonl"


def test_paths_facade_delegates_to_path_registry():
    from agentx_initiator.core import paths
    from agentx_initiator.core import path_registry
    assert paths.repo_root == path_registry.repo_root
    assert paths.state_dir == path_registry.state_dir
    assert paths.resolve_path == path_registry.resolve_path
    assert paths.get_path == path_registry.get_path


def test_runtime_paths_properties():
    paths = RuntimePaths(
        runtime_root=Path("/root/.agentx-init"),
        config_dir=Path("/root/.agentx-init/config"),
        logs_dir=Path("/root/.agentx-init/logs"),
        memory_dir=Path("/root/.agentx-init/memory"),
        reports_dir=Path("/root/.agentx-init/reports"),
        cache_dir=Path("/root/.agentx-init/cache"),
        snapshots_dir=Path("/root/.agentx-init/snapshots"),
    )
    assert "runtime_root" in str(paths)
    assert "config_dir" in str(paths)
