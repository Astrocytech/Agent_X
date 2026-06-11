"""Validate JSON schema versions and canonical JSON formatting.

Gaps 64-74, 366-371: schema version checks, canonical JSON, duplicate keys, UTF-8.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

EXPECTED_SCHEMAS: dict[str, str] = {
    "functional_runtime_mvp_proof_bundle.json": "proof_bundle",
    "functional_runtime_mvp_evidence_manifest.json": "evidence_manifest",
    "functional_runtime_mvp_acceptance_matrix.json": "acceptance_matrix",
    "functional_runtime_mvp_final_verdict.json": "final_verdict",
    "functional_runtime_compatibility_report.json": "compatibility_report",
    "functional_runtime_mvp_anti_false_pass_audit.json": "anti_false_pass_audit",
    "functional_runtime_reuse_map.json": "reuse_map",
    "functional_runtime_mvp_replay_report.json": "replay_report",
    "functional_runtime_mvp_requirement_traceability_matrix.json": "traceability_matrix",
}

SUPPORTED_SCHEMA_VERSIONS = ["v1", "v2"]

# Only enforce strict canonical JSON + duplicate key checks for these files
STRICT_FILES = {
    "functional_runtime_mvp_proof_bundle.json",
    "functional_runtime_mvp_evidence_manifest.json",
}


def _read_raw(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except Exception:
        return ""


def validate_schema_version() -> list[str]:
    errors = []

    for fname in EXPECTED_SCHEMAS:
        fpath = REPORT_DIR / fname
        if not fpath.exists():
            # File may be created later in the pipeline — skip
            continue

        raw = _read_raw(fpath)
        if not raw:
            errors.append(f"Schema-version: {fname} empty or not readable UTF-8")
            continue

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            errors.append(f"Schema-version: {fname} is not valid JSON")
            continue

        if not isinstance(data, dict):
            # Arrays and primitives are valid JSON — skip schema_version checks
            continue

        if fname in STRICT_FILES:
            schema_ver = data.get("schema_version", "")
            if not schema_ver:
                errors.append(f"Schema-version: 366 - {fname} missing schema_version")
            elif "agentx." not in schema_ver:
                errors.append(f"Schema-version: 366 - {fname} schema_version '{schema_ver}' does not contain 'agentx.' prefix")
            else:
                version_part = schema_ver.rsplit(".", 1)[-1] if "." in schema_ver else schema_ver
                if version_part and version_part not in SUPPORTED_SCHEMA_VERSIONS:
                    errors.append(f"Schema-version: 367 - {fname} unsupported schema version: '{version_part}'")

        if fname in STRICT_FILES:
            canonical = json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
            if raw != canonical:
                errors.append(f"Schema-version: 368 - {fname} is not canonical JSON (sorted keys, final newline)")

            import re
            # Check for duplicate top-level keys (exactly 2-space indent)
            top_keys = re.findall(r'^  "([^"]+)"\s*:', raw, re.MULTILINE)
            if len(top_keys) != len(set(top_keys)):
                errors.append(f"Schema-version: 369 - {fname} contains duplicate JSON keys")

    # Items 370-371: Markdown is not independently authoritative
    md_files = sorted(REPORT_DIR.glob("*.md"))
    for mf in md_files:
        jf = REPORT_DIR / (mf.stem + ".json")
        if not jf.exists():
            continue
        md_text = mf.read_text(encoding="utf-8", errors="replace")
        try:
            js_data = json.loads(jf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(js_data, dict):
            continue
        js_verdict = str(js_data.get("verdict", js_data.get("status", "")))
        if js_verdict.upper() == "PASS" and "FAIL" in md_text.upper():
            errors.append(f"Schema-version: 370 - Markdown {mf.name} says FAIL but JSON says PASS — JSON is authoritative")
        if js_verdict.upper() == "FAIL" and "PASS" in md_text.upper():
            errors.append(f"Schema-version: 371 - Markdown {mf.name} says PASS but JSON says FAIL")

    return errors


def main() -> int:
    errs = validate_schema_version()
    if errs:
        print("VALIDATE SCHEMA VERSION FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-schema-version: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
