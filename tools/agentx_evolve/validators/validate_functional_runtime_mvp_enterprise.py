"""Validate enterprise-grade proof concerns: pytest-config, test-quality,
assertion-sensitivity, mutation-score, lineage, identity, authorization,
policy-conflict, artifact-content, external-process, cache-key, parallel-replay,
supply-chain, SBOM, license, static-type, lint, complexity, config-freeze,
clock, fingerprint, noninteractivity, exit-status, stdout, golden-run, locality,
upgradability, completeness-bound, git-object, layout, registries, proof-contract,
gate-input/output, detached-verifier, hash-algorithm, directory-hash,
requirement-to-code/test/validator, DAG, fixed-point, TCB, attestation,
provenance, hooks, generated-code, fixtures, baseline, regression.

Gaps 1801-2200.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from agentx_evolve.validators.common import check_all_gap_items, parse_report_dir

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


def validate_enterprise() -> list[str]:
    errors = []

    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(bundle, dict):
        bundle = {}

    v_dir = ROOT / "tools" / "agentx_evolve" / "validators"
    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))
    if not isinstance(transcript, list):
        transcript = []

    # Gap 1805-1814: Cache-key
    cache_info = bundle.get("cache_key", bundle.get("cache", None))
    if not cache_info:
        errors.append("Enterprise: 1805 - cache_key metadata missing from proof bundle")

    # Gap 1815-1824: Parallel-replay
    parallel_info = bundle.get("parallel_replay", None)
    if not parallel_info:
        errors.append("Enterprise: 1815 - parallel_replay metadata missing from proof bundle")

    # Gap 1825-1834: Supply-chain
    supply = bundle.get("supply_chain", None)
    if not supply:
        errors.append("Enterprise: 1825 - supply_chain metadata missing from proof bundle")

    # Gap 1835-1844: SBOM
    sbom = bundle.get("sbom", None)
    if not sbom:
        errors.append("Enterprise: 1835 - sbom metadata missing from proof bundle")

    # Gap 1845-1854: License
    license_info = bundle.get("license", None)
    if not license_info:
        errors.append("Enterprise: 1845 - license metadata missing from proof bundle")
    license_files = list(ROOT.glob("LICENSE*")) + list(ROOT.glob("LICENCE*"))
    if not license_files:
        errors.append("Enterprise: 1845 - no LICENSE file found in repository root")

    # Gap 1855-1864: Static-type
    static_type = bundle.get("static_type", None)
    if not static_type:
        errors.append("Enterprise: 1855 - static_type metadata missing from proof bundle")
    if v_dir.exists():
        typed_files = 0
        for vf in sorted(v_dir.glob("validate_*.py")):
            try:
                txt = vf.read_text(encoding="utf-8")
                if "-> " in txt or ": " in txt and "int" in txt:
                    typed_files += 1
            except (OSError, UnicodeDecodeError):
                pass
        if typed_files == 0:
            errors.append("Enterprise: 1855 - no validators use type hints")

    # Gap 1865-1874: Lint
    lint_info = bundle.get("lint", None)
    if not lint_info:
        errors.append("Enterprise: 1865 - lint metadata missing from proof bundle")

    # Gap 1875-1884: Complexity
    complexity = bundle.get("complexity", None)
    if not complexity:
        errors.append("Enterprise: 1875 - complexity metadata missing from proof bundle")
    if v_dir.exists():
        large_files = []
        for vf in sorted(v_dir.glob("validate_*.py")):
            if vf.stat().st_size > 20000:
                large_files.append(vf.name)
        if large_files:
            errors.append(f"Enterprise: 1875 - overly complex validators (>20KB): {', '.join(large_files)}")

    # Gap 1885-1894: Config-freeze
    config_freeze = bundle.get("config_freeze", None)
    if not config_freeze:
        errors.append("Enterprise: 1885 - config_freeze metadata missing from proof bundle")
    pyproject_path = ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        errors.append("Enterprise: 1885 - pyproject.toml missing for config freeze reference")

    # Gap 1895-1904: Clock-integrity
    clock = bundle.get("clock_integrity", None)
    if not clock:
        errors.append("Enterprise: 1895 - clock_integrity metadata missing from proof bundle")
    if isinstance(transcript, list) and len(transcript) > 1:
        for i, cmd in enumerate(transcript[1:], 1):
            if isinstance(cmd, dict):
                ts = cmd.get("timestamp", cmd.get("ts", cmd.get("time", "")))
                prev_ts = transcript[i-1].get("timestamp", transcript[i-1].get("ts", transcript[i-1].get("time", "")))
                if ts and prev_ts and isinstance(ts, str) and isinstance(prev_ts, str) and ts < prev_ts:
                    errors.append(f"Enterprise: 1895 - non-monotonic clock at transcript entry {i}")
                    break

    # Gap 1905-1914: Host-fingerprint
    host = bundle.get("host_fingerprint", None)
    if not host:
        errors.append("Enterprise: 1905 - host_fingerprint metadata missing from proof bundle")
    hostname = os.uname().nodename if hasattr(os, 'uname') else None
    if hostname:
        bundle_host = bundle.get("hostname", bundle.get("host", ""))
        if bundle_host and bundle_host != hostname:
            errors.append(f"Enterprise: 1905 - bundle host ({bundle_host}) != actual hostname ({hostname})")

    # Gap 1915-1924: Noninteractivity
    noninteractive = bundle.get("noninteractivity", None)
    if not noninteractive:
        errors.append("Enterprise: 1915 - noninteractivity metadata missing from proof bundle")

    # Gap 1925-1934: Exit-status-taxonomy
    if isinstance(transcript, list):
        exit_codes = {}
        for cmd in transcript:
            if isinstance(cmd, dict):
                ec = cmd.get("exit_code", None)
                if ec is None:
                    errors.append("Enterprise: 1925 - command missing exit_code in transcript: " + str(cmd.get("command", ""))[:60])
                    break
                exit_codes[ec] = exit_codes.get(ec, 0) + 1

    # Gap 1935-1944: Stdout-schema
    stdout_info = bundle.get("stdout_schema", None)
    if not stdout_info:
        errors.append("Enterprise: 1935 - stdout_schema metadata missing from proof bundle")

    # Gap 1945-1954: Golden-run
    golden = bundle.get("golden_run", bundle.get("golden", None))
    if not golden:
        errors.append("Enterprise: 1945 - golden_run metadata missing from proof bundle")

    # Gap 1955-1964: Proof-locality
    locality = bundle.get("proof_locality", bundle.get("locality", None))
    if not locality:
        errors.append("Enterprise: 1955 - proof_locality metadata missing from proof bundle")

    # Gap 1965-1974: Upgradability
    upgradability = bundle.get("upgradability", None)
    if not upgradability:
        errors.append("Enterprise: 1965 - upgradability metadata missing from proof bundle")

    # Gap 1975-1984: Completeness-bound
    completeness = bundle.get("completeness_bound", None)
    if not completeness:
        errors.append("Enterprise: 1975 - completeness_bound metadata missing from proof bundle")

    # Gap 1985-1994: Git-object
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10)
        commit = r.stdout.strip()
        if commit:
            tree_r = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True, text=True, timeout=10)
            tree_hash = tree_r.stdout.strip()
            if isinstance(bundle, dict):
                bundle_tree = bundle.get("tree_hash", bundle.get("git_tree", ""))
                if bundle_tree and tree_hash and bundle_tree != tree_hash:
                    errors.append(f"Enterprise: 1985 - bundle tree hash ({bundle_tree}) != actual ({tree_hash})")
    except Exception as exc:
        errors.append(f"Enterprise: 1985 - git object check failed: {exc}")

    # Gap 1995-2004: Repository-layout
    paths_to_check = [
        ROOT / "tools" / "agentx_evolve" / "validators",
        ROOT / "tools" / "agentx_evolve" / "acceptance",
        ROOT / ".agentx-init" / "reports",
    ]
    for p in paths_to_check:
        if not p.exists():
            errors.append(f"Enterprise: 1995 - required directory missing: {p.relative_to(ROOT)}")

    # Gap 2005-2014: Validator-registry
    validators_dir = ROOT / "tools" / "agentx_evolve" / "validators"
    if validators_dir.exists():
        validator_files = sorted(validators_dir.glob("validate_*.py"))
        if not validator_files:
            errors.append("Enterprise: 2005 - no validator files found for registry")
        else:
            bundle_validators = bundle.get("validators", bundle.get("validator_registry", []))
            if bundle_validators:
                bundle_names = set(bundle_validators) if isinstance(bundle_validators, list) else set()
                fs_names = {v.stem.replace("validate_functional_runtime_mvp_", "") for v in validator_files}
                for bv in bundle_names:
                    if bv not in fs_names and bv.replace("_", "") not in {x.replace("_", "") for x in fs_names}:
                        errors.append(f"Enterprise: 2005 - validator in bundle registry not in filesystem: {bv}")
    else:
        errors.append("Enterprise: 2005 - validators directory missing for registry")

    # Gap 2015-2024: Scenario-registry
    scenario_registry = bundle.get("scenario_registry", None)
    if not scenario_registry:
        errors.append("Enterprise: 2015 - scenario_registry metadata missing from proof bundle")

    # Gap 2025-2034: Test-registry
    test_registry = bundle.get("test_registry", None)
    if not test_registry:
        errors.append("Enterprise: 2025 - test_registry metadata missing from proof bundle")

    # Gap 2035-2044: Schema-registry
    schema_registry = bundle.get("schema_registry", None)
    if not schema_registry:
        errors.append("Enterprise: 2035 - schema_registry metadata missing from proof bundle")

    # Gap 2045-2054: Proof-contract registry
    contract = bundle.get("proof_contract", bundle.get("contract", None))
    if not contract:
        errors.append("Enterprise: 2045 - proof_contract metadata missing from proof bundle")

    # Gap 2055-2064: Gate-input
    gate_input = bundle.get("gate_input", None)
    if not gate_input:
        errors.append("Enterprise: 2055 - gate_input metadata missing from proof bundle")

    # Gap 2065-2074: Gate-output
    verdict = load_json(str(REPORT_DIR / "functional_runtime_mvp_final_verdict.json"))
    if isinstance(verdict, dict):
        output_fields = list(verdict.keys())
        required = ["classification", "git_commit", "proof_run_id"]
        for rf in required:
            if rf not in output_fields:
                errors.append(f"Enterprise: 2065 - final verdict missing required gate output field: {rf}")
    else:
        errors.append("Enterprise: 2065 - final verdict missing for gate output check")

    # Gap 2075-2084: Detached-verifier contract
    detached = bundle.get("detached_verifier", None)
    if not detached:
        errors.append("Enterprise: 2075 - detached_verifier metadata missing from proof bundle")

    # Gap 2085-2094: Evidence-hash algorithm
    if isinstance(bundle, dict):
        report_hashes = bundle.get("report_hashes", {})
        for rpath, h in report_hashes.items():
            if isinstance(h, str) and len(h) != 64:
                errors.append(f"Enterprise: 2085 - non-SHA256 hash length in bundle for {rpath}: {len(h)}")
        if not report_hashes:
            errors.append("Enterprise: 2085 - no report_hashes in proof bundle")

    # Gap 2095-2104: Directory-hash
    dir_hash = bundle.get("directory_hash", None)
    if not dir_hash:
        errors.append("Enterprise: 2095 - directory_hash metadata missing from proof bundle")
    if REPORT_DIR.exists():
        all_report_files = sorted(REPORT_DIR.rglob("*"))
        if not all_report_files:
            errors.append("Enterprise: 2095 - no files in report directory for directory hash")

    # Gap 2105-2114: Requirement-to-code
    trace = load_json(str(REPORT_DIR / "functional_runtime_mvp_requirement_traceability_matrix.json"))
    if isinstance(trace, dict):
        trace_rows = trace.get("rows", [])
        if isinstance(trace_rows, list):
            code_refs = sum(1 for r in trace_rows if isinstance(r, dict) and r.get("code_ref", r.get("source_ref", "")))
            if code_refs == 0:
                errors.append("Enterprise: 2105 - no requirements mapped to source code (code_ref)")

    # Gap 2115-2124: Requirement-to-test
    if isinstance(trace, dict):
        rows = trace.get("rows", [])
        test_refs = sum(1 for r in rows if isinstance(r, dict) and "test" in str(r.get("evidence_refs", "")).lower())
        if test_refs == 0:
            errors.append("Enterprise: 2115 - no requirements mapped to tests")

    # Gap 2125-2134: Requirement-to-validator
    if isinstance(trace, dict):
        rows = trace.get("rows", [])
        val_refs = sum(1 for r in rows if isinstance(r, dict) and "validate" in str(r.get("evidence_refs", "")).lower())
        if val_refs == 0:
            errors.append("Enterprise: 2125 - no requirements mapped to validators")

    # Gap 2135-2144: Report-generation DAG
    dag = bundle.get("report_generation_dag", bundle.get("dag", None))
    if not dag:
        errors.append("Enterprise: 2135 - report_generation_dag metadata missing from proof bundle")

    # Gap 2145-2154: Fixed-point
    fixed_point = bundle.get("fixed_point", None)
    if not fixed_point:
        errors.append("Enterprise: 2145 - fixed_point metadata missing from proof bundle")

    # Gap 2155-2164: Trusted-computing-base
    tcb = bundle.get("trusted_computing_base", bundle.get("tcb", None))
    if not tcb:
        errors.append("Enterprise: 2155 - trusted_computing_base metadata missing from proof bundle")

    # Gap 2165-2174: Attestation
    attestation = bundle.get("attestation", None)
    if not attestation:
        errors.append("Enterprise: 2165 - attestation metadata missing from proof bundle")

    # Gap 2175-2184: Provenance-attestation
    provenance = bundle.get("provenance_attestation", bundle.get("provenance", None))
    if not provenance:
        errors.append("Enterprise: 2175 - provenance_attestation metadata missing from proof bundle")

    # Gap 2185-2194: Build-hook
    hooks_dir = ROOT / ".git" / "hooks"
    if hooks_dir.exists():
        hook_files = [f for f in hooks_dir.iterdir() if f.is_file() and not f.name.endswith(".sample")]
        if hook_files:
            for hf in hook_files:
                if hf.stat().st_size > 0:
                    pass
                else:
                    errors.append(f"Enterprise: 2185 - git hook {hf.name} is empty (0 bytes)")
        else:
            errors.append("Enterprise: 2185 - no active git hooks in .git/hooks")
    else:
        errors.append("Enterprise: 2185 - .git/hooks directory not found")

    # Gap 2195-2204: Generated-code
    generated = bundle.get("generated_code", None)
    if not generated:
        errors.append("Enterprise: 2195 - generated_code metadata missing from proof bundle")

    # Gap 2205-2214: Fixture-integrity
    fixture = bundle.get("fixture_integrity", None)
    if not fixture:
        errors.append("Enterprise: 2205 - fixture_integrity metadata missing from proof bundle")

    # Gap 2215-2224: Baseline
    baseline = bundle.get("baseline", None)
    if not baseline:
        errors.append("Enterprise: 2215 - baseline metadata missing from proof bundle")
    source_before = load_json(str(REPORT_DIR / "functional_runtime_mvp_source_hash_manifest_before.json"))
    if not isinstance(source_before, dict):
        errors.append("Enterprise: 2215 - source hash manifest before missing for baseline")

    # Gap 2225-2234: Regression-matrix
    regression = bundle.get("regression_matrix", None)
    if not regression:
        errors.append("Enterprise: 2225 - regression_matrix metadata missing from proof bundle")

    # Per-item data-driven check — covers ALL 400 items (1801-2200)
    ENTERPRISE_BUNDLE_KEYS = {
        "external-process_proof": "external_process",
        "cache-key_proof": "cache_key",
        "parallel-replay_proof": "parallel_replay",
        "supply-chain_proof": "supply_chain",
        "sbom_proof": "sbom",
        "license_proof": "license",
        "static-type_proof": "static_type",
        "lint_proof": "lint",
        "complexity_proof": "complexity",
        "config-freeze_proof": "config_freeze",
        "clock-integrity_proof": "clock_integrity",
        "host-fingerprint_proof": "host_fingerprint",
        "noninteractivity_proof": "noninteractivity",
        "exit-status_taxonomy_proof": "exit_status_taxonomy",
        "stdout-schema_proof": "stdout_schema",
        "golden-run_proof": "golden_run",
        "proof-locality_proof": "proof_locality",
        "upgradability_proof": "upgradability",
        "completeness-bound_proof": "completeness_bound",
        "git-object_proof": "git_object",
        "repository-layout_proof": "repository_layout",
        "validator-registry_proof": "validator_registry",
        "scenario-registry_proof": "scenario_registry",
        "test-registry_proof": "test_registry",
        "schema-registry_proof": "schema_registry",
        "proof-contract_registry": "proof_contract",
        "gate-input_proof": "gate_input",
        "gate-output_proof": "gate_output",
        "detached-verifier_contract": "detached_verifier",
        "evidence-hash_algorithm_proof": "evidence_hash_algorithm",
        "directory-hash_proof": "directory_hash",
        "requirement-to-code_proof": "requirement_to_code",
        "requirement-to-test_proof": "requirement_to_test",
        "requirement-to-validator_proof": "requirement_to_validator",
        "report-generation_dag_proof": "report_generation_dag",
        "fixed-point_proof": "fixed_point",
        "trusted-computing-base_proof": "trusted_computing_base",
        "attestation_proof": "attestation",
        "provenance-attestation_proof": "provenance_attestation",
        "build-hook_proof": "build_hook",
        "generated-code_proof": "generated_code",
    }
    check_all_gap_items(errors, bundle, "Enterprise", 1801, 2200, ENTERPRISE_BUNDLE_KEYS)
    return errors


def main() -> int:
    errs = validate_enterprise()
    if errs:
        print("VALIDATE ENTERPRISE FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-enterprise: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
