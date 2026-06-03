import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone

from .doc_models import (
    DocumentRecord,
    DocumentScanReport,
    DOC_TYPE_OTHER,
    DOC_AUTHORITY_UNKNOWN,
    new_id,
    utc_now_iso,
    sha256_file,
    to_dict,
)
from .doc_registry import (
    classify_document_type,
    classify_document_authority,
    extract_document_id,
    extract_component_id,
    extract_version,
    has_generated_markers,
    is_protected_document,
)

DOCUMENT_EXTENSIONS = frozenset({".md", ".json", ".yaml", ".yml", ".txt", ".py"})
DEFAULT_EXCLUDE = frozenset({
    ".git",
    "__pycache__",
    ".agentx-init",
    "node_modules",
    ".venv",
    ".env",
    ".eggs",
    "*.pyc",
})


def scan_documentation(
    repo_root: Path,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
) -> DocumentScanReport:
    repo_root = repo_root.resolve()
    scan_id = new_id("scan")
    created_at = utc_now_iso()
    scanned_paths: list[str] = []
    skipped_paths: list[str] = []
    documents: list[DocumentRecord] = []

    exclude_set = set(DEFAULT_EXCLUDE)
    if exclude_paths:
        exclude_set.update(exclude_paths)

    walk_root = repo_root
    if include_paths:
        start_dirs = []
        for p in include_paths:
            candidate = repo_root / p
            if candidate.exists():
                start_dirs.append(candidate)
            elif (repo_root / p).exists():
                start_dirs.append(repo_root / p)
    else:
        start_dirs = [repo_root]

    for start_dir in start_dirs:
        for root_str, dirs, files in os.walk(str(start_dir)):
            root = Path(root_str)
            dirs[:] = [d for d in dirs if d not in exclude_set]

            rel_root = root.relative_to(repo_root)
            rel_str = str(rel_root.as_posix())

            if any(seg in exclude_set for seg in root.parts):
                continue

            for fname in sorted(files):
                fpath = root / fname
                ext = fpath.suffix.lower()

                if ext not in DOCUMENT_EXTENSIONS:
                    continue
                if fname.endswith(".pyc"):
                    continue

                try:
                    rel_path = fpath.relative_to(repo_root)
                except ValueError:
                    skipped_paths.append(str(fpath))
                    continue

                rel_str_path = rel_path.as_posix()
                if any(seg in rel_path.parts for seg in exclude_set):
                    continue

                scanned_paths.append(rel_str_path)
                doc = scan_document_file(repo_root, rel_path)
                documents.append(doc)

    summary = {
        "total_scanned": len(scanned_paths),
        "total_documents": len(documents),
        "total_skipped": len(skipped_paths),
    }

    return DocumentScanReport(
        scan_id=scan_id,
        created_at=created_at,
        repo_root=str(repo_root),
        scanned_paths=scanned_paths,
        documents=documents,
        skipped_paths=skipped_paths,
        summary=summary,
    )


def scan_document_file(repo_root: Path, path: Path) -> DocumentRecord:
    abs_path = (repo_root / path).resolve()
    document_id = str(path.as_posix())
    title = None

    try:
        text = abs_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        text = ""

    lines = text.split("\n")
    for line in lines[:10]:
        stripped = line.strip()
        if stripped.startswith("# ") or stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            break

    doc_type = classify_document_type(path, text)
    authority = classify_document_authority(path, text)
    comp_id = extract_component_id(text)
    doc_id_field = extract_document_id(text)
    version = extract_version(text)
    has_markers = has_generated_markers(text)
    protected = is_protected_document(path, text)

    sha256_val = sha256_file(abs_path) if abs_path.exists() else None

    try:
        mtime = abs_path.stat().st_mtime
        last_modified = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    except Exception:
        last_modified = None

    status = None
    for line in lines[:50]:
        ls = line.strip().lower()
        if ls.startswith("status:"):
            status = line.split(":", 1)[1].strip()
            break

    return DocumentRecord(
        document_id=document_id,
        path=document_id,
        title=title,
        document_type=doc_type,
        authority=authority,
        component_id=comp_id,
        version=version,
        status=status,
        sha256=sha256_val,
        last_modified_utc=last_modified,
        contains_generated_markers=has_markers,
        protected=protected,
    )
