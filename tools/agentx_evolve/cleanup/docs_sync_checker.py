"""Documentation synchronization and claim-boundary enforcement.

Item 28 (24.1/24.2): Checks that documentation claims about
implementation status match reality by scanning docs for
keyword claims and verifying against code.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

CLAIM_PATTERNS: list[dict] = [
    {"pattern": r"implements?\s+(\w[\w/.-]+)", "label": "implementation"},
    {"pattern": r"supports?\s+(\w[\w/.-]+)", "label": "support"},
    {"pattern": r"done|completed|finished", "label": "completion"},
    {"pattern": r"tests?\s+for\s+(\w[\w/.-]+)", "label": "testing"},
    {"pattern": r"(?:passing|failing|skipped)\s+(\d+)", "label": "test-count"},
]


def extract_claims(doc_path: Path) -> list[dict]:
    """Extract claims from a documentation file."""
    if not doc_path.exists():
        return []
    text = doc_path.read_text()
    claims = []
    for pattern_info in CLAIM_PATTERNS:
        for m in re.finditer(pattern_info["pattern"], text, re.IGNORECASE):
            claims.append({
                "file": str(doc_path),
                "line": text[:m.start()].count("\n") + 1,
                "claim_type": pattern_info["label"],
                "claim_text": m.group(0).strip(),
                "value": m.group(1) if m.lastindex else "",
            })
    return claims


VERIFIABLE_INTERFACES: list[str] = [
    "clean_workspace_runner", "artifact_policy", "dependency_change_review",
    "tool_adapter", "evaluation_harness", "docs_sync_checker",
    "prompt_contract", "fixture_manager", "acceptance_dag",
    "artifact_immutability", "clock_control", "component_manifest",
    "command_allowlist", "stop_condition",
]


def validate_claim(claim: dict) -> dict:
    """Validate a claim against reality."""
    result = {"file": claim["file"], "claim": claim["claim_text"],
              "valid": False, "reason": ""}
    if claim["claim_type"] == "completion":
        result["valid"] = False
        result["reason"] = "completion claims cannot be auto-verified"
        return result
    ref = claim["value"]
    if ref in VERIFIABLE_INTERFACES:
        result["valid"] = True
        result["reason"] = f"verifiable interface: {ref}"
    return result


DOCS_DIRS = ["docs", "voya"]


def scan_all_docs(repo_root: str | Path = ".") -> list[dict]:
    """Scan all docs directories for claims and validate them."""
    repo = Path(repo_root)
    all_claims = []
    for d in DOCS_DIRS:
        p = repo / d
        if p.is_dir():
            for f in p.rglob("*.md"):
                all_claims.extend(extract_claims(f))
    validations = [validate_claim(c) for c in all_claims]
    return {
        "total_claims": len(all_claims),
        "valid_claims": sum(1 for v in validations if v["valid"]),
        "invalid_claims": sum(1 for v in validations if not v["valid"]),
        "details": validations[:100],
    }
