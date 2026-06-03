"""Source-of-truth determination for the Documentation Synchronization Layer.

Follows CONTRACT v4 section 9 (Source-of-Truth Rules) and section 8.1
(Source-of-Truth Hierarchy).  In restricted mode (no upstream policy
or sandbox available) the module returns conservative NEEDS_REVIEW
or BLOCK decisions for any operation on governed documents.
"""

from pathlib import Path


# Hierarchy levels matching CONTRACT v4 § 8.1
SOT_LEVEL_EVIDENCE = 1
SOT_LEVEL_MANIFEST = 2
SOT_LEVEL_CONTRACT = 3
SOT_LEVEL_SPEC = 4
SOT_LEVEL_CODE = 5
SOT_LEVEL_SCHEMA = 6
SOT_LEVEL_TEST = 7
SOT_LEVEL_RUNTIME = 8
SOT_LEVEL_GENERATED = 9
SOT_LEVEL_README = 10

SOT_LEVEL_NAMES = {
    SOT_LEVEL_EVIDENCE: "completion_evidence",
    SOT_LEVEL_MANIFEST: "evidence_manifest",
    SOT_LEVEL_CONTRACT: "controlling_contract",
    SOT_LEVEL_SPEC: "implementation_spec",
    SOT_LEVEL_CODE: "code_files",
    SOT_LEVEL_SCHEMA: "schema_files",
    SOT_LEVEL_TEST: "test_files",
    SOT_LEVEL_RUNTIME: "runtime_evidence",
    SOT_LEVEL_GENERATED: "generated_reports",
    SOT_LEVEL_README: "readme_overview",
}


def determine_source_of_truth(document: dict, context: dict | None = None) -> dict:
    if context is None:
        context = {}

    doc_path = document.get("path", "unknown")
    doc_type = document.get("document_type", "UNKNOWN")
    doc_authority = document.get("authority", "UNKNOWN")

    if doc_type == "CONTRACT":
        level = SOT_LEVEL_CONTRACT
    elif doc_type == "IMPLEMENTATION_SPEC":
        level = SOT_LEVEL_SPEC
    elif doc_type == "REVIEW_DOD":
        level = SOT_LEVEL_EVIDENCE
    elif doc_authority == "RUNTIME_EVIDENCE":
        level = SOT_LEVEL_RUNTIME
    elif doc_type == "EVIDENCE":
        level = SOT_LEVEL_MANIFEST
    elif doc_type == "README":
        level = SOT_LEVEL_README
    elif doc_type == "SCHEMA":
        level = SOT_LEVEL_SCHEMA
    elif doc_type == "TEST":
        level = SOT_LEVEL_TEST
    elif doc_authority == "GENERATED":
        level = SOT_LEVEL_GENERATED
    elif doc_authority == "RUNTIME_EVIDENCE":
        level = SOT_LEVEL_RUNTIME
    else:
        level = SOT_LEVEL_README

    return {
        "document_path": doc_path,
        "source_of_truth_level": level,
        "source_of_truth_name": SOT_LEVEL_NAMES.get(level, "unknown"),
        "source_of_truth_basis": f"determined from document_type={doc_type}, authority={doc_authority}",
    }


def resolve_source_of_truth_conflict(
    sources: list[dict],
    context: dict | None = None,
) -> dict:
    if not sources:
        return {"decision": "NEEDS_REVIEW", "reason": "no source-of-truth references available"}

    best = min(sources, key=lambda s: s.get("source_of_truth_level", SOT_LEVEL_README))

    conflicts = [
        s for s in sources
        if s.get("source_of_truth_level") == best.get("source_of_truth_level")
        and s.get("document_path") != best.get("document_path")
    ]

    return {
        "decision": "ALLOW" if not conflicts else "NEEDS_REVIEW",
        "chosen_source": best,
        "conflicting_sources": conflicts,
        "reason": "single best source" if not conflicts else "multiple sources at same level, needs review",
    }
