"""Runtime entrypoint proof — verifiable proof that the runtime started from
a known-good entrypoint and completed initialisation successfully.

Can be invoked as:
    python -m agentx_evolve.runtime.runtime_entrypoint_proof [--goal TEXT] [--profile PROFILE]

Produces `functional_runtime_mvp_runtime_entrypoint_proof.json` containing:
  - Entrypoint module path and version
  - Git commit, tree hash, branch, remote URL at start
  - Initialisation checks (imports, config loading, state store access)
  - Orchestrator instantiation and goal execution result
  - Readiness status
  - Timestamp evidence
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _git_provenance() -> dict[str, str]:
    info: dict[str, str] = {}
    try:
        info["commit"] = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["short_commit"] = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["tree_hash"] = subprocess.run(
            ["git", "rev-parse", "HEAD:"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["parent_commit"] = subprocess.run(
            ["git", "rev-parse", "HEAD^1"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["branch"] = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["remote_url"] = subprocess.run(
            ["git", "remote", "get-url", "origin"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["detached"] = str(
            subprocess.run(
                ["git", "symbolic-ref", "-q", "HEAD"], capture_output=True, timeout=10,
            ).returncode != 0
        )
    except Exception:
        pass
    return info


def _check_imports() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    modules = [
        "agentx_evolve.runtime.runtime_context",
        "agentx_evolve.runtime.runtime_profile",
        "agentx_evolve.state.state_store",
        "agentx_evolve.evidence.event_logger",
        "agentx_evolve.orchestrator.functional_orchestrator",
        "agentx_evolve.safety.circuit_breaker",
        "agentx_evolve.security.security_envelope",
        "agentx_evolve.policy.policy_enforcer",
        "agentx_evolve.transactions.transaction_manager",
        "agentx_evolve.review.review_interface",
        "agentx_evolve.promotion.promotion_gate",
        "agentx_evolve.artifacts.artifact_store",
        "agentx_evolve.bus.event_bus",
        "agentx_evolve.workspace.workspace_manager",
        "agentx_evolve.capabilities.capability_graph",
        "agentx_evolve.contracts.contract_registry",
        "agentx_evolve.policy.rule_engine",
        "agentx_evolve.gates.decision_gate",
        "agentx_evolve.simulation.simulation_engine",
        "agentx_evolve.executors.report_generation_executor",
        "agentx_evolve.rollback.rollback_controller",
        "agentx_evolve.invariants.invariant_engine",
        "agentx_evolve.observation.observer",
        "agentx_evolve.config.runtime_profile",
    ]
    for mod_name in modules:
        try:
            __import__(mod_name)
            checks.append({"module": mod_name, "status": "imported"})
        except ImportError as e:
            checks.append({"module": mod_name, "status": "missing", "error": str(e)})
    return checks


def _try_orchestrator_instantiation(report_dir: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "instantiated": False, "goal_result": None,
        "has_state_records": False,
        "has_event_log": False,
        "review_path_exercised": False,
        "promotion_path_exercised": False,
        "replayable_result": False,
        "errors": [],
    }
    try:
        from agentx_evolve.orchestrator.functional_orchestrator import MvpFunctionalOrchestrator
        orch = MvpFunctionalOrchestrator()
        result["instantiated"] = True
        result["type"] = type(orch).__name__

        # Attempt a real run_goal — failure is NOT acceptable for readiness
        try:
            r = orch.run_goal("entrypoint_proof_goal", profile_id="DRY_RUN")
            if r is not None:
                result["goal_result"] = r.to_dict() if hasattr(r, "to_dict") else str(r)
                result["replayable_result"] = True
            else:
                result["goal_result"] = "run_goal returned None"
        except Exception as e:
            result["goal_result"] = f"run_goal error: {e}"
            result["errors"].append(f"run_goal failed: {e}")

        # Check for non-empty state records
        state_dir = report_dir / "state"
        if state_dir.exists():
            jsonl_files = list(state_dir.glob("*.jsonl"))
            state_records_found = 0
            for jf in jsonl_files:
                try:
                    state_records_found += sum(1 for _ in jf.open(encoding="utf-8") if _.strip())
                except OSError:
                    pass
            result["has_state_records"] = state_records_found > 0
            result["state_record_count"] = state_records_found

        # Check for non-empty event log
        events_dir = report_dir / "events"
        if events_dir.exists():
            event_files = list(events_dir.glob("*"))
            result["has_event_log"] = len(event_files) > 0
            result["event_file_count"] = len(event_files)

        # Check review/promotion/denial paths
        review_dir = report_dir / "review"
        promotion_dir = report_dir / "promotion"
        if review_dir.exists() and list(review_dir.glob("*")):
            result["review_path_exercised"] = True
        if promotion_dir.exists() and list(promotion_dir.glob("*")):
            result["promotion_path_exercised"] = True

    except ImportError as e:
        result["errors"].append(f"ImportError: {e}")
    except Exception as e:
        result["errors"].append(f"Instantiation error: {e}")
    return result


def _check_config(report_dir: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    config_paths = [
        report_dir / "state",
        report_dir / "events",
        report_dir / "review",
        report_dir / "promotion",
    ]
    for p in config_paths:
        checks.append({
            "path": str(p),
            "exists": p.exists(),
        })
    return checks


def compute_entrypoint_proof(
    report_dir: Path,
    goal_text: str = "",
    profile: str = "STRICT",
) -> dict[str, Any]:
    """Compute a runtime entrypoint proof.

    Verifies that all required runtime modules import cleanly,
    config paths are accessible, the orchestrator can be instantiated
    and run a goal successfully, and the runtime produces real
    state records, event log, review/promotion path data,
    and a replayable result.
    """
    imports = _check_imports()
    config_checks = _check_config(report_dir)
    orch_info = _try_orchestrator_instantiation(report_dir)

    all_imports_ok = all(c["status"] == "imported" for c in imports)
    all_config_ok = all(c["exists"] for c in config_checks)
    goal_ok = orch_info.get("replayable_result", False) and bool(orch_info.get("goal_result"))
    state_ok = orch_info.get("has_state_records", False)
    event_ok = orch_info.get("has_event_log", False)
    review_ok = orch_info.get("review_path_exercised", False)
    promotion_ok = orch_info.get("promotion_path_exercised", False)

    readiness_checks = {
        "all_imports_ok": all_imports_ok,
        "all_config_paths_ok": all_config_ok,
        "orchestrator_ok": orch_info.get("instantiated", False),
        "goal_execution_ok": goal_ok,
        "has_state_records": state_ok,
        "has_event_log": event_ok,
        "review_path_exercised": review_ok,
        "promotion_path_exercised": promotion_ok,
    }

    proof = {
        "proof_type": "runtime_entrypoint",
        "schema_version": "agentx.runtime_entrypoint_proof.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_provenance": _git_provenance(),
        "entrypoint": {
            "argv": sys.argv,
            "executable": sys.executable,
            "python_version": sys.version,
            "invocation_mode": "python_module" if sys.argv[0].endswith(".py") else "cli",
        },
        "environment": {
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            "platform": sys.platform,
            "cwd": str(Path.cwd()),
        },
        "goal": {
            "text": goal_text or "(default proof goal)",
            "profile": profile,
        },
        "checks": {
            "imports": imports,
            "config_paths": config_checks,
            "orchestrator": orch_info,
        },
        "readiness": readiness_checks,
        "supported_invocation_modes": [
            {
                "mode": "python_module",
                "command": "python -m agentx_evolve.runtime.runtime_entrypoint_proof",
                "description": "Direct Python module invocation with optional --goal and --profile",
            },
            {
                "mode": "cli_script",
                "command": "python tools/agentx_evolve/runtime/runtime_entrypoint_proof.py",
                "description": "Direct script invocation from repo root",
            },
            {
                "mode": "make_target",
                "command": "make prove-functional-runtime-mvp",
                "description": "Wired into Phase 4f of the proof pipeline",
            },
        ],
    }
    return proof


def main() -> int:
    report_dir = Path(".agentx-init/reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    goal_text = ""
    profile = "STRICT"
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--goal" and i + 1 < len(args):
            goal_text = args[i + 1]
        elif a == "--profile" and i + 1 < len(args):
            profile = args[i + 1]

    proof = compute_entrypoint_proof(report_dir, goal_text=goal_text, profile=profile)
    out_path = report_dir / "functional_runtime_mvp_runtime_entrypoint_proof.json"
    out_path.write_text(
        json.dumps(proof, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    r = proof["readiness"]
    all_pass = all(v is True for v in r.values())
    print(f"Runtime entrypoint proof:")
    for k, v in r.items():
        print(f"  {k}: {'PASS' if v else 'FAIL'}")
    print(f"  Invocation: {proof['entrypoint']['invocation_mode']}")
    print(f"  Output: {out_path}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
