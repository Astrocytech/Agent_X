"""Generate the Functional Runtime MVP gap discovery report from real search."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_DIR = Path(".agentx-init/reports")
ROOT = Path(__file__).resolve().parent.parent.parent.parent

SEARCH_SCOPE = [
    "Makefile",
    "docs/",
    "tools/agentx_evolve/",
    "tests/",
]

SEARCH_PATTERNS = [
    "TODO",
    "FIXME",
    "stub",
    "placeholder",
    "pass",
    "hardcoded",
    "static PASS",
    "exit_code",
    "replay",
    "overwrite",
    "mutation",
    "source mutation",
    "self promotion",
    "self-promotion",
    "promotion",
    "compatibility",
    "reuse map",
    "validator",
    "deterministic",
    "seed",
    "clock",
    "event log",
    "artifact",
    "evidence",
    "proof",
    "acceptance",
    "report",
    "manifest",
    "hash",
    "sha256",
    "temp",
    "random",
    "datetime.now",
    "time.time",
    "uuid",
    "glob",
    "os.walk",
    "symlink",
    "path traversal",
]

IGNORE_DIRS = {"__pycache__", ".git", ".agentx-init", "node_modules", ".pytest_cache"}


def _should_skip(path: Path) -> bool:
    return any(part.startswith(".") or part in IGNORE_DIRS for part in path.parts)


def _is_text_file(path: Path) -> bool:
    try:
        path.read_bytes()
        return True
    except (OSError, UnicodeDecodeError):
        return False


def scan_files() -> dict[str, list[dict]]:
    """Scan files in SEARCH_SCOPE for SEARCH_PATTERNS, returning matched results."""
    matches: dict[str, list[dict]] = {}
    source_files: set[str] = set()
    documents: set[str] = set()

    for scope_pattern in SEARCH_SCOPE:
        full_path = ROOT / scope_pattern
        if not full_path.exists():
            continue

        if full_path.is_file():
            paths = [full_path]
        else:
            paths = sorted(full_path.rglob("*"))

        for p in paths:
            if p.is_dir() or _should_skip(p) or not _is_text_file(p):
                continue
            rel = str(p.relative_to(ROOT))
            if rel.endswith(".py") or rel.endswith(".sh") or rel.endswith(".md") or rel.endswith(".txt") or rel == "Makefile":
                if rel.startswith("docs/"):
                    documents.add(rel)
                else:
                    source_files.add(rel)

            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            for pattern in SEARCH_PATTERNS:
                for line_no, line in enumerate(text.split("\n"), 1):
                    if pattern.lower() in line.lower():
                        match_entry = {
                            "file": rel,
                            "line": line_no,
                            "context": line.strip()[:150],
                        }
                        if pattern not in matches:
                            matches[pattern] = []
                        matches[pattern].append(match_entry)
                        break  # one match per file per pattern

    return {
        "matches": matches,
        "source_files_inspected": sorted(source_files),
        "documents_inspected": sorted(documents),
    }


def _classify_finding(pattern: str, match_count: int) -> str:
    """Classify a pattern finding based on match context and count."""
    high_signal_patterns = {
        "TODO": "NEEDS_REVIEW",
        "FIXME": "MVP_BLOCKER",
        "stub": "NEEDS_REVIEW",
        "placeholder": "NEEDS_REVIEW",
        "hardcoded": "MVP_BLOCKER",
        "static PASS": "MVP_BLOCKER",
        "overwrite": "MVP_BLOCKER",
        "path traversal": "MVP_BLOCKER",
        "symlink": "MVP_BLOCKER",
        "random": "NEEDS_REVIEW",
        "uuid": "NEEDS_REVIEW",
        "datetime.now": "NEEDS_REVIEW",
    }
    if pattern in high_signal_patterns:
        return high_signal_patterns[pattern]
    if match_count <= 3:
        return "BENIGN"
    return "NEEDS_REVIEW"


def classify_matches(scanned: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """Classify discovered matches into findings with evidence and classification."""
    matches = scanned.get("matches", {})

    known_gaps: list[dict] = [
        {"id": "KG-01", "description": "No streaming execution (all synchronous)", "status": "CONFIRMED"},
        {"id": "KG-02", "description": "No distributed cluster support", "status": "CONFIRMED"},
        {"id": "KG-03", "description": "No persistent queue for inbox", "status": "CONFIRMED"},
    ]

    # Build scan-derived findings with per-pattern classification
    findings: list[dict] = []
    for pattern, match_list in sorted(matches.items(), key=lambda x: -len(x[1])):
        classification = _classify_finding(pattern, len(match_list))
        finding = {
            "finding_id": f"GD-{len(findings) + 1:03d}",
            "pattern": pattern,
            "match_count": len(match_list),
            "classification": classification,
            "rationale": f"Pattern '{pattern}' found {len(match_list)} times. "
                         f"Classification '{classification}' based on pattern semantics and match count.",
            "evidence_refs": [{"file": m["file"], "line": m["line"], "context": m["context"]}
                              for m in match_list[:3]],
        }
        if classification in ("FIXED", "BENIGN") and match_list:
            finding["closure_evidence"] = [f"{m['file']}:{m['line']}" for m in match_list[:3]]
        findings.append(finding)

    new_gaps: list[dict] = []
    for pattern, match_list in sorted(matches.items(), key=lambda x: -len(x[1])):
        ng_id = f"NG-{len(new_gaps) + 1:02d}"
        ng = {
            "id": ng_id,
            "description": f"Pattern '{pattern}' found {len(match_list)} times across codebase",
            "resolution": "OPEN",
            "match_count": len(match_list),
            "evidence_refs": [{"file": m["file"], "line": m["line"], "context": m["context"]} for m in match_list[:3]],
        }
        new_gaps.append(ng)

    suspected_gaps: list[dict] = []
    if matches:
        for pattern, match_list in sorted(matches.items()):
            suspected_gaps.append({
                "id": f"SG-{len(suspected_gaps) + 1:02d}",
                "description": f"Pattern '{pattern}' appeared in codebase",
                "status": "OPEN",
                "match_count": len(match_list),
                "evidence_ref": {"file": match_list[0]["file"], "line": match_list[0]["line"]} if match_list else {},
            })

    out_of_scope = [
        "Multi-node clustering",
        "Persistent message queue",
        "Streaming execution",
    ]

    # Determine provisional classification from findings
    has_blocker = any(f["classification"] == "MVP_BLOCKER" for f in findings)
    has_needs_review = any(f["classification"] == "NEEDS_REVIEW" for f in findings)
    if has_blocker:
        provisional = "FUNCTIONAL_SCAFFOLD_WITH_MVP_VERTICAL_SLICE"
        notes = "MVP_BLOCKER findings present — classification held at scaffold level."
    elif has_needs_review:
        provisional = "FUNCTIONAL_SCAFFOLD_WITH_MVP_VERTICAL_SLICE"
        notes = "NEEDS_REVIEW findings present — classification held at scaffold level until reviewed."
    else:
        provisional = "FUNCTIONAL_RUNTIME_MVP"
        notes = "No MVP_BLOCKER or NEEDS_REVIEW findings. Classification confirmed by scan results."

    return {
        "known_gaps_confirmed": known_gaps,
        "new_gaps_discovered": new_gaps,
        "suspected_gaps": suspected_gaps,
        "out_of_scope": out_of_scope,
        "findings": findings,
        "_provisional_classification": provisional,
        "_classification_notes": notes,
    }


def generate_gap_discovery_report() -> tuple[str, str]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    scanned = scan_files()
    classified = classify_matches(scanned)

    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        git_commit = r.stdout.strip()
    except Exception:
        git_commit = "unknown"

    classification = classified.pop("_provisional_classification", "FUNCTIONAL_SCAFFOLD_WITH_MVP_VERTICAL_SLICE")
    classification_notes = classified.pop("_classification_notes", "Classified from scan results.")

    data = {
        "report_type": "functional_runtime_mvp_gap_discovery_report",
        "classification": classification,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit,
        "search_scope": SEARCH_SCOPE,
        "search_patterns": SEARCH_PATTERNS,
        "documents_inspected": scanned.get("documents_inspected", []),
        "source_files_inspected": scanned.get("source_files_inspected", []),
        "matches": scanned.get("matches", {}),
        **classified,
        "final_pre_implementation_classification": "FUNCTIONAL_SCAFFOLD_WITH_MVP_VERTICAL_SLICE",
        "final_post_implementation_classification": classification,
        "classification_notes": classification_notes,
    }

    js_path = REPORT_DIR / "functional_runtime_mvp_gap_discovery_report.json"
    js_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    md_lines = [
        "# Functional Runtime MVP — Gap Discovery Report",
        "",
        f"**Classification**: {data['classification']}",
        f"**Git commit**: {git_commit}",
        f"**Generated**: {data['created_at']}",
        "",
        "## Search Scope",
    ]
    for s in SEARCH_SCOPE:
        md_lines.append(f"- {s}")
    md_lines.extend(["", "## Search Patterns (" + str(len(SEARCH_PATTERNS)) + " patterns)"])

    md_lines.extend(["", "## Source Files Inspected (" + str(len(scanned.get("source_files_inspected", []))) + " files)"])
    for f in scanned.get("source_files_inspected", [])[:50]:
        md_lines.append(f"- {f}")
    if len(scanned.get("source_files_inspected", [])) > 50:
        md_lines.append(f"- ... and {len(scanned.get('source_files_inspected', [])) - 50} more")

    md_lines.extend(["", "## Documents Inspected (" + str(len(scanned.get("documents_inspected", []))) + " docs)"])
    for d in scanned.get("documents_inspected", []):
        md_lines.append(f"- {d}")

    md_lines.extend(["", "## Known Gaps Confirmed", "| ID | Description | Status |", "|---|---|---|"])
    for g in data["known_gaps_confirmed"]:
        md_lines.append(f"| {g['id']} | {g['description']} | {g['status']} |")

    md_lines.extend(["", "## New Gaps Discovered", "| ID | Description | Resolution |", "|---|---|---|"])
    for g in data["new_gaps_discovered"]:
        md_lines.append(f"| {g['id']} | {g['description']} | {g['resolution']} |")

    md_lines.extend(["", "## Suspected Gaps", "| ID | Description | Status |", "|---|---|---|"])
    for g in data["suspected_gaps"]:
        md_lines.append(f"| {g['id']} | {g['description']} | {g['status']} |")

    md_lines.extend(["", "## Out of Scope", ""] + [f"- {s}" for s in data["out_of_scope"]])

    md_path = REPORT_DIR / "functional_runtime_mvp_gap_discovery_report.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    return str(js_path), str(md_path)


if __name__ == "__main__":
    try:
        js, md = generate_gap_discovery_report()
        print(f"Gap discovery report: {js}")
        print(f"Gap discovery MD: {md}")
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: gap discovery report generation failed: {e}", file=sys.stderr)
        sys.exit(1)
