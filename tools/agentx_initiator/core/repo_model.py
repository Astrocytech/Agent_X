from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class RepositoryFileRecord:
    path: str
    relative_path: str
    extension: str
    size_bytes: int = 0
    sha256: Optional[str] = None
    detected_layer: str = "unknown"
    is_protected: bool = False
    artifact_kinds: list[str] = field(default_factory=list)
    trust_level: str = "MEDIUM"
    detection_rules: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RepositoryDirectoryRecord:
    path: str
    relative_path: str
    detected_layer: str = "unknown"
    is_protected: bool = False
    artifact_kinds: list[str] = field(default_factory=list)
    trust_level: str = "MEDIUM"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RepositoryFingerprint:
    schema_version: str = "1.0"
    repo_root: str = ""
    scanner_version: str = ""
    total_files: int = 0
    total_directories: int = 0
    file_digest_manifest_hash: str = ""
    repository_hash: str = ""
    technology_summary: dict = field(default_factory=dict)
    layer_summary: dict = field(default_factory=dict)
    protected_path_summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RepositoryScanResult:
    schema_version: str = "1.0"
    scan_id: str = ""
    timestamp: str = ""
    repo_root: str = ""
    scanner_version: str = ""
    scan_profile: str = "default"
    status: str = "PASS"
    files: list[RepositoryFileRecord] = field(default_factory=list)
    directories: list[RepositoryDirectoryRecord] = field(default_factory=list)
    repository_fingerprint: Optional[RepositoryFingerprint] = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return len(self.files)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["total_files"] = self.total_files
        return d


@dataclass
class LayerEntry:
    layer: str = ""
    path: Path | None = None
    purpose: str = ""
    file_count: int = 0
    has_readme: bool = False


class RepoScan:
    """Backward-compat class wrapping RepositoryScanResult."""
    def __init__(self, result: RepositoryScanResult | None = None,
                 root: str = "", layers: list[LayerEntry] | None = None,
                 total_files: int = 0, source_files: int = 0,
                 doc_files: int = 0, test_files: int = 0):
        if result is not None:
            self._result = result
            self._root = result.repo_root
            self._layers = []
            self._total = result.total_files
            self._source = sum(
                1 for f in result.files
                if f.extension in (".py", ".js", ".ts", ".go", ".rs", ".java")
            )
            self._doc = sum(1 for f in result.files if f.extension == ".md")
            self._test = sum(1 for f in result.files if "test" in Path(f.path).name.lower())
        else:
            self._result = RepositoryScanResult()
            self._root = root
            self._layers = layers or []
            self._total = total_files
            self._source = source_files
            self._doc = doc_files
            self._test = test_files

    @property
    def root(self) -> str:
        return self._root

    @property
    def layers(self) -> list[LayerEntry]:
        return self._layers

    @layers.setter
    def layers(self, val: list[LayerEntry]):
        self._layers = val

    @property
    def total_files(self) -> int:
        return self._total

    @property
    def source_files(self) -> int:
        return self._source

    @property
    def doc_files(self) -> int:
        return self._doc

    @property
    def test_files(self) -> int:
        return self._test


@dataclass
class FileEntry:
    """Backward-compat: old file entry model."""
    path: Path | None = None
    relative_path: str = ""
    size_bytes: int = 0
    extension: str = ""


@dataclass
class ArchitectureReport:
    layers: list[LayerEntry] = field(default_factory=list)
    layer_count: int = 0
    valid_layer_structure: bool = False
    l0_independent: bool = False
    l1_separated: bool = False
    l2_contains_active_runtime: bool = False
    risks: list[dict] = field(default_factory=list)

    def model_dump_json(self, indent: int = 2) -> str:
        import json
        return json.dumps(asdict(self), indent=indent)
