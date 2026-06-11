from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ObservationResult:
    action_id: str = ""
    all_expected_found: bool = False
    artifacts: list[dict] = field(default_factory=list)
    hashes: dict[str, str] = field(default_factory=dict)
    source_mutation_detected: bool = False
    unexpected_effects: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "all_expected_found": self.all_expected_found,
            "artifacts": list(self.artifacts),
            "hashes": dict(self.hashes),
            "source_mutation_detected": self.source_mutation_detected,
            "unexpected_effects": list(self.unexpected_effects),
            "errors": list(self.errors),
        }


class MvpObserver:
    def __init__(self, artifact_store: Any, source_dirs: list[str] | None = None) -> None:
        self._artifact_store = artifact_store
        self._source_dirs = source_dirs or []
        self._last_result: ObservationResult | None = None
        self._last_mutation_errors: list[str] = []

    def observe(self, action: Any, context: dict[str, Any]) -> ObservationResult:
        action_id = getattr(action, "action_id", "")
        run_id = context.get("run_id", "")
        expected_artifacts = context.get("expected_artifacts", [])

        found_artifacts = []
        hashes: dict[str, str] = {}
        errors = []

        for exp in expected_artifacts:
            path = exp.get("path", "")
            h = self._artifact_store.hash_path(path) if hasattr(self._artifact_store, "hash_path") else None
            content = self._artifact_store.read(path) if hasattr(self._artifact_store, "read") else None
            if content is not None:
                found_artifacts.append({"path": path, "hash": h})
                if h:
                    hashes[path] = h
            else:
                errors.append(f"Expected artifact not found: {path}")

        source_mutation = self._check_source_mutation()
        if self._last_mutation_errors:
            errors.extend(self._last_mutation_errors)
        unexp = context.get("unexpected_effects", [])

        result = ObservationResult(
            action_id=action_id,
            all_expected_found=len(errors) == 0,
            artifacts=found_artifacts,
            hashes=hashes,
            source_mutation_detected=source_mutation,
            unexpected_effects=unexp,
            errors=errors,
        )
        self._last_result = result
        return result

    def _check_source_mutation(self) -> bool:
        from agentx_evolve.observation.source_manifest import (
            DEFAULT_SOURCE_SCOPE, collect_source_manifest,
            compare_source_manifests,
        )
        report_dir = Path(".agentx-init/reports")
        before_path = report_dir / "functional_runtime_mvp_source_hash_manifest_before.json"
        root = Path.cwd()
        include_paths = self._source_dirs or list(DEFAULT_SOURCE_SCOPE)
        self._last_mutation_errors = []
        try:
            if before_path.exists():
                import json
                before = json.loads(before_path.read_text(encoding="utf-8"))
            else:
                before = collect_source_manifest(root, include_paths=include_paths)
            after = collect_source_manifest(root, include_paths=include_paths)
            diff = compare_source_manifests(before, after)
            return diff.get("mutation_detected", False)
        except Exception as e:
            self._last_mutation_errors = [f"source mutation check failed: {e}"]
            return True

    @property
    def last_result(self) -> ObservationResult | None:
        return self._last_result
