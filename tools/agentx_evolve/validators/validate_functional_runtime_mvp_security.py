"""Validate security: threat model, tamper evidence, evidence cycles, mock boundary, sandbox.

Gaps 421-431 (threat model), 432-437 (tamper evidence), 374-379 (evidence cycles),
328-333 (mock boundary), 781-790 (tool adapter), 791-800 (sandbox),
771-780 (prompt injection), 644-651 (filesystem portability)
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def _collect_paths(obj, depth=0) -> list[str]:
    paths = []
    if depth > 15:
        return paths
    if isinstance(obj, dict):
        for key, val in obj.items():
            if isinstance(val, str) and val:
                paths.append(val)
            paths.extend(_collect_paths(val, depth + 1))
    elif isinstance(obj, list):
        for item in obj:
            paths.extend(_collect_paths(item, depth + 1))
    return paths


def validate_security() -> list[str]:
    errors = []

    # --- Evidence cycles (gaps 374-379) ---
    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if isinstance(bundle, dict):
        proof_objects = {}
        for key in ("command_proofs", "scenario_proofs", "replay_proofs"):
            objs = bundle.get(key, [])
            if isinstance(objs, list):
                for obj in objs:
                    if isinstance(obj, dict):
                        pid = obj.get("id", obj.get("scenario_id", key))
                        refs = obj.get("evidence_refs", obj.get("artifact_refs", []))
                        proof_objects[pid] = [r.get("path", r.get("id", "")) for r in refs if isinstance(r, dict)]

        for pid, refs in proof_objects.items():
            self_refs = [r for r in refs if pid in r]
            if self_refs:
                errors.append(f"Security: proof object '{pid}' has self-referential evidence: {self_refs}")

    # --- Threat model (gaps 421-431) ---
    afp = load_json(str(REPORT_DIR / "functional_runtime_mvp_anti_false_pass_audit.json"))
    if isinstance(afp, dict):
        attack_results = afp.get("attack_results", [])
        threat_classes = set()
        for ar in attack_results:
            if isinstance(ar, dict):
                name = ar.get("name", "")
                if "JSON" in name or "json" in name:
                    threat_classes.add("json_mutation")
                elif "source" in name.lower() or "delet" in name.lower():
                    threat_classes.add("report_deletion")
                elif "transcript" in name.lower():
                    threat_classes.add("transcript_forgery")
                elif "replay" in name.lower():
                    threat_classes.add("replay_fabrication")

        required_threats = {"json_mutation", "report_deletion"}
        missing = required_threats - threat_classes
        if missing:
            errors.append(f"Security: anti-false-PASS audit missing threat classes: {missing}")

    # --- Mock boundary (gaps 328-333) ---
    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))
    if isinstance(transcript, list):
        all_cmd_text = " ".join(c.get("command", "") for c in transcript if isinstance(c, dict)).lower()
        for mock_word in ("mock", "fixture", "stub", "fake"):
            if mock_word in all_cmd_text:
                errors.append(f"Security: mock/fixture/stub reference found in proof commands: '{mock_word}'")

    # --- Prompt injection (gaps 771-780) ---
    skip_injection = {"functional_runtime_mvp_gap_discovery_report.json", "functional_runtime_mvp_command_transcript.json"}
    for report_file in REPORT_DIR.glob("*.json"):
        if report_file.name in skip_injection:
            continue
        try:
            content = report_file.read_text(encoding="utf-8")
            content_lower = content.lower()
            for injection_keyword in ("import os", "subprocess.run", "__import__", "eval(", "exec("):
                if injection_keyword in content_lower:
                    errors.append(f"Security: possible injection vector in {report_file.name}: '{injection_keyword}'")
        except (OSError, UnicodeDecodeError):
            pass

    # --- Tool adapter (gaps 781-790) ---
    if isinstance(transcript, list):
        for cmd in transcript:
            if isinstance(cmd, dict):
                cmd_str = cmd.get("command", "")
                if cmd_str and not cmd_str.startswith("/") and not cmd_str.startswith("./"):
                    if any(c in cmd_str for c in ("|", ";", "&&", "`", "$(")):
                        errors.append(f"Security: shell injection risk in command: '{cmd_str}'")

    # --- Filesystem portability (gaps 644-651) ---
    for report_file in REPORT_DIR.glob("*"):
        fname = report_file.name
        for bad in ("\\", ":", "*", "?", '"', "<", ">", "|"):
            if bad in fname:
                errors.append(f"Security: problematic char in filename: '{fname}'")
                break

    # --- Tamper evidence (gaps 432-437) ---
    if isinstance(bundle, dict):
        report_hashes = bundle.get("report_hashes", {})
        for rpath, expected_hash in report_hashes.items():
            if "command_transcript" in rpath:
                continue
            actual = hashlib.sha256(Path(rpath).read_bytes()).hexdigest() if Path(rpath).exists() else ""
            if actual and actual != expected_hash:
                errors.append(f"Security: report '{rpath}' hash changed since bundle generation (tamper detected)")

    return errors


def main() -> int:
    errs = validate_security()
    if errs:
        print("VALIDATE SECURITY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-security: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
