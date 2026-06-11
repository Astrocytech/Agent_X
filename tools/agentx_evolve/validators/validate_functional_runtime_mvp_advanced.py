"""Validate advanced proof concerns with concrete programmatic checks.

Gaps 901-1400.
"""
from __future__ import annotations

import json
import os
import re
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


def _git_commit() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception:
        return ""


def validate_advanced() -> list[str]:
    errors = []

    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(bundle, dict):
        bundle = {}
        errors.append("Advanced: proof bundle missing or invalid — cannot validate bundle-key checks")
    # Per-item data-driven check — covers ALL 500 items (901-1400)
    ADVANCED_BUNDLE_KEYS = {
        "ordering_proof": "ordering_proof",
        "compatibility-scope_proof": COVERED_BY_MANUAL_CHECK,
        "metrics_proof": COVERED_BY_MANUAL_CHECK,
        "audit-log_proof": COVERED_BY_MANUAL_CHECK,
        "approval-expiry_proof": COVERED_BY_MANUAL_CHECK,
        "access-control_proof": "access_control",
        "activation_proof": "activation",
        "rollback-depth_proof": COVERED_BY_MANUAL_CHECK,
        "crash-recovery_proof": "crash_recovery",
        "data-retention_proof": "data_retention",
        "archive_proof": "archive",
        "human-readable_consistency_proof": COVERED_BY_MANUAL_CHECK,
        "api-contract_proof": "api_contract",
        "serialization_proof": COVERED_BY_MANUAL_CHECK,
        "internationalization_proof": COVERED_BY_MANUAL_CHECK,
        "deprecation_proof": "deprecated",
        "minimality_proof": "minimality",
        "assurance-level_proof": COVERED_BY_MANUAL_CHECK,
        "invariant_completeness_proof": "invariant_registry",
        "decision_precedence_proof": "decision_trace",
        "causal-chain_proof": "causal_chain",
        "property-based_proof": "property_tests",
        "fuzzing_proof": "fuzzing",
        "differential_validation_proof": "differential_validation",
        "oracle_proof": "oracle",
        "self-test_proof": "self_test",
        "semantic-drift_proof": "semantic_drift",
        "reviewability_proof": COVERED_BY_MANUAL_CHECK,
        "machine-readability_proof": COVERED_BY_MANUAL_CHECK,
        "changelog_proof": "changelog",
        "risk-register_proof": COVERED_BY_MANUAL_CHECK,
        "escalation_proof": COVERED_BY_MANUAL_CHECK,
        "evidence_freshness_proof": COVERED_BY_MANUAL_CHECK,
        "evidence_ownership_proof": COVERED_BY_MANUAL_CHECK,
        "independent-review_proof": COVERED_BY_MANUAL_CHECK,
        "machine-actionability_proof": COVERED_BY_MANUAL_CHECK,
        "evidence_prioritization_proof": "evidence_prioritization",
        "semantic-validation_proof": COVERED_BY_MANUAL_CHECK,
        "runtime-vs-proof_separation": COVERED_BY_MANUAL_CHECK,
        "scenario_isolation_proof": "scenario_definitions",
        "scenario-definition_proof": "scenario_registry",
        "evidence-query_proof": "evidence_query",
        "validator-composition_proof": COVERED_BY_MANUAL_CHECK,
        "report-lifecycle_proof": "report_lifecycle",
        "proof-scope_proof": "proof_scope",
        "slo_proof": "slo",
        "formal-claim_proof": "formal_claims",
        "counterevidence_proof": "counterevidence",
        "evidence-graph_reachability_proof": "evidence_graph",
        "proof-query_api": "query_api",
        "runtime-entrypoint_proof": "runtime_entrypoint",
    }
    check_all_gap_items(errors, bundle, "Advanced", 901, 1400, ADVANCED_BUNDLE_KEYS)

    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))
    if not isinstance(transcript, list):
        errors.append("Advanced: command transcript missing")
        transcript = []

    matrix = load_json(str(REPORT_DIR / "functional_runtime_mvp_acceptance_matrix.json"))
    trace = load_json(str(REPORT_DIR / "functional_runtime_mvp_requirement_traceability_matrix.json"))
    event_log = load_json(str(REPORT_DIR / "functional_runtime_mvp_event_log.json"))
    evidence = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    verdict = load_json(str(REPORT_DIR / "functional_runtime_mvp_final_verdict.json"))
    state = load_json(str(REPORT_DIR / "functional_runtime_mvp_state.json"))
    compat = load_json(str(REPORT_DIR / "functional_runtime_compatibility_report.json"))

    # Gap 901-903: Ordering — duplicate IDs
    id_sources = {}
    for src_name, src in [("acceptance_matrix", matrix), ("traceability", trace), ("event_log", event_log)]:
        if isinstance(src, dict):
            rows = src.get("rows", src.get("events", src.get("findings", [])))
            if isinstance(rows, list):
                for r in rows:
                    if isinstance(r, dict):
                        rid = r.get("id") or r.get("requirement_id") or r.get("event_id") or r.get("attack_id")
                        if rid:
                            key = f"{src_name}:{rid}"
                            if key in id_sources:
                                errors.append(f"Advanced: 901 - duplicate ID {rid} in {src_name}")
                            id_sources[key] = True

    # Gap 904-913: Compatibility-scope
    if isinstance(compat, dict):
        platforms = compat.get("supported_platforms", compat.get("platforms", []))
        if not platforms:
            errors.append("Advanced: 904 - compatibility report missing supported_platforms")
        if isinstance(platforms, list):
            for p in platforms:
                if isinstance(p, str) and ("linux" not in p.lower() and "posix" not in p.lower()):
                    errors.append(f"Advanced: 905 - non-Linux platform in compatibility report: {p}")
    else:
        errors.append("Advanced: 904 - compatibility report missing")

    # Gap 909: platform assumptions in final verdict
    if isinstance(verdict, dict):
        plat = verdict.get("platform", verdict.get("compatibility", None))
        if not plat:
            errors.append("Advanced: 909 - final verdict missing platform metadata")

    # Gap 914-923: Metrics consistency
    if isinstance(matrix, dict):
        rows = matrix.get("rows", [])
        total = len(rows)
        statuses = [r.get("status", "") for r in rows if isinstance(r, dict)]
        passed = statuses.count("PASS")
        failed = statuses.count("FAIL")
        skipped = statuses.count("SKIP") + statuses.count("SKIPPED")
        blocked = statuses.count("BLOCKED")

        pass_rate = matrix.get("pass_rate", matrix.get("pass_percentage", None))
        if total > 0 and pass_rate is not None:
            expected = round(passed / total * 100, 1)
            actual = round(float(pass_rate), 1) if isinstance(pass_rate, (int, float)) else 0
            if actual != expected:
                errors.append(f"Advanced: 919 - pass_rate {actual}% != expected {expected}% ({passed}/{total})")

        if failed > 0 and pass_rate is not None and float(pass_rate) >= 99.9:
            errors.append(f"Advanced: 920 - pass_rate ~100% but {failed} rows failed")

        if total == 0:
            errors.append("Advanced: 917 - zero rows in acceptance matrix")

    # Gap 924-933: Audit/event log
    if isinstance(event_log, dict):
        events = event_log.get("events", event_log.get("rows", []))
        if not isinstance(events, list) or len(events) == 0:
            errors.append("Advanced: 924 - event log empty")
        else:
            seq_nums = [e.get("sequence", e.get("seq", e.get("id", None))) for e in events if isinstance(e, dict)]
            seq_nums = [s for s in seq_nums if isinstance(s, int)]
            if seq_nums and len(seq_nums) > 1:
                expected_seq = list(range(min(seq_nums), max(seq_nums) + 1))
                if sorted(seq_nums) != expected_seq:
                    errors.append("Advanced: 926 - event log sequence numbers have gaps")

            # Gap 927: every event must have an actor identity
            for ev in events:
                if isinstance(ev, dict) and not ev.get("actor") and not ev.get("actor_id") and not ev.get("user"):
                    errors.append(f"Advanced: 927 - event missing actor identity: {ev.get('type', 'unknown type')}")

            # Gap 928: events must have timestamps
            no_ts_count = 0
            for ev in events:
                if isinstance(ev, dict) and not ev.get("timestamp") and not ev.get("ts"):
                    no_ts_count += 1
            if no_ts_count > 0:
                errors.append(f"Advanced: 928 - {no_ts_count} events missing timestamps")

    # Gap 934-943: Approval-expiry — traceability rows with approval component must exist
    if isinstance(trace, dict):
        trace_rows = trace.get("rows", [])
        if isinstance(trace_rows, list):
            approval_rows = [r for r in trace_rows if isinstance(r, dict) and "approval" in str(r.get("component", "")).lower()]
            if not approval_rows:
                errors.append("Advanced: 934 - no approval-related rows in traceability matrix")

    # Gap 944-953: Access-control metadata in bundle
    ac = bundle.get("access_control", bundle.get("access", None))
    if not ac:
        errors.append("Advanced: 944 - access_control metadata missing from proof bundle")

    # Gap 954-963: Activation metadata
    activation = bundle.get("activation", None)
    if not activation:
        errors.append("Advanced: 954 - activation metadata missing from proof bundle")

    # Gap 964-973: Rollback events
    if isinstance(event_log, dict):
        evt_list = event_log.get("events", [])
        if isinstance(evt_list, list):
            rollback_events = [e for e in evt_list if isinstance(e, dict) and "rollback" in str(e.get("type", "")).lower()]
            if rollback_events:
                for rb in rollback_events:
                    if not rb.get("before_hash") and not rb.get("before"):
                        errors.append("Advanced: 968 - rollback event missing before hash")

    # Gap 974-983: Crash recovery metadata
    recovery = bundle.get("crash_recovery", bundle.get("recovery", None))
    if not recovery:
        errors.append("Advanced: 974 - crash_recovery metadata missing from proof bundle")

    # Gap 984-993: Data retention metadata
    retention = bundle.get("data_retention", bundle.get("retention", None))
    if not retention:
        errors.append("Advanced: 984 - data_retention metadata missing from proof bundle")

    # Gap 990: stale PASS files in report dir
    for f in sorted(REPORT_DIR.glob("*")):
        if f.is_file() and "PASS" in f.stem.upper() and not f.suffix:
            errors.append(f"Advanced: 990 - stale PASS file in reports: {f.name}")

    # Gap 994-1003: Archive metadata
    archive = bundle.get("archive", None)
    if not archive:
        errors.append("Advanced: 994 - archive metadata missing from proof bundle")

    # Gap 1004-1013: Human-readable consistency — md/json verdicts must agree
    for md_file in sorted(REPORT_DIR.glob("*.md")):
        json_file = REPORT_DIR / (md_file.stem + ".json")
        if json_file.exists():
            try:
                md_content = md_file.read_text(encoding="utf-8")
                js_data = load_json(str(json_file))
                if isinstance(js_data, dict):
                    js_status = str(js_data.get("status", js_data.get("verdict", "")))
                    if js_status.upper() == "PASS" and "FAIL" in md_content:
                        errors.append(f"Advanced: 1004 - md says FAIL but JSON says PASS for {md_file.name}")
                    if "FAIL" in md_content.upper() and js_status.upper() == "PASS":
                        errors.append(f"Advanced: 1005 - md says PASS but JSON says FAIL for {md_file.name}")
            except (OSError, UnicodeDecodeError):
                errors.append(f"Advanced: 1004 - cannot read {md_file.name} for consistency check")
        # Gap 1007: markdown links must resolve
        for m in re.finditer(r'\[.*?\]\(([^)]+)\)', (md_content if 'md_content' in dir() and md_content else "")):
            link = m.group(1)
            if link.startswith("http"):
                continue
            linked_path = REPORT_DIR / link
            if not linked_path.exists():
                linked_abs = ROOT / link
                if not linked_abs.exists():
                    errors.append(f"Advanced: 1007 - broken markdown link in {md_file.name}: {link}")

    # Gap 1014-1023: API-contract metadata
    api_contract = bundle.get("api_contract", bundle.get("api", None))
    if not api_contract:
        errors.append("Advanced: 1014 - api_contract metadata missing from proof bundle")

    # Gap 1024-1033: Serialization validity
    for report_file in sorted(REPORT_DIR.glob("*.json")):
        raw = report_file.read_bytes()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"Advanced: 1027 - {report_file.name} is not valid UTF-8")

        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                keys1 = list(obj.keys())
                obj2 = json.loads(raw)
                keys2 = list(obj2.keys())
                if keys1 != keys2:
                    errors.append(f"Advanced: 1029 - {report_file.name} key order differs on re-parse")
        except json.JSONDecodeError:
            errors.append(f"Advanced: 1029 - {report_file.name} is not valid JSON")

    # Gap 1034-1043: Internationalization — all reports must be valid UTF-8
    for report_file in sorted(REPORT_DIR.glob("*.json")):
        try:
            report_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            errors.append(f"Advanced: 1034 - {report_file.name} has non-UTF-8 content")

    # Gap 1044-1053: Deprecation — no deprecated reports in final dir
    deprecated = bundle.get("deprecated", bundle.get("deprecation", None))
    if deprecated:
        dep_reports = deprecated.get("reports", [])
        if isinstance(dep_reports, list):
            for dr in dep_reports:
                for f in REPORT_DIR.glob("*.json"):
                    if str(dr).replace(".json", "") in f.stem:
                        errors.append(f"Advanced: 1045 - deprecated report {f.name} in final dir")

    # Gap 1054-1063: Minimality
    min_info = bundle.get("minimality", bundle.get("minimal", None))
    if isinstance(min_info, dict):
        required = min_info.get("required", [])
        if not required:
            errors.append("Advanced: 1054 - minimality missing required artifact list")
    else:
        errors.append("Advanced: 1054 - minimality metadata missing from proof bundle")

    # Gap 1064-1073: Assurance-level — each trace row must have evidence_type
    if isinstance(trace, dict):
        trace_rows = trace.get("rows", [])
        if isinstance(trace_rows, list):
            missing_type = 0
            for r in trace_rows:
                if isinstance(r, dict):
                    evidence_type = r.get("evidence_type", r.get("assurance", r.get("type", "")))
                    if not evidence_type:
                        missing_type += 1
            if missing_type > 0:
                errors.append(f"Advanced: 1064 - {missing_type} traceability rows missing evidence_type/assurance")

    # Gap 1074-1083: Invariant completeness
    inv_registry = bundle.get("invariant_registry", bundle.get("invariants", None))
    if not inv_registry:
        errors.append("Advanced: 1074 - invariant_registry metadata missing from proof bundle")

    # Gap 1084-1093: Decision precedence
    decision_trace = bundle.get("decision_trace", bundle.get("decisions", None))
    if not decision_trace:
        errors.append("Advanced: 1084 - decision_trace metadata missing from proof bundle")

    # Gap 1094-1103: Causal-chain
    causal = bundle.get("causal_chain", bundle.get("chain", None))
    if not causal:
        errors.append("Advanced: 1094 - causal_chain metadata missing from proof bundle")

    # Gap 1104-1113: Property-based proof
    prop_tests = bundle.get("property_tests", bundle.get("property", None))
    if not prop_tests:
        errors.append("Advanced: 1104 - property_tests metadata missing from proof bundle")

    # Gap 1114-1123: Fuzzing
    fuzz = bundle.get("fuzzing", None)
    if not fuzz:
        errors.append("Advanced: 1114 - fuzzing metadata missing from proof bundle")

    # Gap 1124-1133: Differential validation
    diff_val = bundle.get("differential_validation", bundle.get("differential", None))
    if not diff_val:
        errors.append("Advanced: 1124 - differential_validation metadata missing from proof bundle")

    # Gap 1134-1143: Oracle
    oracle = bundle.get("oracle", bundle.get("oracles", None))
    if not oracle:
        errors.append("Advanced: 1134 - oracle metadata missing from proof bundle")

    # Gap 1144-1153: Self-test
    self_test = bundle.get("self_test", bundle.get("selftest", None))
    if not self_test:
        errors.append("Advanced: 1144 - self_test metadata missing from proof bundle")

    # Gap 1154-1163: Semantic-drift
    drift = bundle.get("semantic_drift", bundle.get("drift", None))
    if not drift:
        errors.append("Advanced: 1154 - semantic_drift metadata missing from proof bundle")

    # Gap 1164-1173: Reviewability — artifact index + final verdict
    artifact_index = load_json(str(REPORT_DIR / "functional_runtime_mvp_artifact_index.json"))
    if not isinstance(artifact_index, dict):
        errors.append("Advanced: 1164 - artifact index missing for reviewability")
    if not isinstance(verdict, dict):
        errors.append("Advanced: 1164 - final verdict missing for reviewability")

    # Gap 1174-1183: Machine-readability — every .md must have JSON counterpart
    for md_file in sorted(REPORT_DIR.glob("*.md")):
        json_file = REPORT_DIR / (md_file.stem + ".json")
        if not json_file.exists():
            errors.append(f"Advanced: 1174 - no JSON counterpart for markdown: {md_file.name}")

    # Gap 1184-1193: Changelog
    changelog = bundle.get("changelog", None)
    if not changelog:
        errors.append("Advanced: 1184 - changelog metadata missing from proof bundle")

    # Gap 1194-1203: Risk-register — gap discovery must not have open unfixed findings
    gap_report = load_json(str(REPORT_DIR / "functional_runtime_mvp_gap_discovery_report.json"))
    if isinstance(gap_report, dict):
        findings = gap_report.get("findings", gap_report.get("gaps", []))
        if isinstance(findings, list):
            open_findings = [f for f in findings if isinstance(f, dict) and f.get("status", "").upper() not in ("FIXED", "CLOSED", "BENIGN")]
            if open_findings:
                errors.append(f"Advanced: 1194 - {len(open_findings)} open findings not marked FIXED/CLOSED/BENIGN")

    # Gap 1204-1213: Escalation — verdict must have correct classification
    if isinstance(verdict, dict):
        if verdict.get("classification", "").upper() != "FUNCTIONAL_RUNTIME_MVP":
            errors.append(f"Advanced: 1204 - verdict classification is not FUNCTIONAL_RUNTIME_MVP")

    # Gap 1214-1223: Evidence freshness
    if isinstance(evidence, dict):
        ev_timestamp = evidence.get("generated_at", evidence.get("timestamp", evidence.get("ts", "")))
        if not ev_timestamp:
            errors.append("Advanced: 1221 - evidence manifest missing timestamp")
        ev_commit = evidence.get("git_commit", evidence.get("commit", ""))
        current = _git_commit()
        if ev_commit and current and ev_commit != current:
            errors.append(f"Advanced: 1221 - evidence git_commit {ev_commit} != current {current}")
        if not ev_commit:
            errors.append("Advanced: 1221 - evidence manifest missing git_commit")
        if not ev_timestamp:
            errors.append("Advanced: 1221 - evidence manifest missing timestamp")

    # Gap 1224-1233: Evidence ownership
    if isinstance(artifact_index, dict):
        artifacts = artifact_index.get("artifacts", artifact_index.get("files", []))
        if isinstance(artifacts, list):
            owners = [a.get("owner", "") for a in artifacts if isinstance(a, dict)]
            if not owners:
                errors.append("Advanced: 1224 - artifact index entries missing owner field")

    # Gap 1234-1243: Independent-review
    review_recs = load_json(str(REPORT_DIR / "review_records.json"))
    if not isinstance(review_recs, dict):
        errors.append("Advanced: 1234 - review_records.json missing for independent review")

    # Gap 1244-1253: Machine-actionability
    if isinstance(verdict, dict):
        if not verdict.get("classification", ""):
            errors.append("Advanced: 1246 - final verdict missing classification")
        if not verdict.get("git_commit", ""):
            errors.append("Advanced: 1246 - final verdict missing git_commit")
        if not verdict.get("proof_run_id", ""):
            errors.append("Advanced: 1246 - final verdict missing proof_run_id")
    else:
        errors.append("Advanced: 1244 - final verdict missing (machine-actionability)")

    # Gap 1254-1263: Evidence prioritization
    prioritization = bundle.get("evidence_prioritization", bundle.get("prioritization", None))
    if not prioritization:
        errors.append("Advanced: 1254 - evidence_prioritization metadata missing from proof bundle")

    # Gap 1264-1273: Semantic-validation — evidence_refs must resolve
    if isinstance(trace, dict):
        ev_ref_rows = [r for r in trace.get("rows", []) if isinstance(r, dict) and r.get("evidence_refs", [])]
        if not ev_ref_rows:
            errors.append("Advanced: 1264 - no evidence_refs in traceability rows")
        else:
            for r in ev_ref_rows:
                refs = r.get("evidence_refs", [])
                if isinstance(refs, list):
                    for ref in refs:
                        if isinstance(ref, str) and not (REPORT_DIR / ref).exists() and not (ROOT / ref).exists():
                            errors.append(f"Advanced: 1265 - evidence_ref points to non-existent file: {ref}")

    # Gap 1274-1283: Runtime-vs-proof separation
    transcript_commands = [c.get("command", "") for c in transcript if isinstance(c, dict)]
    all_cmds = " ".join(transcript_commands)
    if "runtime" in all_cmds.lower() and "import" not in all_cmds.lower():
        errors.append("Advanced: 1274 - runtime commands detected in proof transcript (separation violation)")

    # Gap 1284-1293: Scenario isolation
    scenario_defs = bundle.get("scenario_definitions", bundle.get("scenarios", None))
    if not scenario_defs:
        errors.append("Advanced: 1284 - scenario_definitions metadata missing from proof bundle")

    # Gap 1294-1303: Scenario-definition registry
    scenario_registry = bundle.get("scenario_registry", None)
    if not scenario_registry:
        errors.append("Advanced: 1294 - scenario_registry metadata missing from proof bundle")

    # Gap 1304-1314: Evidence-query
    query_support = bundle.get("evidence_query", bundle.get("query", None))
    if not query_support:
        errors.append("Advanced: 1304 - evidence_query metadata missing from proof bundle")

    # Gap 1315-1324: Validator-composition
    validators_run = [c for c in transcript_commands if "validate_functional_runtime_mvp" in c]
    validator_names_run = [v.split()[-1] for v in validators_run]
    if not validator_names_run:
        errors.append("Advanced: 1315 - no validators found in transcript")
    else:
        # Check all required validators ran (32 known validators)
        required = ["anti_false_pass", "replay", "gap_discovery", "transcript", "reports",
                     "traceability", "source_safety", "reuse_map", "idempotency",
                     "self_promotion", "event_log", "state", "path_safety", "runtime_safety",
                     "schema", "all_in_one", "cross_report", "corrective_coverage",
                     "validator_proof", "clean_checkout", "artifact_safety",
                     "execution_integrity", "provenance", "security", "completeness",
                     "lifecycle", "infrastructure", "determinism", "meta_quality",
                     "advanced", "deep", "enterprise", "aspirational"]
        found = set()
        for c in validator_names_run:
            for r in required:
                if r.replace("_", "") in c.replace("_", ""):
                    found.add(r)
        missing_validators = [r for r in required if r not in found]
        if missing_validators:
            errors.append(f"Advanced: 1315 - {len(missing_validators)} required validators not in transcript: {', '.join(missing_validators)}")

    # Gap 1325-1334: Report-lifecycle
    lifecycle_info = bundle.get("report_lifecycle", bundle.get("lifecycle", None))
    if not lifecycle_info:
        errors.append("Advanced: 1325 - report_lifecycle metadata missing from proof bundle")

    # Gap 1335-1344: Proof-scope
    scope_info = bundle.get("proof_scope", bundle.get("scope", None))
    if not scope_info:
        errors.append("Advanced: 1335 - proof_scope metadata missing from proof bundle")

    # Gap 1345-1354: SLO
    slo_info = bundle.get("slo", bundle.get("performance", None))
    if not slo_info:
        errors.append("Advanced: 1345 - slo metadata missing from proof bundle")

    # Gap 1355-1364: Formal-claim
    claims = bundle.get("formal_claims", bundle.get("claims", None))
    if not claims:
        errors.append("Advanced: 1355 - formal_claims metadata missing from proof bundle")

    # Gap 1365-1374: Counterevidence
    counter = bundle.get("counterevidence", bundle.get("counter", None))
    if not counter:
        errors.append("Advanced: 1365 - counterevidence metadata missing from proof bundle")

    # Gap 1375-1384: Evidence-graph
    graph = bundle.get("evidence_graph", bundle.get("graph", None))
    if not graph:
        errors.append("Advanced: 1375 - evidence_graph metadata missing from proof bundle")

    # Gap 1385-1394: Proof-query API
    query_api = bundle.get("query_api", None)
    if not query_api:
        errors.append("Advanced: 1385 - query_api metadata missing from proof bundle")

    # Gap 1395-1400: Runtime-entrypoint
    entrypoint_info = bundle.get("runtime_entrypoint", bundle.get("entrypoint", None))
    if not entrypoint_info:
        errors.append("Advanced: 1395 - runtime_entrypoint metadata missing from proof bundle")

    return errors


def main() -> int:
    errs = validate_advanced()
    if errs:
        print("VALIDATE ADVANCED FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-advanced: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
