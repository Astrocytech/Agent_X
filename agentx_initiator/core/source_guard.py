from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SourceMutationCheckResult:
    passed: bool = True
    mutated_paths: list[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "mutated_paths": self.mutated_paths,
            "error": self.error,
        }


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def capture_source_state(root: Path, exclude_dirs: set | None = None) -> dict[str, str]:
    if exclude_dirs is None:
        exclude_dirs = {".agentx-init", ".git", "__pycache__", ".venv", "node_modules"}
    state: dict[str, str] = {}
    root = root.resolve()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(root)
            if any(part in exclude_dirs for part in rel.parts):
                continue
            state[str(rel)] = _hash_file(p)
        except (ValueError, OSError):
            pass
    return state


def verify_no_source_mutation(before: dict[str, str], after: dict[str, str]) -> SourceMutationCheckResult:
    mutated: list[str] = []
    for path, before_hash in before.items():
        after_hash = after.get(path)
        if after_hash is None:
            mutated.append(f"{path} (missing after)")
        elif after_hash != before_hash:
            mutated.append(f"{path} (hash changed)")

    added = set(after.keys()) - set(before.keys())
    for path in sorted(added):
        mutated.append(f"{path} (new file)")

    if mutated:
        return SourceMutationCheckResult(passed=False, mutated_paths=mutated)

    return SourceMutationCheckResult(passed=True)
