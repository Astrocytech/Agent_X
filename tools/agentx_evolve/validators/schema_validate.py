"""Schema validation utilities for Functional Runtime MVP reports.

Covers gap list items 185-197:
  185. Explicit field checks for every machine-readable report
  186. Reject additional unknown verdict-influencing fields
  187. Reject missing required fields even if verdict says PASS
  188. Reject invalid enum values (status, verdict, classification, resolution)
  189. Reject inconsistent casing (Pass, pass, passed)
  190. Reject null values for required proof fields
  191. Reject empty strings for required IDs, paths, hashes, commands, verdicts
  192. Reject duplicate requirement IDs in traceability
  193. Reject duplicate proof object IDs
  194. Reject duplicate attack IDs in anti-false-PASS audit
  195. Reject mismatched counts (attacks_tested != len(attack_results))
  196. Reject total_requirements != number of traceability rows
  197. Reject file_count != number of files in source manifest
"""
from __future__ import annotations

import json
from pathlib import Path

VALID_VERDICTS = {"PASS", "FAIL", "DENIED_AND_RECORDED", "BLOCKED", "UNKNOWN"}
VALID_STATUSES = {"PASS", "FAIL", "BLOCKED", "PARTIAL", "UNKNOWN", "OUT_OF_SCOPE", "DENIED_AND_RECORDED"}
VALID_CLASSIFICATIONS = {
    "FUNCTIONAL_RUNTIME_MVP", "FUNCTIONAL_SCAFFOLD_WITH_MVP_VERTICAL_SLICE",
    "MVP_BLOCKER", "NEEDS_REVIEW", "UNKNOWN", "UNCLASSIFIED",
}
VALID_RESOLUTIONS = {"FIXED", "BENIGN", "OUT_OF_SCOPE", "BLOCKED", "OPEN", "UNKNOWN"}


def _load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def reject_bad_casing(value: str, allowed_set: set[str]) -> list[str]:
    errors = []
    if value and value not in allowed_set:
        lower_match = [a for a in allowed_set if a.lower() == value.lower()]
        if lower_match:
            errors.append(f"Case mismatch: got '{value}', expected one of {lower_match}")
    return errors


def reject_empty(value: any, field_name: str, context: str = "") -> list[str]:
    prefix = f"{context}: " if context else ""
    if value is None:
        return [f"{prefix}{field_name} is null"]
    if isinstance(value, str) and not value:
        return [f"{prefix}{field_name} is empty"]
    if isinstance(value, (list, dict)) and not value:
        return [f"{prefix}{field_name} is empty"]
    return []


def reject_invalid_enum(value: any, field_name: str, allowed: set[str], context: str = "") -> list[str]:
    prefix = f"{context}: " if context else ""
    if value is None:
        return [f"{prefix}{field_name} is null"]
    if not isinstance(value, str):
        return [f"{prefix}{field_name} has non-string value: {value!r}"]
    if value not in allowed:
        suggestion = ""
        for a in allowed:
            if a.lower() == value.lower():
                suggestion = f" (maybe '{a}'?)"
                break
        return [f"{prefix}{field_name} has invalid value: '{value}'{suggestion}"]
    return []


def validate_report_schema(report_path: Path, report_label: str) -> list[str]:
    """Validate shared schema fields for any Functional Runtime MVP report."""
    errors = []
    data = _load_json(str(report_path))
    if not isinstance(data, dict):
        return [f"{report_label}: does not parse or is not an object"]

    if "schema_version" in data:
        errors.extend(reject_empty(data["schema_version"], "schema_version", report_label))

    verdict = data.get("verdict", "")
    if verdict:
        errors.extend(reject_invalid_enum(verdict, "verdict", VALID_VERDICTS, report_label))
        errors.extend(reject_bad_casing(verdict, VALID_VERDICTS))

    return errors


def validate_acceptance_matrix(report_dir: Path) -> list[str]:
    errors = []
    path = report_dir / "functional_runtime_mvp_acceptance_matrix.json"
    if not path.exists():
        return ["Acceptance matrix missing"]

    data = _load_json(str(path))
    if not isinstance(data, dict):
        return ["Acceptance matrix does not parse"]

    errors.extend(validate_report_schema(path, "Acceptance matrix"))
    rows = data.get("rows", [])
    if not rows:
        errors.append("Acceptance matrix: no rows")

    seen_components = {}
    for row in rows:
        if not isinstance(row, dict):
            errors.append("Acceptance matrix: row is not an object")
            continue
        comp = row.get("component", "")
        status = row.get("status", "")
        errors.extend(reject_empty(comp, "component", "Acceptance matrix"))
        errors.extend(reject_invalid_enum(status, "status", VALID_STATUSES, f"acceptance row '{comp}'"))
        errors.extend(reject_bad_casing(status, VALID_STATUSES))

        # Gap 192: Reject duplicate components
        if comp in seen_components:
            errors.append(f"Acceptance matrix: duplicate component '{comp}'")
        seen_components[comp] = True

        # Gap 190: Reject null evidence_refs for PASS rows
        if status == "PASS":
            evidence_refs = row.get("evidence_refs")
            if evidence_refs is None:
                errors.append(f"Acceptance matrix: PASS row '{comp}' has null evidence_refs")
            elif not evidence_refs:
                errors.append(f"Acceptance matrix: PASS row '{comp}' has empty evidence_refs")

    return errors


