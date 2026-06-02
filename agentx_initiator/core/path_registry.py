from __future__ import annotations
from pathlib import Path
from typing import Optional
from agentx_initiator.core.config_model import RuntimePaths, ConfigValidationReport

PATH_IDS = {
    "runtime_root": "",
    "config_dir": "config",
    "logs_dir": "logs",
    "memory_dir": "memory",
    "reports_dir": "reports",
    "cache_dir": "cache",
    "snapshots_dir": "snapshots",
    "config_file": "config/config.json",
    "path_registry_file": "config/path_registry.json",
    "audit_events_file": "memory/audit_events.jsonl",
    "command_history_file": "logs/command_history.jsonl",
    "repo_scan_latest": "snapshots/repo_scan_latest.json",
    "scans_history": "memory/scans.jsonl",
    "architecture_latest": "snapshots/architecture_latest.json",
    "latest_status_report": "reports/latest_status.md",
    "architecture_report": "reports/architecture_report.md",
}


class PathRegistry:
    def __init__(self, repo_root: Path):
        self._repo_root = repo_root.resolve()
        self._runtime_root = self._repo_root / ".agentx-init"

    @property
    def repo_root(self) -> Path:
        return self._repo_root

    @property
    def runtime_root(self) -> Path:
        return self._runtime_root

    def resolve_path(self, path_id: str) -> Path:
        if path_id == "runtime_root":
            return self._runtime_root
        rel = PATH_IDS.get(path_id)
        if rel is None:
            raise ValueError(f"Unknown path id: {path_id}")
        return self._runtime_root / rel

    def get_paths(self) -> RuntimePaths:
        return RuntimePaths(
            runtime_root=self._runtime_root,
            config_dir=self._runtime_root / "config",
            logs_dir=self._runtime_root / "logs",
            memory_dir=self._runtime_root / "memory",
            reports_dir=self._runtime_root / "reports",
            cache_dir=self._runtime_root / "cache",
            snapshots_dir=self._runtime_root / "snapshots",
        )

    def ensure_runtime_dirs(self) -> ConfigValidationReport:
        report = ConfigValidationReport()
        for path_id in [
            "config_dir", "logs_dir", "memory_dir",
            "reports_dir", "cache_dir", "snapshots_dir",
        ]:
            p = self.resolve_path(path_id)
            try:
                p.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                report.warnings.append(f"Cannot create {path_id}: {e}")
        if report.warnings:
            report.status = "PARTIAL"
        return report

    def is_within_runtime(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self._runtime_root)
            return True
        except ValueError:
            return False


_DEFAULT_REGISTRY: Optional[PathRegistry] = None


def _get_default_registry() -> PathRegistry:
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = PathRegistry(_detect_repo_root())
    return _DEFAULT_REGISTRY


def _detect_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def repo_root() -> Path:
    return _get_default_registry().repo_root


def state_dir() -> Path:
    return _get_default_registry().runtime_root


def config_file() -> Path:
    return _get_default_registry().resolve_path("config_file")


def memory_file(name: str) -> Path:
    return _get_default_registry().resolve_path("memory_dir") / name


def report_file(name: str) -> Path:
    return _get_default_registry().resolve_path("reports_dir") / name


def snapshot_file(name: str) -> Path:
    return _get_default_registry().resolve_path("snapshots_dir") / name


def ensure_state_dirs():
    _get_default_registry().ensure_runtime_dirs()


def resolve_path(path_id: str, registry: Optional[PathRegistry] = None) -> Path:
    if registry is None:
        registry = _get_default_registry()
    return registry.resolve_path(path_id)


def get_path(path_id: str) -> Path:
    return _get_default_registry().resolve_path(path_id)


def ensure_runtime_dirs(paths: RuntimePaths) -> ConfigValidationReport:
    registry = PathRegistry(paths.runtime_root.parent)
    return registry.ensure_runtime_dirs()
