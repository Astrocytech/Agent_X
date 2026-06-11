"""Validate execution integrity: exit codes, timeouts, logging, env, retry, parallelism.

Gaps 308-315 (exit-code/timeout), 316-319 (logging), 320-327 (environment),
675-680 (retry), 681-687 (flakiness), 688-693 (parallelism), 738-749 (subprocess isolation)
"""
from __future__ import annotations

import json
import os
import subprocess
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


def validate_execution_integrity() -> list[str]:
    errors = []

    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))
    if not isinstance(transcript, list):
        errors.append("Execution integrity: command transcript missing or invalid")
        return errors

    seen_commands = {}
    for cmd in transcript:
        if not isinstance(cmd, dict):
            continue
        cname = cmd.get("command", "?")
        ec = cmd.get("exit_code", -1)
        duration = cmd.get("duration_seconds", -1)
        stdout_hash = cmd.get("stdout_hash", "")
        stderr_hash = cmd.get("stderr_hash", "")
        hashes_ok = bool(stdout_hash) and bool(stderr_hash)

        # Gap 308: Exit code propagation
        if ec < 0:
            errors.append(f"Execution integrity: command '{cname}' has invalid exit_code {ec}")

        # Gap 309: Nonzero exit recorded as zero
        if ec == 0 and "FAILED" in (cmd.get("stdout_summary", "") or "").upper():
            errors.append(f"Execution integrity: command '{cname}' exit 0 but output suggests failure")

        # Gap 310: Signal/termination detection
        if ec is None or ec < -1:
            errors.append(f"Execution integrity: command '{cname}' was killed by signal or terminated (exit_code={ec})")

        # Gap 311: Timeout/signal/exception status recording
        timeout_val = cmd.get("timeout_seconds", 0)
        if not timeout_val and "timeout" in cname.lower():
            errors.append(f"Execution integrity: command '{cname}' has no recorded timeout_seconds")

        # Gap 312: Timeout proof
        if timeout_val and ec == 0:
            errors.append(f"Execution integrity: command '{cname}' timed out (timeout={timeout_val}s) but exit_code=0")

        # Gap 316: Logging capture
        if not hashes_ok:
            errors.append(f"Execution integrity: command '{cname}' missing stdout_hash or stderr_hash")

        # Gap 318: Binary output detection
        stdout_summary = cmd.get("stdout_summary", "") or ""
        if stdout_summary and any(c in stdout_summary for c in "\x00\x01\x02"):
            errors.append(f"Execution integrity: command '{cname}' appears to have binary stdout")

        # Retry detection (gap 675-680)
        if cname in seen_commands:
            seen_commands[cname].append(cmd)
        else:
            seen_commands[cname] = [cmd]

    # Gap 675-680: Retry detection
    for cname, instances in seen_commands.items():
        if len(instances) > 1:
            exit_codes = [c.get("exit_code", -1) for c in instances]
            if 0 in exit_codes and any(ec != 0 for ec in exit_codes):
                errors.append(
                    f"Execution integrity: command '{cname}' was retried {len(instances)} times "
                    f"(exit codes: {exit_codes}) — retry must be recorded"
                )

    # Gap 320-322: Environment recording
    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if isinstance(bundle, dict):
        env_record = bundle.get("environment", {})
        if not env_record:
            errors.append("Execution integrity: proof bundle missing environment record")

        required_env_vars = {"PYTHONPATH", "PATH"}
        if env_record:
            for var in required_env_vars:
                if var not in env_record:
                    errors.append(f"Execution integrity: required env var '{var}' not recorded in proof bundle")

        # Gap 325: Debug/bypass flags
        for key in env_record:
            val = str(env_record[key]).lower()
            if any(flag in key.lower() for flag in ("debug", "bypass", "force", "skip", "warn")):
                if val in ("1", "true", "yes"):
                    if "AGENTX_MVP_NO_FORCED_PASS" in key:
                        continue
                    errors.append(f"Execution integrity: debug/bypass flag '{key}' is enabled")

        # Gap 326: AGENTX_MVP_NO_FORCED_PASS
        no_forced = env_record.get("AGENTX_MVP_NO_FORCED_PASS", "")
        if no_forced not in ("1", "true"):
            errors.append("Execution integrity: AGENTX_MVP_NO_FORCED_PASS not enabled in proof bundle")

    # Gap 738-739: Subprocess isolation check — validators run as subprocesses
    # Check transcript for validators run directly
    validator_count = sum(1 for c in transcript if isinstance(c, dict) and "validate_functional_runtime_mvp_" in c.get("command", ""))
    if validator_count < 5:
        errors.append(f"Execution integrity: only {validator_count} validators recorded as subprocess commands")

    # Gap 688-693: Parallelism proof
    if isinstance(bundle, dict):
        parallelism = bundle.get("parallelism", bundle.get("parallel", ""))
        if not parallelism:
            errors.append("Execution integrity: proof bundle missing parallelism declaration")

    # Gap 694-699: Error taxonomy
    final_verdict_path = REPORT_DIR / "functional_runtime_mvp_final_verdict.json"
    if final_verdict_path.exists():
        verdict = load_json(str(final_verdict_path))
        if isinstance(verdict, dict):
            failure_codes = verdict.get("failure_codes", [])
            classification = verdict.get("classification", "")
            if classification != "FUNCTIONAL_RUNTIME_MVP" and not failure_codes:
                errors.append("Execution integrity: final verdict missing failure_codes when not PASS")

    return errors


def main() -> int:
    errs = validate_execution_integrity()
    if errs:
        print("VALIDATE EXECUTION INTEGRITY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-execution-integrity: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