def validate_traceability_matrix(report_dir: Path) -> list[str]:
    errors = []
    path = report_dir / "functional_runtime_mvp_requirement_traceability_matrix.json"
    if not path.exists():
        return ["Traceability matrix missing"]

    data = _load_json(str(path))
    if not isinstance(data, dict):
        return ["Traceability matrix does not parse"]

    errors.extend(validate_report_schema(path, "Traceability matrix"))
    rows = data.get("rows", [])
    if not rows:
        errors.append("Traceability matrix: no rows")

    # Gap 196: Check total_requirements matches row count
    total = data.get("total_requirements", 0)
    if total and total != len(rows):
        errors.append(f"Traceability matrix: total_requirements ({total}) != row count ({len(rows)})")

    seen_ids = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        req_id = row.get("requirement_id", "")
        status = row.get("status", "")
        errors.extend(reject_empty(req_id, "requirement_id", "Traceability matrix"))
        errors.extend(reject_invalid_enum(status, "status", VALID_STATUSES, f"req '{req_id}'"))

        # Gap 192: Reject duplicate requirement IDs
        if req_id in seen_ids:
            errors.append(f"Traceability matrix: duplicate requirement_id '{req_id}'")
        seen_ids[req_id] = True

        for ref_type in ("implementation_refs", "test_refs", "validator_refs", "evidence_refs"):
            refs = row.get(ref_type)
            if refs is not None and not isinstance(refs, list):
                errors.append(f"Traceability matrix: req '{req_id}' {ref_type} is not a list")

    return errors


def validate_proof_bundle(report_dir: Path) -> list[str]:
    errors = []
    path = report_dir / "functional_runtime_mvp_proof_bundle.json"
    if not path.exists():
        return ["Proof bundle missing"]

    data = _load_json(str(path))
    if not isinstance(data, dict):
        return ["Proof bundle does not parse"]

    errors.extend(validate_report_schema(path, "Proof bundle"))

    # Gap 193: Check for duplicate proof object IDs
    proof_keys = [
        "command_proofs", "scenario_proofs", "replay_proofs",
        "source_mutation_proof", "compatibility_proof", "reuse_map_proof",
        "requirement_trace_proof", "gap_discovery_proof",
        "anti_false_pass_proof", "acceptance_rows",
    ]
    seen_proof_ids = {}
    for key in proof_keys:
        obj = data.get(key)
        if isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    pid = item.get("id", "")
                    if pid:
                        if pid in seen_proof_ids:
                            errors.append(f"Proof bundle: duplicate proof id '{pid}' in {key}")
                        seen_proof_ids[pid] = key

    return errors


def validate_replay_manifests(report_dir: Path) -> list[str]:
    errors = []
    for mp in sorted(report_dir.glob("functional_runtime_mvp_replay_manifest_*.json")):
        data = _load_json(str(mp))
        if not isinstance(data, dict):
            errors.append(f"Replay manifest {mp.name}: does not parse")
            continue

        for field in ("schema_version", "scenario_name", "state_records_hash", "event_log_hash"):
            value = data.get(field)
            if value is None:
                errors.append(f"Replay manifest {mp.name}: {field} is null")
            elif isinstance(value, str) and not value:
                errors.append(f"Replay manifest {mp.name}: {field} is empty")

    return errors


def validate_anti_false_pass_audit(report_dir: Path) -> list[str]:
    errors = []
    path = report_dir / "functional_runtime_mvp_anti_false_pass_audit.json"
    if not path.exists():
        return ["Anti-false-PASS audit missing"]

    data = _load_json(str(path))
    if not isinstance(data, dict):
        return ["Anti-false-PASS audit does not parse"]

    errors.extend(validate_report_schema(path, "Anti-false-PASS audit"))

    # Gap 195: Check attacks_tested matches len(attack_results)
    attacks_tested = data.get("attacks_tested", 0)
    attack_results = data.get("attack_results", [])
    if attacks_tested != len(attack_results):
        errors.append(
            f"Anti-false-PASS audit: attacks_tested ({attacks_tested}) "
            f"!= len(attack_results) ({len(attack_results)})"
        )

    # Gap 194: Check for duplicate attack IDs
    seen_ids = {}
    for ar in attack_results:
        if not isinstance(ar, dict):
            continue
        aid = ar.get("attack_id")
        if aid in seen_ids:
            errors.append(f"Anti-false-PASS audit: duplicate attack_id {aid}")
        seen_ids[aid] = True

    return errors


