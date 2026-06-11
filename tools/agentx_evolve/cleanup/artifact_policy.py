"""Artifact root policy and cleanup rules.

Item 22 (18.1/18.2): Unified artifact-root mapping and cleanup policy.
"""

from __future__ import annotations

import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


@dataclass
class ArtifactRoot:
    name: str
    path: str
    description: str
    persistence: str = "retained"  # retained | ephemeral | committed
    cleanup_age_days: int = 0
    patterns_to_clean: list[str] = field(default_factory=list)


ROOTS: list[ArtifactRoot] = [
    ArtifactRoot("source_docs", "docs/plans", "Source plans & documents", "committed"),
    ArtifactRoot("schemas", "schemas", "Shared JSON schemas", "committed"),
    ArtifactRoot("benchmark_artifacts", "benchmarks", "Benchmark source + derived", "committed"),
    ArtifactRoot("example_agents", "examples", "Example agent source", "committed"),
    ArtifactRoot("runtime_evidence", ".agentx-init", "Runtime evidence & provenance", "retained"),
    ArtifactRoot("reports", "reports", "Generated acceptance reports", "retained"),
    ArtifactRoot("temp_workspace", "", "Temporary Stage B workspace", "ephemeral",
                 cleanup_age_days=0, patterns_to_clean=["/tmp/umbrella-*", "/tmp/clean-*"]),
    ArtifactRoot("canary_files", "", "Canary test files", "ephemeral",
                 cleanup_age_days=0, patterns_to_clean=["/tmp/canary-*", "canary_*.txt"]),
    ArtifactRoot("pytest_cache", "", "pytest __pycache__ and .pytest_cache", "ephemeral",
                 cleanup_age_days=0, patterns_to_clean=["__pycache__", ".pytest_cache", "*.pyc"]),
]


def get_root(name: str) -> ArtifactRoot | None:
    for r in ROOTS:
        if r.name == name:
            return r
    return None


def classify(path: str) -> str:
    """Classify a file path into an artifact root name."""
    p = path.replace("\\", "/")
    for r in ROOTS:
        if r.path and p.startswith(r.path):
            return r.name
    if "/tmp/" in p or p.startswith("/tmp/"):
        return "temp_workspace"
    if p.endswith(".pyc") or "__pycache__" in p or ".pytest_cache" in p:
        return "pytest_cache"
    if "canary" in p.lower():
        return "canary_files"
    return "runtime_evidence"


def run_cleanup(dry_run: bool = True) -> list[dict[str, Any]]:
    """Remove ephemeral artifacts according to policy."""
    results = []
    now = time.time()
    for root in ROOTS:
        if root.persistence != "ephemeral":
            continue
        for pattern in root.patterns_to_clean:
            import glob
            for path in glob.glob(pattern):
                p = Path(path)
                if p.exists():
                    entry = {"root": root.name, "path": str(p), "action": "dry-run" if dry_run else "removed"}
                    if not dry_run:
                        if p.is_dir():
                            shutil.rmtree(p, ignore_errors=True)
                        else:
                            p.unlink(missing_ok=True)
                        entry["action"] = "removed"
                    results.append(entry)
    return results


def describe_roots() -> list[dict[str, Any]]:
    return [{"name": r.name, "path": r.path, "description": r.description,
             "persistence": r.persistence} for r in ROOTS]
