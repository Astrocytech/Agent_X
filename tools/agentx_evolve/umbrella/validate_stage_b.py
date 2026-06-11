#!/usr/bin/env python3
import json, os, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = REPO_ROOT / "reports" / "umbrella_agent"

REQUIRED_REPORTS = [
    "stage_b_patch_provenance.json",
    "umbrella_persistence_classification_report.json",
    "replayability_report.json",
    "umbrella_contract_closure.json",
    "umbrella_rule_test_results.json",
    "umbrella_fixture_field_closure.json",
]


def _current_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT)).decode().strip()


def validate() -> None:
    errors: list[str] = []
    commit = _current_commit()

    for name in REQUIRED_REPORTS:
        path = REPORT_DIR / name
        if not path.is_file():
            errors.append(f"MISSING: reports/umbrella_agent/{name}")
            continue
        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError) as e:
            errors.append(f"INVALID JSON: reports/umbrella_agent/{name} — {e}")
            continue
        if not isinstance(data, dict):
            errors.append(f"NOT A DICT: reports/umbrella_agent/{name}")
            continue
        if data.get("status") not in ("PASS", "REGENERATED", "PATCHED"):
            errors.append(f"UNEXPECTED status '{data.get('status')}' in {name}")

        if data.get("commit") and data["commit"] != commit:
            errors.append(f"{name}: commit {data['commit']} != HEAD {commit}")

    # Deep validation of individual reports
    prov_path = REPORT_DIR / "stage_b_patch_provenance.json"
    if prov_path.is_file():
        try:
            with open(prov_path) as f:
                prov = json.load(f)
            canary = prov.get("canary_tests", [])
            if not canary:
                errors.append("stage_b_patch_provenance: no canary test results")
            for c in canary:
                if not c.get("passed", False) and "error" not in c:
                    errors.append(f"stage_b_patch_provenance: canary test failed: {c.get('test')}")
            generation = prov.get("generation", {})
            gen_passed = generation.get("pytest_passed", False)
            if not gen_passed:
                errors.append(f"stage_b_patch_provenance: generation pytest failed: {generation.get('pytest_summary')}")
        except (json.JSONDecodeError, ValueError):
            errors.append("stage_b_patch_provenance: unreadable")

    replay_path = REPORT_DIR / "replayability_report.json"
    if replay_path.is_file():
        try:
            with open(replay_path) as f:
                replay = json.load(f)
            replay_result = replay.get("replay_result", {})
            if not replay_result.get("replayable", False):
                errors.append(f"replayability_report: replay not replayable: {replay_result.get('exit_code')}")
        except (json.JSONDecodeError, ValueError):
            errors.append("replayability_report: unreadable")

    rules_path = REPORT_DIR / "umbrella_rule_test_results.json"
    if rules_path.is_file():
        try:
            with open(rules_path) as f:
                rules_data = json.load(f)
            verification = rules_data.get("verification", {})
            if verification.get("mode") != "real_generation":
                errors.append(f"umbrella_rule_test_results: verification mode is not real_generation")
            if not rules_data.get("status") == "PASS":
                errors.append(f"umbrella_rule_test_results: status is not PASS")
        except (json.JSONDecodeError, ValueError):
            errors.append("umbrella_rule_test_results: unreadable")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    print(f"PASS: Stage B reports validated ({len(REQUIRED_REPORTS)} reports, commit={commit[:12]})")


if __name__ == "__main__":
    validate()
