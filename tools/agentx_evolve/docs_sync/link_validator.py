import re
from pathlib import Path
from urllib.parse import urlparse

from .doc_models import (
    DocumentLinkRecord,
    DocumentScanReport,
    LINK_TYPE_LOCAL_FILE,
    LINK_TYPE_LOCAL_FILE_WITH_ANCHOR,
    LINK_TYPE_LOCAL_ANCHOR,
    LINK_TYPE_EXTERNAL_HTTP,
    LINK_TYPE_EXTERNAL_MAILTO,
    LINK_TYPE_EXTERNAL_OTHER,
    LINK_TYPE_UNSUPPORTED,
    LINK_TYPE_MALFORMED,
    CENTRAL_STATUS_PASS,
    CENTRAL_STATUS_FAIL,
    CENTRAL_STATUS_NOT_CHECKED,
    CENTRAL_STATUS_DEFERRED_SAFELY,
    CENTRAL_STATUS_CURRENT,
    new_id,
)


INLINE_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
REFERENCE_LINK_RE = re.compile(r"\[([^\]]+)\]:\s*(\S+)")
ANCHOR_ONLY_RE = re.compile(r"^#[\w\-]+")


def extract_markdown_links(text: str, source_path: Path) -> list[DocumentLinkRecord]:
    links: list[DocumentLinkRecord] = []
    seen_targets: set[str] = set()

    for match in INLINE_LINK_RE.finditer(text):
        target = match.group(2).strip()
        if target in seen_targets:
            continue
        seen_targets.add(target)
        link = _classify_link(source_path, target)
        links.append(link)

    for match in REFERENCE_LINK_RE.finditer(text):
        target = match.group(2).strip()
        if target in seen_targets:
            continue
        seen_targets.add(target)
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        link = _classify_link(source_path, target)
        links.append(link)

    return links


def _classify_link(source_path: Path, target: str) -> DocumentLinkRecord:
    link_id = new_id("link")
    source_str = str(source_path.as_posix())

    if target.startswith("mailto:"):
        return DocumentLinkRecord(
            link_id=link_id, source_path=source_str, target=target,
            link_type=LINK_TYPE_EXTERNAL_MAILTO, status=CENTRAL_STATUS_NOT_CHECKED,
            reason="mailto link, not fetched",
        )

    if target.startswith("http://") or target.startswith("https://"):
        link_type = LINK_TYPE_EXTERNAL_HTTP
        return DocumentLinkRecord(
            link_id=link_id, source_path=source_str, target=target,
            link_type=link_type, status=CENTRAL_STATUS_NOT_CHECKED,
            reason="external link, not fetched",
        )

    if target.startswith("#"):
        return DocumentLinkRecord(
            link_id=link_id, source_path=source_str, target=target,
            link_type=LINK_TYPE_LOCAL_ANCHOR, status=CENTRAL_STATUS_DEFERRED_SAFELY,
            reason="anchor only, deferral in v1",
        )

    if ANCHOR_ONLY_RE.match(target):
        return DocumentLinkRecord(
            link_id=link_id, source_path=source_str, target=target,
            link_type=LINK_TYPE_LOCAL_ANCHOR, status=CENTRAL_STATUS_DEFERRED_SAFELY,
            reason="anchor only, deferral in v1",
        )

    if target.startswith("data:"):
        return DocumentLinkRecord(
            link_id=link_id, source_path=source_str, target=target,
            link_type=LINK_TYPE_UNSUPPORTED, status=CENTRAL_STATUS_NOT_CHECKED,
            reason="data URI, not checked",
        )

    if target.startswith("file://"):
        target = target[7:]

    if "#" in target:
        parts = target.split("#", 1)
        file_part = parts[0]
        anchor_part = parts[1]
        if not file_part:
            return DocumentLinkRecord(
                link_id=link_id, source_path=source_str, target=target,
                link_type=LINK_TYPE_LOCAL_FILE_WITH_ANCHOR,
                status=CENTRAL_STATUS_DEFERRED_SAFELY,
                reason="same-file anchor, deferral in v1",
            )

    if any(c in target for c in ("://",)):
        return DocumentLinkRecord(
            link_id=link_id, source_path=source_str, target=target,
            link_type=LINK_TYPE_EXTERNAL_OTHER, status=CENTRAL_STATUS_NOT_CHECKED,
            reason="external non-HTTP link, not fetched",
        )

    return DocumentLinkRecord(
        link_id=link_id, source_path=source_str, target=target,
        link_type=LINK_TYPE_LOCAL_FILE, status=CENTRAL_STATUS_NOT_CHECKED,
        reason="unresolved local file link",
    )


def resolve_relative_link(
    repo_root: Path, source_path: Path, target: str
) -> Path | None:
    anchor_part = None
    if "#" in target:
        idx = target.index("#")
        target = target[:idx]

    if not target:
        return source_path

    base = source_path.parent if source_path.is_relative_to(repo_root) else repo_root
    candidate = (base / target).resolve()

    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        return None

    if candidate.exists():
        return candidate
    return None


def validate_document_links(
    repo_root: Path, scan_report: DocumentScanReport
) -> list[DocumentLinkRecord]:
    repo_root = repo_root.resolve()
    all_links: list[DocumentLinkRecord] = []

    for doc in scan_report.documents:
        doc_path = repo_root / doc.path
        if not doc_path.exists():
            continue
        try:
            text = doc_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        extracted = extract_markdown_links(text, doc_path)
        for link in extracted:
            if link.link_type == LINK_TYPE_LOCAL_FILE:
                resolved = resolve_relative_link(repo_root, doc_path, link.target)
                if resolved is not None and resolved.exists():
                    link.status = CENTRAL_STATUS_PASS
                    link.resolved_path = str(resolved.relative_to(repo_root).as_posix())
                    link.reason = "resolved"
                else:
                    link.status = CENTRAL_STATUS_FAIL
                    link.reason = "broken link"
            elif link.link_type == LINK_TYPE_LOCAL_FILE_WITH_ANCHOR:
                file_part = link.target.split("#", 1)[0] if "#" in link.target else link.target
                if file_part:
                    resolved = resolve_relative_link(repo_root, doc_path, file_part)
                    if resolved and resolved.exists():
                        link.resolved_path = str(resolved.relative_to(repo_root).as_posix())
                        link.status = CENTRAL_STATUS_PASS
                        link.reason = "file resolved, anchor deferred"
                    else:
                        link.status = CENTRAL_STATUS_FAIL
                        link.reason = "broken link"
            all_links.append(link)

    return all_links
