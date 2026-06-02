from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4
from agentx_initiator.core.repo_model import (
    RepositoryScanResult, RepositoryFileRecord, RepositoryDirectoryRecord,
    RepositoryFingerprint, RepoScan, LayerEntry,
)
from agentx_initiator.core.layer_mapper import (
    classify_agentx_layer, is_protected_path,
)
from agentx_initiator.core.path_registry import _detect_repo_root, get_path


IGNORE_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".agentx-init"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
SCANNER_VERSION = "1.0.0"


def scan_repo(root: Optional[Path] = None) -> RepoScan:
    """Backward-compat: scan default repo root and return old RepoScan."""
    if root is None:
        root = _detect_repo_root()
    result = scan_repository(root)
    layers = []
    for layer_name in ["L0", "L1", "L2"]:
        layer_path = root / layer_name
        if not layer_path.exists():
            continue
        count = sum(
            1 for f in result.files
            if classify_agentx_layer(Path(f.path)) == layer_name
        )
        layers.append(LayerEntry(
            layer=layer_name,
            path=layer_path,
            purpose=_layer_purpose(layer_name),
            file_count=count,
            has_readme=(layer_path / "README.md").exists(),
        ))
    return RepoScan(
        root=str(root),
        layers=layers,
        total_files=result.total_files,
        source_files=sum(
            1 for f in result.files
            if f.extension in (".py", ".js", ".ts", ".go", ".rs", ".java")
        ),
        doc_files=sum(1 for f in result.files if f.extension == ".md"),
        test_files=sum(
            1 for f in result.files if "test" in Path(f.path).name.lower()
        ),
    )


def scan_repository(root: Path,
                     ignore_dirs: Optional[set[str]] = None,
                     max_file_size: int = MAX_FILE_SIZE_BYTES,
                     include_hidden: bool = False) -> RepositoryScanResult:
    root = root.resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repository root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository root is not a directory: {root}")

    ignore = set(IGNORE_DIRS)
    if ignore_dirs:
        ignore.update(ignore_dirs)

    scan_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    files: list[RepositoryFileRecord] = []
    directories: list[RepositoryDirectoryRecord] = []
    warnings: list[str] = []
    errors: list[str] = []
    file_hashes: list[str] = []

    for entry in sorted(root.rglob("*"), key=lambda p: str(p)):
        try:
            rel = entry.relative_to(root)
        except ValueError:
            continue

        parts = rel.parts
        if any(part in ignore for part in parts):
            continue

        if not include_hidden and any(p.startswith(".") for p in parts):
            continue

        if entry.is_symlink():
            target = entry.resolve()
            try:
                target.relative_to(root)
            except ValueError:
                warnings.append(f"SYMLINK_SKIPPED: {rel} escapes repository root")
                continue
            warnings.append(f"SYMLINK_SKIPPED: {rel} (safe, but skipped for consistency)")
            continue

        if entry.is_dir():
            layer = classify_agentx_layer(entry)
            protected = is_protected_path(entry)
            directories.append(RepositoryDirectoryRecord(
                path=str(entry),
                relative_path=str(rel),
                detected_layer=layer,
                is_protected=protected,
                trust_level="HIGH" if protected else "MEDIUM",
            ))
            continue

        if not entry.is_file():
            continue

        ext = entry.suffix
        size = entry.stat().st_size

        sha256_val: Optional[str] = None
        entry_warnings: list[str] = []

        if size > max_file_size:
            entry_warnings.append("LARGE_FILE_SKIPPED")
            warnings.append(f"LARGE_FILE_SKIPPED: {rel} ({size} bytes)")
        else:
            try:
                sha256_val = _hash_file(entry)
            except OSError as e:
                entry_warnings.append(f"FILE_READ_ERROR: {e}")
                errors.append(f"FILE_READ_ERROR: {rel}: {e}")

        layer = classify_agentx_layer(entry)
        protected = is_protected_path(entry)

        artifact_kinds = _detect_artifact_kinds(rel, ext)
        trust_level = "HIGH" if protected else "MEDIUM"

        files.append(RepositoryFileRecord(
            path=str(entry),
            relative_path=str(rel),
            extension=ext,
            size_bytes=size,
            sha256=sha256_val,
            detected_layer=layer,
            is_protected=protected,
            artifact_kinds=artifact_kinds,
            trust_level=trust_level,
            warnings=entry_warnings,
        ))
        if sha256_val:
            file_hashes.append(sha256_val)

    repo_hash = hashlib.sha256(
        "".join(sorted(file_hashes)).encode("utf-8")
    ).hexdigest() if file_hashes else ""

    manifest_hash = hashlib.sha256(
        "".join(sorted(file_hashes)).encode("utf-8")
    ).hexdigest() if file_hashes else ""

    fingerprint = RepositoryFingerprint(
        repo_root=str(root),
        scanner_version=SCANNER_VERSION,
        total_files=len(files),
        total_directories=len(directories),
        file_digest_manifest_hash=manifest_hash,
        repository_hash=repo_hash,
        layer_summary=_build_layer_summary(files),
        protected_path_summary=_build_protected_summary(files),
    )

    status = "PASS"
    if errors:
        status = "FAIL"
    elif warnings:
        status = "PARTIAL"

    return RepositoryScanResult(
        scan_id=scan_id,
        timestamp=timestamp,
        repo_root=str(root),
        scanner_version=SCANNER_VERSION,
        status=status,
        files=files,
        directories=directories,
        repository_fingerprint=fingerprint,
        warnings=warnings,
        errors=errors,
    )


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _detect_artifact_kinds(rel: Path, ext: str) -> list[str]:
    kinds = []
    parts_lower = [p.lower() for p in rel.parts]
    if "test" in rel.name.lower():
        kinds.append("test")
    if ext in (".py", ".js", ".ts", ".go", ".rs", ".java"):
        kinds.append("source")
    if ext == ".md":
        kinds.append("documentation")
    if ext == ".json" and "schema" in parts_lower:
        kinds.append("schema")
    if "validator" in parts_lower:
        kinds.append("validator")
    if "profile" in parts_lower or "spec" in parts_lower:
        kinds.append("profile")
    return kinds


def _build_layer_summary(files: list[RepositoryFileRecord]) -> dict:
    summary: dict[str, int] = {}
    for f in files:
        layer = f.detected_layer
        summary[layer] = summary.get(layer, 0) + 1
    return summary


def _build_protected_summary(files: list[RepositoryFileRecord]) -> dict:
    total = sum(1 for f in files if f.is_protected)
    return {"total_protected": total}


def _layer_purpose(layer: str) -> str:
    purposes = {
        "L0": "Governed seed kernel — protected runtime",
        "L1": "External evolution / Controller governance",
        "L2": "Specialization profile/spec layer",
    }
    return purposes.get(layer, "")
