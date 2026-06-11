"""Validate deep proof concerns: side-effect, file-watch, state-reconstruction,
intent-preservation, final-gate, legacy, consumer/producer, error, invalid-proof,
bootstrap, liveness, assumption, claim-downgrade, strength, budget, red-team,
metamorphic, equivalence, temporal, normalization, roundtrip, minimization,
recovery, contract-test, static-analysis, call-graph, data-flow, taint, regex.

Gaps 1401-1800.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from agentx_evolve.validators.common import (
    COVERED_BY_MANUAL_CHECK,
    check_all_gap_items,
    parse_report_dir,
)

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1
ROOT = Path(__file__).resolve().parent.parent.parent.parent


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def _sha256(path: str) -> str:
    try:
        import hashlib
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return ""


def validate_deep() -> list[str]:
    errors = []

    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(bundle, dict):
        bundle = {}

    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))
    if not isinstance(transcript, list):
        transcript = []

    source_before = load_json(str(REPORT_DIR / "functional_runtime_mvp_source_hash_manifest_before.json"))
    source_after = load_json(str(REPORT_DIR / "functional_runtime_mvp_source_hash_manifest_after.json"))

    acceptance_dir = ROOT / "tools" / "agentx_evolve" / "acceptance"
    validators_dir = ROOT / "tools" / "agentx_evolve" / "validators"
    makefile_path = ROOT / "Makefile"

    # Gap 1405-1414: Side-effect — detect files generated outside report dir
    known_generators = [
        acceptance_dir / "run_anti_false_pass_audit.py",
        acceptance_dir / "generate_acceptance_matrix.py",
        acceptance_dir / "generate_requirement_traceability_matrix.py",
    ]
    for gen in known_generators:
        if gen.exists():
            content = gen.read_bytes()
            if b"sys.argv" in content or b"open(" in content or b"write(" in content:
                errors.append(f"Deep: 1405 - side-effect generator {gen.name} uses sys.argv/open/write")

    # Gap 1415-1424: File-watch — check .gitignore covers generated files
    gitignore_path = ROOT / ".gitignore"
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text(encoding="utf-8")
        generated_paths = [".agentx-init/reports", "*.pyc", "__pycache__/"]
        missing_entries = [gp for gp in generated_paths if gp not in gitignore_content]
        if missing_entries:
            errors.append(f"Deep: 1415 - .gitignore missing entries: {', '.join(missing_entries)}")

    # Gap 1425-1434: State-reconstruction
    state_rec = bundle.get("state_reconstruction", None)
    if not state_rec:
        errors.append("Deep: 1425 - state_reconstruction metadata missing from proof bundle")
    state_file = load_json(str(REPORT_DIR / "functional_runtime_mvp_state.json"))
    if isinstance(state_file, dict):
        state_entries = state_file.get("rows", state_file.get("states", state_file.get("entries", [])))
        if isinstance(state_entries, list):
            missing_keys_total = 0
            for se in state_entries:
                if isinstance(se, dict):
                    for key in ("transition", "from_state", "to_state", "event", "timestamp"):
                        if key not in se:
                            missing_keys_total += 1
            if missing_keys_total > 0:
                errors.append(f"Deep: 1425 - {missing_keys_total} state entries missing required keys")

    # Gap 1435-1444: Intent-preservation — scenario name consistency
    matrix = load_json(str(REPORT_DIR / "functional_runtime_mvp_acceptance_matrix.json"))
    trace = load_json(str(REPORT_DIR / "functional_runtime_mvp_requirement_traceability_matrix.json"))
    if isinstance(matrix, dict) and isinstance(trace, dict):
        matrix_scenarios = {r.get("scenario", r.get("id", "")) for r in matrix.get("rows", []) if isinstance(r, dict)}
        trace_scenarios = {r.get("scenario", r.get("requirement_id", "")) for r in trace.get("rows", []) if isinstance(r, dict)}
        for s in matrix_scenarios:
            if s and s not in trace_scenarios:
                errors.append(f"Deep: 1435 - scenario {s} in acceptance matrix but not in traceability")
        for s in trace_scenarios:
            if s and s not in matrix_scenarios:
                errors.append(f"Deep: 1435 - scenario {s} in traceability but not in acceptance matrix")

    # Gap 1445-1454: Final-gate
    verdict = load_json(str(REPORT_DIR / "functional_runtime_mvp_final_verdict.json"))
    if isinstance(verdict, dict):
        classification = verdict.get("classification", "")
        final_gate = verdict.get("final_gate", verdict.get("gate", verdict.get("status", "")))
        if not classification:
            errors.append("Deep: 1445 - final verdict missing classification for final gate")
        if not final_gate:
            errors.append("Deep: 1445 - final verdict missing final_gate field")
        git_commit = verdict.get("git_commit", "")
        if not git_commit:
            errors.append("Deep: 1445 - final verdict missing git_commit for gate binding")
    else:
        errors.append("Deep: 1445 - final verdict missing")

    evidence_manifest = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))

    # Gap 1455-1464: Legacy-artifact
    all_reports = sorted(REPORT_DIR.glob("*.json"))
    for f in all_reports:
        data = load_json(str(f))
        if isinstance(data, dict):
            if "legacy" in f.stem.lower() or "old" in f.stem.lower():
                errors.append(f"Deep: 1455 - legacy/old report in final dir: {f.name}")

    # Gap 1465-1474: Report-consumer — validators exist and cover reports
    if validators_dir.exists():
        validator_files = sorted(validators_dir.glob("validate_*.py"))
        if not validator_files:
            errors.append("Deep: 1465 - no validator files found")
        else:
            report_stems = {f.stem.replace("functional_runtime_mvp_", "") for f in all_reports}
            uncovered = []
            for rs in sorted(report_stems):
                refs = [v for v in validator_files if rs.replace("_", "") in v.stem.replace("_", "")]
                if not refs:
                    uncovered.append(rs)
            if uncovered:
                errors.append(f"Deep: 1465 - reports with no validator reference: {', '.join(uncovered)}")
    else:
        errors.append("Deep: 1465 - validators directory not found")

    # Gap 1475-1484: Report-producer — generators exist
    producer_found = False
    if acceptance_dir.exists():
        generators = list(acceptance_dir.glob("*generate*.py")) + list(acceptance_dir.glob("*collect*.py"))
        if generators:
            producer_found = True
    if not producer_found:
        errors.append("Deep: 1475 - no report generators found in acceptance directory")

    # Gap 1485-1494: Runtime-error — check transcript for nonzero exit codes
    transcript_commands = [c for c in transcript if isinstance(c, dict)]
    failed_commands = [c for c in transcript_commands if c.get("exit_code", 0) != 0]
    if failed_commands:
        for fc in failed_commands:
            cmd_text = str(fc.get("command", ""))[:80]
            if not fc.get("acknowledged", fc.get("expected", False)):
                errors.append(f"Deep: 1485 - unacknowledged runtime error: {cmd_text} (exit {fc.get('exit_code')})")

    # Gap 1495-1504: Invalid-proof — detect corrupted source files
    if isinstance(source_before, dict) and isinstance(source_after, dict):
        before_files = source_before.get("files", source_before.get("hashes", {}))
        after_files = source_after.get("files", source_after.get("hashes", {}))
        for fpath, h2 in after_files.items():
            h1 = before_files.get(fpath) if isinstance(before_files, dict) else None
            if h1 and h1 != h2:
                errors.append(f"Deep: 1495 - source file changed during proof: {fpath}")

    # Gap 1505-1514: Proof-bootstrap
    bootstrap = bundle.get("bootstrap", None)
    if not bootstrap:
        errors.append("Deep: 1505 - bootstrap metadata missing from proof bundle")
    if makefile_path.exists():
        mk_content = makefile_path.read_text(encoding="utf-8")
        if "bootstrap" not in mk_content and "init" not in mk_content:
            errors.append("Deep: 1505 - Makefile has no bootstrap or init target")

    # Gap 1515-1524: Evidence-liveness — check evidence files exist
    if isinstance(evidence_manifest, dict):
        evidence_files = evidence_manifest.get("evidence", evidence_manifest.get("files", []))
        if isinstance(evidence_files, list):
            for ev in evidence_files:
                if isinstance(ev, dict):
                    ev_path = ev.get("path", "")
                    if ev_path:
                        ev_full = REPORT_DIR / ev_path if not os.path.isabs(str(ev_path)) else Path(str(ev_path))
                        if not ev_full.exists():
                            errors.append(f"Deep: 1515 - evidence file referenced but missing: {ev_path}")
    else:
        errors.append("Deep: 1515 - evidence manifest missing for liveness check")

    # Gap 1525-1534: Assumption-register
    assumptions = bundle.get("assumptions", bundle.get("assumption_register", None))
    if not assumptions:
        errors.append("Deep: 1525 - assumptions metadata missing from proof bundle")
    if validators_dir.exists():
        for vf in sorted(validators_dir.glob("validate_*.py")):
            try:
                txt = vf.read_text(encoding="utf-8")
                if "assume" in txt.lower() and "bundle.get" not in txt:
                    errors.append(f"Deep: 1525 - inline assumption in {vf.name} without bundle-registered metadata")
            except (OSError, UnicodeDecodeError):
                errors.append(f"Deep: 1525 - cannot read validator file {vf.name}")

    # Gap 1535-1544: Claim-downgrade
    downgrade = bundle.get("claim_downgrade", None)
    if not downgrade:
        errors.append("Deep: 1535 - claim_downgrade metadata missing from proof bundle")
    if isinstance(verdict, dict):
        v_status = verdict.get("classification", verdict.get("status", "")).upper()
        if v_status in ("PASS", "FUNCTIONAL_RUNTIME_MVP"):
            if isinstance(evidence_manifest, dict):
                ev_files = evidence_manifest.get("evidence", evidence_manifest.get("files", []))
                if isinstance(ev_files, list):
                    failing_ev = [e for e in ev_files if isinstance(e, dict) and str(e.get("status", "")).upper() == "FAIL"]
                    if failing_ev:
                        errors.append(f"Deep: 1535 - verdict is PASS but {len(failing_ev)} evidence items have FAIL status")

    # Gap 1545-1554: Evidence-strength
    if isinstance(bundle, dict):
        strength = bundle.get("evidence_strength", None)
        if not strength:
            errors.append("Deep: 1545 - evidence_strength metadata missing from proof bundle")

    # Gap 1555-1564: Proof-budget
    budget = bundle.get("proof_budget", bundle.get("budget", None))
    if not budget:
        errors.append("Deep: 1555 - proof_budget metadata missing from proof bundle")
    if isinstance(transcript, list) and len(transcript) >= 2:
        start_ts = transcript[0].get("timestamp", transcript[0].get("ts", transcript[0].get("time", "")))
        end_ts = transcript[-1].get("timestamp", transcript[-1].get("ts", transcript[-1].get("time", "")))
        if start_ts and end_ts and isinstance(start_ts, str) and isinstance(end_ts, str) and start_ts >= end_ts:
            errors.append("Deep: 1555 - transcript timestamps out of order (start >= end)")

    # Gap 1565-1574: Red-team
    red_team = bundle.get("red_team", None)
    if not red_team:
        errors.append("Deep: 1565 - red_team metadata missing from proof bundle")
    antifp_path = acceptance_dir / "run_anti_false_pass_audit.py"
    if not antifp_path.exists():
        errors.append("Deep: 1565 - anti-false-pass audit generator missing (red-team mechanism)")

    # Gap 1575-1584: Metamorphic
    metamorphic = bundle.get("metamorphic", None)
    if not metamorphic:
        errors.append("Deep: 1575 - metamorphic metadata missing from proof bundle")

    # Gap 1585-1594: Equivalence
    equivalence = bundle.get("equivalence", None)
    if not equivalence:
        errors.append("Deep: 1585 - equivalence metadata missing from proof bundle")
    if isinstance(source_before, dict) and isinstance(source_after, dict):
        before_keys = set(source_before.get("files", source_before.get("hashes", {})).keys())
        after_keys = set(source_after.get("files", source_after.get("hashes", {})).keys())
        if before_keys != after_keys:
            added = after_keys - before_keys
            removed = before_keys - after_keys
            if added:
                errors.append(f"Deep: 1585 - files added during proof: {', '.join(list(added)[:5])}")
            if removed:
                errors.append(f"Deep: 1585 - files removed during proof: {', '.join(list(removed)[:5])}")

    # Gap 1595-1604: Temporal-consistency
    temporal = bundle.get("temporal_consistency", None)
    if not temporal:
        errors.append("Deep: 1595 - temporal_consistency metadata missing from proof bundle")
    if isinstance(transcript, list) and len(transcript) > 1:
        timestamps_ok = True
        for i, cmd in enumerate(transcript[1:], 1):
            ts = cmd.get("timestamp", cmd.get("ts", cmd.get("time", "")))
            prev_ts = transcript[i-1].get("timestamp", transcript[i-1].get("ts", transcript[i-1].get("time", "")))
            if ts and prev_ts and isinstance(ts, str) and isinstance(prev_ts, str) and ts < prev_ts:
                timestamps_ok = False
                break
        if not timestamps_ok:
            errors.append("Deep: 1595 - transcript timestamps out of order")

    # Gap 1605-1614: Evidence-normalization
    normalization = bundle.get("evidence_normalization", None)
    if not normalization:
        errors.append("Deep: 1605 - evidence_normalization metadata missing from proof bundle")
    for rf in sorted(REPORT_DIR.glob("*.json")):
        try:
            raw = rf.read_bytes()
            json.loads(raw)
            json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            errors.append(f"Deep: 1605 - {rf.name} cannot be parsed consistently")

    # Gap 1615-1624: Schema-roundtrip
    roundtrip = bundle.get("schema_roundtrip", None)
    if not roundtrip:
        errors.append("Deep: 1615 - schema_roundtrip metadata missing from proof bundle")

    # Gap 1625-1634: Evidence-minimization
    minimization = bundle.get("evidence_minimization", None)
    if not minimization:
        errors.append("Deep: 1625 - evidence_minimization metadata missing from proof bundle")
    for rf in sorted(REPORT_DIR.glob("*.json")):
        if rf.stat().st_size > 10 * 1024 * 1024:
            errors.append(f"Deep: 1625 - oversized report (>10MB): {rf.name} ({rf.stat().st_size} bytes)")

    # Gap 1635-1644: Recovery-from-validation-failure
    recovery = bundle.get("recovery_from_validation_failure", None)
    if not recovery:
        errors.append("Deep: 1635 - recovery_from_validation_failure metadata missing from proof bundle")
    if isinstance(transcript, list):
        for i, cmd in enumerate(transcript):
            if isinstance(cmd, dict) and cmd.get("exit_code", 0) != 0:
                if i + 1 < len(transcript):
                    next_cmd = transcript[i + 1]
                    if isinstance(next_cmd, dict):
                        next_text = str(next_cmd.get("command", ""))
                        curr_text = str(cmd.get("command", ""))
                        if curr_text in next_text:
                            errors.append(f"Deep: 1635 - retry detected after failure: {curr_text[:60]}")

    # Gap 1645-1654: Proof-contract test
    contract_test = bundle.get("proof_contract_test", None)
    if not contract_test:
        errors.append("Deep: 1645 - proof_contract_test metadata missing from proof bundle")

    # Gap 1655-1664: Static-analysis
    static_info = bundle.get("static_analysis", None)
    if not static_info:
        errors.append("Deep: 1655 - static_analysis metadata missing from proof bundle")

    # Gap 1665-1674: Call-graph
    call_graph = bundle.get("call_graph", None)
    if not call_graph:
        errors.append("Deep: 1665 - call_graph metadata missing from proof bundle")

    # Gap 1675-1684: Data-flow
    data_flow = bundle.get("data_flow", None)
    if not data_flow:
        errors.append("Deep: 1675 - data_flow metadata missing from proof bundle")

    # Gap 1685-1694: Taint-tracking
    taint = bundle.get("taint_tracking", None)
    if not taint:
        errors.append("Deep: 1685 - taint_tracking metadata missing from proof bundle")

    # Gap 1695-1704: Regex-safety
    regex_safety = bundle.get("regex_safety", None)
    if not regex_safety:
        errors.append("Deep: 1695 - regex_safety metadata missing from proof bundle")
    if validators_dir.exists():
        for vf in sorted(validators_dir.glob("validate_*.py")):
            try:
                txt = vf.read_text(encoding="utf-8")
                if "re.compile" in txt and "(.*?)" in txt:
                    errors.append(f"Deep: 1695 - dangerous regex in {vf.name}")
            except (OSError, UnicodeDecodeError):
                pass

    # Gap 1705-1714: Pytest-configuration
    pyproject_path = ROOT / "pyproject.toml"
    if pyproject_path.exists():
        pyproject_text = pyproject_path.read_text(encoding="utf-8")
        if "[tool.pytest" not in pyproject_text and "pytest" not in pyproject_text:
            errors.append("Deep: 1705 - pyproject.toml missing pytest configuration")
    conftest_paths = list(ROOT.rglob("conftest.py"))
    if not conftest_paths:
        errors.append("Deep: 1705 - no conftest.py found in repository")

    # Gap 1715-1724: Test-quality
    if isinstance(bundle, dict):
        test_quality = bundle.get("test_quality", None)
        if not test_quality:
            errors.append("Deep: 1715 - test_quality metadata missing from proof bundle")

    # Gap 1725-1734: Assertion-sensitivity
    assertion_sens = bundle.get("assertion_sensitivity", None)
    if not assertion_sens:
        errors.append("Deep: 1725 - assertion_sensitivity metadata missing from proof bundle")
    if validators_dir.exists():
        for vf in sorted(validators_dir.glob("validate_*.py")):
            try:
                txt = vf.read_text(encoding="utf-8")
                if "errors.append(" in txt and "else:" in txt:
                    errors.append(f"Deep: 1725 - {vf.name} uses else: with errors.append() which may mask silent passes")
            except (OSError, UnicodeDecodeError):
                pass

    # Gap 1735-1744: Mutation-score
    mutation = bundle.get("mutation_score", None)
    if not mutation:
        errors.append("Deep: 1735 - mutation_score metadata missing from proof bundle")

    # Gap 1745-1754: Lineage
    lineage = bundle.get("lineage", None)
    if not lineage:
        errors.append("Deep: 1745 - lineage metadata missing from proof bundle")
    if isinstance(evidence_manifest, dict):
        ev_files = evidence_manifest.get("evidence", evidence_manifest.get("files", []))
        if isinstance(ev_files, list):
            missing_source = 0
            for ev in ev_files:
                if isinstance(ev, dict):
                    if not ev.get("source") and not ev.get("origin") and not ev.get("generator"):
                        missing_source += 1
            if missing_source > 0:
                errors.append(f"Deep: 1745 - {missing_source} evidence entries missing source/origin/generator")

    # Gap 1755-1764: Identity-resolution
    identity = bundle.get("identity_resolution", None)
    if not identity:
        errors.append("Deep: 1755 - identity_resolution metadata missing from proof bundle")

    # Gap 1765-1774: Authorization-boundary
    auth_boundary = bundle.get("authorization_boundary", None)
    if not auth_boundary:
        errors.append("Deep: 1765 - authorization_boundary metadata missing from proof bundle")

    # Gap 1775-1784: Policy-conflict
    policy_conflict = bundle.get("policy_conflict", None)
    if not policy_conflict:
        errors.append("Deep: 1775 - policy_conflict metadata missing from proof bundle")

    # Gap 1785-1794: Artifact-content — zero-byte check
    ev_man = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    if isinstance(ev_man, dict):
        ev_files = ev_man.get("evidence", ev_man.get("files", []))
        if isinstance(ev_files, list):
            for ev in ev_files:
                if isinstance(ev, dict):
                    ev_path = ev.get("path", "")
                    if ev_path:
                        ev_full = REPORT_DIR / ev_path if not os.path.isabs(str(ev_path)) else Path(str(ev_path))
                        if ev_full.exists() and ev_full.stat().st_size == 0:
                            errors.append(f"Deep: 1785 - zero-byte evidence artifact: {ev_path}")

    # Gap 1795-1804: External-process — complete exit codes
    transcript_entries = transcript if isinstance(transcript, list) else []
    for cmd in transcript_entries:
        if isinstance(cmd, dict):
            ec = cmd.get("exit_code", -1)
            if ec < 0:
                errors.append("Deep: 1795 - command transcript entry missing exit_code: " + str(cmd.get("command", ""))[:80])

    # Check git dirty state
    try:
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10)
        dirty = [l for l in r.stdout.strip().split("\n") if l.strip()]
        if dirty:
            errors.append(f"Deep: dirty working tree with {len(dirty)} uncommitted changes")
    except Exception as exc:
        errors.append(f"Deep: git status check failed: {exc}")

    # Source manifest comparison: before vs after
    if isinstance(source_before, dict) and isinstance(source_after, dict):
        before_files = source_before.get("files", source_before.get("hashes", {}))
        after_files = source_after.get("files", source_after.get("hashes", {}))
        if isinstance(before_files, dict) and isinstance(after_files, dict):
            for fpath, h1 in before_files.items():
                h2 = after_files.get(fpath)
                if h2 and h1 != h2:
                    errors.append(f"Deep: source file hash changed during proof: {fpath}")

    # Per-item data-driven check — covers ALL 400 items (1401-1800)
    DEEP_BUNDLE_KEYS = {
        "runtime-entrypoint_proof": "runtime_entrypoint",
        "side-effect_proof": COVERED_BY_MANUAL_CHECK,
        "file-watch_proof": COVERED_BY_MANUAL_CHECK,
        "state-reconstruction_proof": "state_reconstruction",
        "intent-preservation_proof": "intent_preservation",
        "final-gate_proof": "final_gate",
        "legacy-artifact_proof": COVERED_BY_MANUAL_CHECK,
        "report-consumer_proof": COVERED_BY_MANUAL_CHECK,
        "report-producer_proof": COVERED_BY_MANUAL_CHECK,
        "runtime-error_proof": COVERED_BY_MANUAL_CHECK,
        "invalid-proof_proof": COVERED_BY_MANUAL_CHECK,
        "proof_bootstrap_proof": "bootstrap",
        "evidence-liveness_proof": COVERED_BY_MANUAL_CHECK,
        "assumption_register_proof": COVERED_BY_MANUAL_CHECK,
        "claim-downgrade_proof": "claim_downgrade",
        "evidence-strength_proof": "evidence_strength",
        "proof-budget_proof": "proof_budget",
        "red-team_proof": COVERED_BY_MANUAL_CHECK,
        "metamorphic_proof": "metamorphic",
        "equivalence_proof": "equivalence",
        "temporal-consistency_proof": "temporal_consistency",
        "evidence-normalization_proof": "evidence_normalization",
        "schema-roundtrip_proof": "schema_roundtrip",
        "evidence-minimization_proof": "evidence_minimization",
        "recovery-from-validation-failure_proof": "recovery_from_validation_failure",
        "proof-contract_test": "proof_contract_test",
        "static-analysis_proof": "static_analysis",
        "call-graph_proof": "call_graph",
        "data-flow_proof": "data_flow",
        "taint-tracking_proof": "taint_tracking",
        "regex-safety_proof": "regex_safety",
        "pytest-configuration_proof": "pytest_configuration",
        "test-quality_proof": "test_quality",
        "assertion-sensitivity_proof": "assertion_sensitivity",
        "mutation-score_proof": "mutation_score",
        "lineage_proof": "lineage",
        "identity-resolution_proof": "identity_resolution",
        "authorization-boundary_proof": "authorization_boundary",
        "policy-conflict_proof": "policy_conflict",
        "artifact-content_proof": "artifact_content",
        "external-process_proof": "external_process",
    }
    check_all_gap_items(errors, bundle, "Deep", 1401, 1800, DEEP_BUNDLE_KEYS)
    return errors


def main() -> int:
    errs = validate_deep()
    if errs:
        print("VALIDATE DEEP FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-deep: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
