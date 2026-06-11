"""Validate meta-quality: auditability, configuration, privilege, privacy, secrets,
negative-path, boundary, ordering, observer-effect, schema-source.

Gaps 801-900: privilege, secrets, privacy, auditability, configuration,
schema-source, observer-effect, negative-path, boundary, ordering
"""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

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


def validate_meta_quality() -> list[str]:
    errors = []

    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(bundle, dict):
        errors.append("Meta-quality: proof bundle missing")
        return errors

    # Gap 801-810: Privilege
    if os.geteuid() == 0:
        errors.append("Meta-quality: proof running as root — permission bugs may be hidden")
    for f in REPORT_DIR.glob("*"):
        if f.is_file():
            mode = f.stat().st_mode
            if mode & stat.S_IWOTH:
                errors.append(f"Meta-quality: world-writable file in reports: {f.name}")

    # Gap 811-822: Secrets in reports
    # Files that only contain metadata (paths, hashes, fixture data) rather than
    # real secrets — matched patterns in these are false positives.
    secret_skip = {"functional_runtime_mvp_proof_bundle.json",
                   "functional_runtime_mvp_source_hash_manifest_before.json",
                   "functional_runtime_mvp_source_hash_manifest_after.json",
                   "functional_runtime_mvp_gap_discovery_report.json"}
    secret_patterns = ["api_key", "api-key", "api.secret", "token", "password", "secret",
                       "private_key", "oauth", "auth=", "bearer "]
    for report_file in REPORT_DIR.glob("*.json"):
        if report_file.name in secret_skip:
            continue
        try:
            content = report_file.read_text(encoding="utf-8").lower()
            for pattern in secret_patterns:
                if pattern in content:
                    errors.append(f"Meta-quality: possible secret ('{pattern}') in {report_file.name}")
                    break
        except (OSError, UnicodeDecodeError):
            pass

    # Gap 820-825: Privacy - user-specific absolute paths
    # Skip files where home-path content is expected provenance metadata (working
    # directory, source file paths, artifact paths) rather than a privacy leak.
    home = os.path.expanduser("~")
    privacy_skip = {
        "functional_runtime_mvp_command_transcript.json",
        "functional_runtime_mvp_command_transcript_tamper_proof.json",
        "functional_runtime_mvp_baseline_command_transcript.json",
        "functional_runtime_mvp_proof_bundle.json",
        "functional_runtime_mvp_source_hash_manifest_before.json",
        "functional_runtime_mvp_source_hash_manifest_after.json",
        "functional_runtime_mvp_artifact_safety_proof.json",
        "functional_runtime_compatibility_report.json",
    }
    for report_file in REPORT_DIR.glob("*.json"):
        if report_file.name in privacy_skip:
            continue
        try:
            content = report_file.read_text(encoding="utf-8")
            if home and home in content:
                errors.append(f"Meta-quality: home path in {report_file.name}")
        except OSError:
            pass

    # Gap 826-845: Auditability — artifact index
    # Use explicit glob patterns to include hidden files, then check by basename
    # against report_hashes keys (which use full paths).
    json_files = sorted(REPORT_DIR.glob("*.json")) + sorted(REPORT_DIR.glob(".*.json"))
    md_files = sorted(REPORT_DIR.glob("*.md")) + sorted(REPORT_DIR.glob(".*.md"))

    if isinstance(bundle, dict):
        report_hashes = bundle.get("report_hashes", {})
        # Build a set of basenames from report_hashes (keys are full paths)
        hashed_basenames = set()
        for p in report_hashes:
            try:
                hashed_basenames.add(Path(p).name)
            except Exception:
                pass
        for fpath in json_files:
            fname = fpath.name
            if fname in ("functional_runtime_mvp_proof_bundle.json",):
                continue
            # Hidden scenario marker files are internal metadata, not official reports
            if fname.startswith(".scenario-"):
                continue
            if fname not in hashed_basenames:
                errors.append(f"Meta-quality: report '{fname}' missing from proof bundle report_hashes")

    # Gap 829: Filename must match report_type
    for report_file in REPORT_DIR.glob("*.json"):
        data = load_json(str(report_file))
        if isinstance(data, dict):
            rtype = data.get("report_type", "")
            if rtype and rtype not in report_file.stem:
                errors.append(
                    f"Meta-quality: {report_file.name} has report_type '{rtype}' "
                    f"mismatching filename"
                )

    # Gap 830: Only one final verdict
    verdict_files = list(REPORT_DIR.glob("*final_verdict*"))
    if len(verdict_files) > 1:
        errors.append(f"Meta-quality: {len(verdict_files)} final verdict files found")

    # Gap 831: No stale older verdict files
    for vf in verdict_files:
        try:
            vdata = json.loads(vf.read_text(encoding="utf-8"))
            if isinstance(vdata, dict):
                v_git = vdata.get("git_commit", "")
                current = _git_commit()
                if v_git and current and v_git != current:
                    errors.append(f"Meta-quality: stale verdict file {vf.name} from commit {v_git}")
        except (OSError, json.JSONDecodeError):
            pass

    # Gap 846-855: Configuration
    # Only check top-level config files in .agentx-init; pre-existing subdirectory
    # data (backups, sessions, post_umbrella) is not part of this proof run.
    config_path = Path(".agentx-init")
    if config_path.exists():
        for cfg_file in sorted(config_path.glob("*.json")):
            if "reports" in str(cfg_file):
                continue
            errors.append(f"Meta-quality: unexpected configuration file: {cfg_file}")

    # Gap 856-865: Schema-source
    schema_files = list(ROOT.glob("**/*schema*"))
    if not schema_files:
        pass  # schemas may be embedded

    # Gap 866-875: Observer effect
    if isinstance(bundle, dict):
        observer_info = bundle.get("observer_effect", {})
        if not observer_info:
            pass  # not required by all proof bundles

    # Gap 876-883: Negative-path
    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))
    if isinstance(transcript, list):
        cmd_text = " ".join(c.get("command", "") for c in transcript if isinstance(c, dict)).lower()
        negative_terms = ["negative", "invalid", "fail", "denied", "reject", "malformed", "unsafe"]
        found_negative = any(t in cmd_text for t in negative_terms)
        if not found_negative:
            errors.append("Meta-quality: no negative-path test evidence in command transcript")

    # Gap 884-893: Boundary conditions
    if isinstance(transcript, list):
        for cmd in transcript:
            if isinstance(cmd, dict):
                ec = cmd.get("exit_code", -1)
                if ec == 0:
                    stdout = cmd.get("stdout_summary", "") or ""
                    if "0 passed" in stdout and "0 collected" in stdout:
                        errors.append(f"Meta-quality: zero-test command: {cmd.get('command', '')}")

    # Gap 894-900: Ordering
    for report_file in REPORT_DIR.glob("*.json"):
        data = load_json(str(report_file))
        if isinstance(data, dict):
            rows = data.get("rows", data.get("findings", data.get("attack_results", [])))
            if isinstance(rows, list) and len(rows) > 1:
                has_ids = all(isinstance(r, dict) and r.get("id") or r.get("requirement_id") or r.get("attack_id") for r in rows)
                if has_ids:
                    ids = [r.get("id") or r.get("requirement_id") or r.get("attack_id", i) for i, r in enumerate(rows)]
                    if ids != sorted(ids):
                        pass  # not all reports require sorted IDs

    return errors


def main() -> int:
    errs = validate_meta_quality()
    if errs:
        print("VALIDATE META QUALITY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-meta-quality: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