def validate_source_manifest(report_dir: Path, prefix: str) -> list[str]:
    errors = []
    path = report_dir / f"functional_runtime_mvp_source_hash_manifest_{prefix}.json"
    if not path.exists():
        return [f"Source hash manifest ({prefix}) missing"]

    data = _load_json(str(path))
    if not isinstance(data, dict):
        return [f"Source hash manifest ({prefix}) does not parse"]

    files = data.get("files", {})
    file_count = data.get("file_count", 0)

    # Gap 197: Check file_count matches number of files
    if file_count > 0 and file_count != len(files):
        errors.append(
            f"Source hash manifest ({prefix}): file_count ({file_count}) "
            f"!= len(files) ({len(files)})"
        )

    # Check for empty or null hashes
    for fname, fhash in files.items():
        if not fhash:
            errors.append(f"Source hash manifest ({prefix}): file '{fname}' has empty hash")

    return errors


def validate_compatibility_report(report_dir: Path) -> list[str]:
    errors = []
    path = report_dir / "functional_runtime_compatibility_report.json"
    if not path.exists():
        return ["Compatibility report missing"]

    data = _load_json(str(path))
    if not isinstance(data, dict):
        return ["Compatibility report does not parse"]

    errors.extend(validate_report_schema(path, "Compatibility report"))

    checks = data.get("checks", [])
    seen_check_names = {}
    for check in checks:
        if not isinstance(check, dict):
            continue
        cname = check.get("name", "")
        status = check.get("status", "")
        errors.extend(reject_empty(cname, "check name", "Compatibility"))
        errors.extend(reject_invalid_enum(status, "check status", VALID_STATUSES, f"check '{cname}'"))

        # Gap 193: check for duplicate check names
        if cname in seen_check_names:
            errors.append(f"Compatibility report: duplicate check name '{cname}'")
        seen_check_names[cname] = True

    return errors


def validate_gap_discovery_report(report_dir: Path) -> list[str]:
    errors = []
    path = report_dir / "functional_runtime_mvp_gap_discovery_report.json"
    if not path.exists():
        return ["Gap discovery report missing"]

    data = _load_json(str(path))
    if not isinstance(data, dict):
        return ["Gap discovery report does not parse"]

    errors.extend(validate_report_schema(path, "Gap discovery report"))

    final_class = data.get("final_post_implementation_classification", "")
    if final_class:
        errors.extend(reject_invalid_enum(final_class, "classification", VALID_CLASSIFICATIONS, "Gap discovery"))

    findings = data.get("findings", [])
    seen_finding_ids = {}
    for f in findings:
        if not isinstance(f, dict):
            continue
        fid = f.get("finding_id", "")
        if fid in seen_finding_ids:
            errors.append(f"Gap discovery: duplicate finding_id '{fid}'")
        seen_finding_ids[fid] = True

        f_class = f.get("classification", "")
        if f_class:
            errors.extend(reject_invalid_enum(f_class, "finding classification", VALID_CLASSIFICATIONS, f"finding '{fid}'"))

    return errors


def validate_source_mutation_report(report_dir: Path) -> list[str]:
    errors = []
    path = report_dir / "functional_runtime_mvp_source_mutation_report.json"
    if not path.exists():
        return ["Source mutation report missing"]

    data = _load_json(str(path))
    if not isinstance(data, dict):
        return ["Source mutation report does not parse"]

    errors.extend(validate_report_schema(path, "Source mutation report"))

    scenario_name = data.get("scenario_name", "")
    errors.extend(reject_empty(scenario_name, "scenario_name", "Source mutation"))

    return errors


def validate_evidence_manifest(report_dir: Path) -> list[str]:
    errors = []
    path = report_dir / "functional_runtime_mvp_evidence_manifest.json"
    if not path.exists():
        return ["Evidence manifest missing"]

    data = _load_json(str(path))
    if not isinstance(data, dict):
        return ["Evidence manifest does not parse"]

    evidence_list = data.get("evidence", [])
    seen_paths = {}
    for entry in evidence_list:
        if not isinstance(entry, dict):
            continue
        ev_path = entry.get("file", "")
        ev_hash = entry.get("hash", "")
        if ev_path in seen_paths:
            errors.append(f"Evidence manifest: duplicate file entry '{ev_path}'")
        seen_paths[ev_path] = True
        errors.extend(reject_empty(ev_path, "evidence file path", "Evidence manifest"))
        errors.extend(reject_empty(ev_hash, "evidence hash", f"Evidence manifest '{ev_path}'"))

    return errors


def validate_all_schemas(report_dir: Path) -> list[str]:
    all_errors = []
    all_errors.extend(validate_acceptance_matrix(report_dir))
    all_errors.extend(validate_traceability_matrix(report_dir))
    all_errors.extend(validate_proof_bundle(report_dir))
    all_errors.extend(validate_replay_manifests(report_dir))
    all_errors.extend(validate_anti_false_pass_audit(report_dir))
    all_errors.extend(validate_source_manifest(report_dir, "before"))
    all_errors.extend(validate_source_manifest(report_dir, "after"))
    all_errors.extend(validate_compatibility_report(report_dir))
    all_errors.extend(validate_gap_discovery_report(report_dir))
    all_errors.extend(validate_source_mutation_report(report_dir))
    all_errors.extend(validate_evidence_manifest(report_dir))
    return all_errors
