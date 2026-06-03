import pytest
from pathlib import Path
from agentx_evolve.model_runtime.profile_repository import (
    resolve_profile_sources, load_profile_repository,
    hash_profile_repository, validate_approved_model_roots,
    normalize_model_path,
)


def test_resolve_profile_sources():
    repo_root = Path("/tmp/repo")
    config = {"profile_dirs": ["profiles"], "approved_model_roots": ["/tmp/models"]}
    result = resolve_profile_sources(repo_root, config)
    assert result["repo_root"] == "/tmp/repo"
    assert "profiles" in result["profile_dirs"]
    assert "/tmp/models" in result["approved_model_roots"]


def test_resolve_profile_sources_empty_config():
    repo_root = Path("/tmp/repo")
    result = resolve_profile_sources(repo_root, {})
    assert result["profile_dirs"] == []
    assert result["approved_model_roots"] == []


def test_load_profile_repository():
    repo_root = Path("/tmp/repo")
    config = {"repository_version": "2.0"}
    repo = load_profile_repository(repo_root, config)
    assert repo["repository_id"].startswith("repo-")
    assert repo["repository_version"] == "2.0"
    assert "profile_sources" in repo
    assert "repository_hash" in repo


def test_hash_profile_repository():
    repo = {"a": 1, "b": 2}
    h = hash_profile_repository(repo)
    assert isinstance(h, str)
    assert len(h) == 64


def test_hash_profile_repository_deterministic():
    data = {"x": 10, "y": 20}
    h1 = hash_profile_repository(data)
    h2 = hash_profile_repository({"y": 20, "x": 10})
    assert h1 == h2


def test_validate_approved_model_roots_all_valid(tmp_path):
    sub = tmp_path / "models"
    sub.mkdir()
    result = validate_approved_model_roots([sub], tmp_path)
    assert result["all_valid"] is True
    assert len(result["valid_roots"]) == 1
    assert len(result["invalid_roots"]) == 0


def test_validate_approved_model_roots_outside(tmp_path):
    outside = Path("/tmp")
    result = validate_approved_model_roots([outside], tmp_path)
    assert result["all_valid"] is False
    assert len(result["invalid_roots"]) >= 1


def test_normalize_model_path_within_root(tmp_path):
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    model_file = models_dir / "test.gguf"
    model_file.write_text("dummy")
    result = normalize_model_path(model_file, [models_dir])
    assert result == model_file.resolve()


def test_normalize_model_path_outside_root():
    result = normalize_model_path(Path("/etc/passwd"), [Path("/tmp/models")])
    assert result == Path("/etc/passwd").resolve()
