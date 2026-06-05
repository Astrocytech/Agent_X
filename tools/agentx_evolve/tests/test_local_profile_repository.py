import pytest
from pathlib import Path
from agentx_evolve.model_runtime.profile_repository import (
    resolve_profile_sources, hash_profile_repository,
    validate_approved_model_roots, normalize_model_path,
)


def test_hash_is_deterministic():
    repo = {
        "repository_id": "test",
        "repository_version": "1.0",
        "approved_model_roots": ["/tmp/models"],
    }
    h1 = hash_profile_repository(repo)
    h2 = hash_profile_repository(dict(sorted(repo.items())))
    assert h1 == h2
    assert len(h1) == 64


def test_resolve_profile_sources():
    result = resolve_profile_sources(Path("/repo"), {"profile_dirs": ["profiles"]})
    assert result["repo_root"] == "/repo"


def test_validate_approved_model_roots():
    repo_root = Path("/tmp")
    result = validate_approved_model_roots([Path("/tmp/models")], repo_root)
    assert result["all_valid"] is True


def test_normalize_path_does_not_crash():
    p = normalize_model_path(Path("/some/path"), [Path("/other")])
    assert p is not None
