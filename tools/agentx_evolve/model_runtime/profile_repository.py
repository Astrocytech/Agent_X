from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any


def resolve_profile_sources(repo_root: Path, config: dict) -> dict:
    return {
        "repo_root": str(repo_root),
        "profile_dirs": config.get("profile_dirs", []),
        "approved_model_roots": config.get("approved_model_roots", []),
    }


def load_profile_repository(repo_root: Path, config: dict) -> dict:
    sources = resolve_profile_sources(repo_root, config)
    repository = {
        "repository_id": "repo-" + hashlib.md5(str(repo_root).encode()).hexdigest()[:12],
        "repository_version": config.get("repository_version", "1.0"),
        "created_at": __import__("datetime").datetime.now(__import__("pytz").timezone.utc).isoformat() if False else "",
        "profile_sources": sources,
        "approved_model_roots": sources["approved_model_roots"],
        "model_profile_hashes": {},
        "runtime_profile_hashes": {},
        "inventory_hash": "",
        "hardware_profile_hash": "",
        "repository_hash": "",
    }
    return repository


def hash_profile_repository(repository: dict) -> str:
    raw = json.dumps(repository, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def validate_approved_model_roots(roots: list[Path], repo_root: Path) -> dict:
    valid: list[str] = []
    invalid: list[str] = []
    for root in roots:
        resolved = root.resolve() if root.exists() else root
        try:
            resolved.relative_to(repo_root.resolve())
            valid.append(str(resolved))
        except ValueError:
            invalid.append(str(resolved))
    return {"valid_roots": valid, "invalid_roots": invalid, "all_valid": len(invalid) == 0}


def normalize_model_path(path: Path, approved_model_roots: list[Path]) -> Path:
    resolved = path.resolve()
    for root in approved_model_roots:
        try:
            resolved.relative_to(root.resolve())
            return resolved
        except ValueError:
            continue
    return resolved
