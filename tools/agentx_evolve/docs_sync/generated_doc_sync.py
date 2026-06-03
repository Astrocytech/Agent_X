import re
from pathlib import Path

from .doc_models import (
    GeneratedDocumentSection,
    GeneratedSectionRegistry,
    DocumentScanReport,
    CENTRAL_STATUS_CURRENT,
    CENTRAL_STATUS_BLOCKED,
    sha256_bytes,
    new_id,
    utc_now_iso,
    to_dict,
)

GENERATED_SECTION_START_RE = re.compile(
    r"<!--\s*AGENTX-GENERATED-SECTION:START\s+(\S+)\s*-->", re.IGNORECASE
)
GENERATED_SECTION_END_RE = re.compile(
    r"<!--\s*AGENTX-GENERATED-SECTION:END\s+(\S+)\s*-->", re.IGNORECASE
)
GENERATED_DOC_START_RE = re.compile(
    r"<!--\s*AGENTX-GENERATED:START\s+docs_sync\s*-->", re.IGNORECASE
)
GENERATED_DOC_END_RE = re.compile(
    r"<!--\s*AGENTX-GENERATED:END\s+docs_sync\s*-->", re.IGNORECASE
)


def find_generated_sections(text: str, target_path: str) -> list[dict]:
    sections: list[dict] = []
    seen_ids: set[str] = set()

    for match in GENERATED_SECTION_START_RE.finditer(text):
        section_id = match.group(1)
        if section_id in seen_ids:
            continue
        seen_ids.add(section_id)

        end_pattern = r"<!--\s*AGENTX-GENERATED-SECTION:END\s+" + re.escape(section_id) + r"\s*-->"
        end_match = re.search(end_pattern, text[match.end():], re.IGNORECASE)
        end_pos = end_match.start() + match.end() if end_match else len(text)

        content = text[match.end():end_pos]
        end_marker_search = re.search(
            GENERATED_SECTION_END_RE, text[end_pos:] if end_match else text
        )

        sections.append({
            "section_id": section_id,
            "target_path": target_path,
            "start_marker": match.group(0),
            "end_marker": end_match.group(0) if end_match else "",
            "start_pos": match.start(),
            "end_pos": end_pos + (end_match.end() - end_match.start() if end_match else 0),
            "content": content.strip(),
            "status": CENTRAL_STATUS_CURRENT,
        })

    for match in GENERATED_DOC_START_RE.finditer(text):
        end_match = GENERATED_DOC_END_RE.search(text, match.end())
        if end_match:
            content = text[match.end():end_match.start()]
            sections.append({
                "section_id": "docs_sync_full",
                "target_path": target_path,
                "start_marker": match.group(0),
                "end_marker": end_match.group(0),
                "start_pos": match.start(),
                "end_pos": end_match.end(),
                "content": content.strip(),
                "status": CENTRAL_STATUS_CURRENT,
            })

    sections.sort(key=lambda s: s["start_pos"])
    return sections


def validate_generated_sections(sections: list[dict]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    seen_ids_by_file: dict[str, set[str]] = {}

    for section in sections:
        target = section.get("target_path", "")
        section_id = section.get("section_id", "")
        start_marker = section.get("start_marker", "")
        end_marker = section.get("end_marker", "")

        if not section_id:
            errors.append(f"section missing section_id in {target}")
        if not start_marker:
            errors.append(f"section {section_id} missing start marker")
        if not end_marker:
            errors.append(f"section {section_id} missing end marker")

        if target not in seen_ids_by_file:
            seen_ids_by_file[target] = set()
        if section_id in seen_ids_by_file[target]:
            errors.append(f"duplicate section_id '{section_id}' in {target}")
        seen_ids_by_file[target].add(section_id)

        if GENERATED_SECTION_START_RE.search(end_marker) if end_marker else False:
            errors.append(f"nested generated section detected in {target}")

    return len(errors) == 0, errors


def build_generated_section_registry(
    repo_root: Path,
    scan_report: DocumentScanReport,
) -> dict:
    all_sections: list[dict] = []
    seen_ids: set[str] = set()
    duplicate_ids: list[str] = []

    for doc in scan_report.documents:
        abs_path = repo_root / doc.path
        if not abs_path.exists():
            continue
        text = abs_path.read_text(encoding="utf-8", errors="replace")
        sections = find_generated_sections(text, doc.path)
        for section in sections:
            sid = section["section_id"]
            if sid in seen_ids:
                if sid not in duplicate_ids:
                    duplicate_ids.append(sid)
            seen_ids.add(sid)
            all_sections.append(section)

    registry = {
        "schema_version": "1.0",
        "schema_id": "generated_section_registry.schema.json",
        "component_id": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
        "registry_id": new_id("reg"),
        "created_at": utc_now_iso(),
        "sections": all_sections,
        "duplicate_section_ids": duplicate_ids,
        "warnings": [],
        "errors": [],
    }

    return registry


def render_generated_section(section_id: str, payload: dict) -> str:
    lines = [f"<!-- AGENTX-GENERATED-SECTION:START {section_id} -->"]
    lines.append("")
    for key, value in payload.items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append(f"<!-- AGENTX-GENERATED-SECTION:END {section_id} -->")
    return "\n".join(lines)


def replace_generated_section_content(
    original_text: str,
    section_id: str,
    new_content: str,
) -> tuple[str, dict]:
    start_pattern = r"<!--\s*AGENTX-GENERATED-SECTION:START\s+" + re.escape(section_id) + r"\s*-->"
    end_pattern = r"<!--\s*AGENTX-GENERATED-SECTION:END\s+" + re.escape(section_id) + r"\s*-->"

    start_match = re.search(start_pattern, original_text, re.IGNORECASE)
    end_match = re.search(end_pattern, original_text, re.IGNORECASE)

    if not start_match or not end_match:
        raise ValueError(f"generated section '{section_id}' not found")

    if start_match.start() >= end_match.start():
        raise ValueError(f"malformed markers for section '{section_id}'")

    inner_content = original_text[start_match.end():end_match.start()]
    nested_start = GENERATED_SECTION_START_RE.search(inner_content)
    nested_end = GENERATED_SECTION_END_RE.search(inner_content)
    if nested_start or nested_end:
        raise ValueError(f"nested generated section markers found inside section '{section_id}'")

    pre_content = original_text[start_match.end():end_match.start()]
    pre_hash = sha256_bytes(pre_content)

    new_text = (
        original_text[:start_match.end()]
        + "\n"
        + new_content.strip()
        + "\n"
        + original_text[end_match.start():]
    )

    post_content = original_text[start_match.end():end_match.start()]
    post_hash = sha256_bytes(new_content.strip())

    meta = {
        "section_id": section_id,
        "previous_content_sha256": pre_hash,
        "new_content_sha256": post_hash,
    }

    return new_text, meta


def write_generated_section_registry(repo_root: Path, registry: dict) -> dict:
    import json
    out_dir = repo_root / ".agentx-init" / "docs_sync"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "generated_section_registry.json"
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, default=str)
    tmp.replace(path)
    return {"path": str(path), "status": "written"}
