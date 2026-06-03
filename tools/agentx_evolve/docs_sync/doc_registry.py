import re
from pathlib import Path

from .doc_models import (
    DOC_AUTHORITY_MANUAL_GOVERNED,
    DOC_AUTHORITY_MANUAL_EDITABLE,
    DOC_AUTHORITY_GENERATED,
    DOC_AUTHORITY_RUNTIME_EVIDENCE,
    DOC_AUTHORITY_EXTERNAL_REFERENCE,
    DOC_AUTHORITY_UNKNOWN,
    DOC_TYPE_CONTRACT,
    DOC_TYPE_IMPLEMENTATION_SPEC,
    DOC_TYPE_REVIEW_DOD,
    DOC_TYPE_README,
    DOC_TYPE_INDEX,
    DOC_TYPE_SCHEMA,
    DOC_TYPE_TEST,
    DOC_TYPE_REPORT,
    DOC_TYPE_EVIDENCE,
    DOC_TYPE_OTHER,
    DRIFT_TYPE_MISSING_CONTRACT_SPEC_REVIEW,
    DRIFT_TYPE_MISSING_SCHEMA,
    DRIFT_TYPE_MISSING_TEST,
    DRIFT_TYPE_DONE_WITHOUT_EVIDENCE,
)


DOC_ID_RE = re.compile(r"document_id\s*:\s*(\S+)", re.IGNORECASE)
COMPONENT_ID_RE = re.compile(r"component_id\s*:\s*(\S+)", re.IGNORECASE)
VERSION_RE = re.compile(r"version\s*:\s*v?(\d+\.\d+)", re.IGNORECASE)
GENERATED_START_RE = re.compile(r"<!--\s*AGENTX-GENERATED-START\s+docs_sync\s*-->", re.IGNORECASE)
GENERATED_START_SECTION_RE = re.compile(
    r"<!--\s*AGENTX-GENERATED-SECTION:START\s+(\S+)\s*-->", re.IGNORECASE
)
GENERATED_END_RE = re.compile(r"<!--\s*AGENTX-GENERATED-END\s+docs_sync\s*-->", re.IGNORECASE)
GENERATED_END_SECTION_RE = re.compile(
    r"<!--\s*AGENTX-GENERATED-SECTION:END\s+(\S+)\s*-->", re.IGNORECASE
)

GOVERNED_PATH_FRAGMENTS = frozenset({
    "IMPLEMENTATION_SPEC",
    "DOCUMENTATION_SYNCHRONIZATION_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "IMPLEMENTATION_REVIEW_AND_DOD",
    "ROADMAP",
    "STANDARD",
})

RUNTIME_EVIDENCE_PREFIX = ".agentx-init/"


def classify_document_type(path: Path, text: str) -> str:
    lower = path.name.lower()
    parent = str(path.parent).lower()

    if lower.endswith(".schema.json") or lower == "schema.json":
        return DOC_TYPE_SCHEMA
    if "test_" in lower and lower.endswith(".py"):
        return DOC_TYPE_TEST
    if "readme" in lower or "readme" in parent:
        return DOC_TYPE_README
    if "index" in lower and lower.endswith(".md"):
        return DOC_TYPE_INDEX
    if "report" in lower or "report" in parent:
        return DOC_TYPE_REPORT
    if path.name.startswith("validate_") and path.name.endswith("_schemas.py"):
        return DOC_TYPE_OTHER
    if "evidence" in lower or path.name.startswith(".agentx-init/"):
        return DOC_TYPE_EVIDENCE
    if "contract" in lower or "contract" in parent:
        return DOC_TYPE_CONTRACT
    if "spec" in lower or "implementation_spec" in lower or "specification" in parent:
        return DOC_TYPE_IMPLEMENTATION_SPEC
    if "review" in lower and "dod" in lower:
        return DOC_TYPE_REVIEW_DOD
    if "dod" in lower.replace("_", "").replace("-", ""):
        return DOC_TYPE_REVIEW_DOD
    return DOC_TYPE_OTHER


def classify_document_authority(path: Path, text: str) -> str:
    str_path = str(path.as_posix())

    if str_path.startswith(RUNTIME_EVIDENCE_PREFIX) or "/.agentx-init/" in str_path:
        return DOC_AUTHORITY_RUNTIME_EVIDENCE
    if DOC_AUTHORITY_GENERATED == DOC_AUTHORITY_GENERATED:
        if GENERATED_START_RE.search(text) or GENERATED_START_SECTION_RE.search(text):
            return DOC_AUTHORITY_GENERATED

    for fragment in GOVERNED_PATH_FRAGMENTS:
        if fragment in str_path:
            return DOC_AUTHORITY_MANUAL_GOVERNED

    if text.strip().startswith("<!-- AGENTX-GENERATED") or text.strip().startswith("<!--AGENTX-GENERATED"):
        return DOC_AUTHORITY_GENERATED

    return DOC_AUTHORITY_MANUAL_EDITABLE


def extract_document_id(text: str) -> str | None:
    m = DOC_ID_RE.search(text)
    return m.group(1) if m else None


def extract_component_id(text: str) -> str | None:
    m = COMPONENT_ID_RE.search(text)
    return m.group(1) if m else None


def extract_version(text: str) -> str | None:
    m = VERSION_RE.search(text)
    return m.group(1) if m else None


def has_generated_markers(text: str) -> bool:
    start = GENERATED_START_RE.search(text) or GENERATED_START_SECTION_RE.search(text)
    end = GENERATED_END_RE.search(text) or GENERATED_END_SECTION_RE.search(text)
    return bool(start) or bool(end)


def is_protected_document(path: Path, text: str) -> bool:
    authority = classify_document_authority(path, text)
    if authority == DOC_AUTHORITY_MANUAL_GOVERNED:
        return True
    return False
