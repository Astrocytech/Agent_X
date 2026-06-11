#!/usr/bin/env python3
import json, os, sys

BASE = os.path.join(".agentx-init", "post_umbrella", "phase_3_example_agents", "provenance")

AGENTS = ["clothing_advice_agent", "daily_planning_agent"]

GOVERNANCE_FILES = [
    "proposal_artifact.json",
    "risk_classification.json",
    "policy_approval.json",
    "human_review.json",
    "promotion_decision.json",
]

TOP_LEVEL_FILES = [
    "provenance_record.json",
    "event_log.json",
    "clean_checkout_replay.json",
    "sabotage_check_result.json",
]

REQUIRED_TOP_LEVEL_KEYS = {
    "proposal_artifact.json": ["artifact_type", "status"],
    "risk_classification.json": ["classification", "classified_by"],
    "policy_approval.json": ["approval_status", "approved_by"],
    "human_review.json": ["review_id", "decision"],
    "promotion_decision.json": ["promotion_id", "decision"],
    "provenance_record.json": ["artifact_type", "agent"],
    "event_log.json": None,
    "clean_checkout_replay.json": ["replay_id", "verdict"],
    "sabotage_check_result.json": ["check_id", "status"],
}


def _check_file(path: str, required_keys: list[str] | None = None) -> list[str]:
    errs: list[str] = []
    if not os.path.isfile(path):
        errs.append(f"MISSING: {path}")
        return errs
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        errs.append(f"INVALID JSON: {path} — {e}")
        return errs
    if required_keys:
        for k in required_keys:
            if k not in data:
                errs.append(f"MISSING KEY '{k}' in {path}")
    return errs


def main() -> None:
    errors: list[str] = []

    for agent in AGENTS:
        agent_dir = os.path.join(BASE, agent)
        gov_dir = os.path.join(agent_dir, "governance")

        # Check governance subdirectory
        if not os.path.isdir(gov_dir):
            errors.append(f"MISSING governance directory: {gov_dir}")
        else:
            for fname in GOVERNANCE_FILES:
                fpath = os.path.join(gov_dir, fname)
                errs = _check_file(fpath, REQUIRED_TOP_LEVEL_KEYS.get(fname))
                errors.extend(errs)

        # Check top-level files
        for fname in TOP_LEVEL_FILES:
            fpath = os.path.join(agent_dir, fname)
            errs = _check_file(fpath, REQUIRED_TOP_LEVEL_KEYS.get(fname))
            errors.extend(errs)

        # Check top-level governance copies (legacy)
        for fname in GOVERNANCE_FILES:
            fpath = os.path.join(agent_dir, fname)
            errs = _check_file(fpath, REQUIRED_TOP_LEVEL_KEYS.get(fname))
            errors.extend(errs)

        # Check source_diff_report (shared file)
        shared_diff = os.path.join(BASE, "source_diff_report.md")
        if not os.path.isfile(shared_diff):
            errors.append(f"MISSING shared: source_diff_report.md")

    # Check provenance record agent field consistency
    for agent in AGENTS:
        prov_path = os.path.join(BASE, agent, "provenance_record.json")
        if os.path.isfile(prov_path):
            try:
                with open(prov_path) as f:
                    prov = json.load(f)
                expected_agent = agent.replace("_", "-")
                actual = prov.get("agent", "")
                if expected_agent not in actual and actual not in agent:
                    errors.append(
                        f"AGENT MISMATCH in {prov_path}: expected '{expected_agent}', got '{actual}'"
                    )
            except (json.JSONDecodeError, ValueError):
                errors.append(f"INVALID JSON (checked for agent field): {prov_path}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    print(f"PASS: post-umbrella agent lifecycle artifacts validated ({len(AGENTS)} agents)")
    sys.exit(0)


if __name__ == "__main__":
    main()
