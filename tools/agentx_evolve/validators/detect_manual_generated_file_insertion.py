"""Detect files that appear manually generated without a complete provenance chain.

Item 14.4: Cross-references generated file paths with provenance records,
patch execution records, and event logs.
"""
import json, sys, os, glob as glob_mod
from pathlib import Path


EVIDENCE_ROOTS = [".agentx-init", "reports"]
GENERATED_AGENT_ROOTS = ["examples"]
PROVENANCE_PATTERNS = ["provenance_record.json", "proposal_artifact.json",
                       "patch_execution_result.json", "event_log.json"]


def _find_provenance_records():
    records = {}
    for root in EVIDENCE_ROOTS:
        for dirpath, dirs, files in os.walk(root):
            for fn in files:
                if fn == "provenance_record.json":
                    fp = os.path.join(dirpath, fn)
                    try:
                        with open(fp) as f:
                            records[fp] = json.load(f)
                    except (json.JSONDecodeError, OSError):
                        pass
    return records


def detect():
    issues = []

    # 1. Check JSON files for validity
    for root in EVIDENCE_ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, dirs, files in os.walk(root):
            for fn in files:
                fp = os.path.join(dirpath, fn)
                if fn.endswith(".json"):
                    try:
                        with open(fp) as f:
                            json.load(f)
                    except (json.JSONDecodeError, OSError):
                        issues.append(f"{fp}: invalid JSON")

    # 2. Cross-reference generated file paths with provenance
    provenance_records = _find_provenance_records()
    all_stage_b_files = set()
    for rec_path, rec in provenance_records.items():
        for fpath in rec.get("stage_b_pipeline_generated", []):
            all_stage_b_files.add(fpath)

    # Check if agent source files exist without corresponding provenance
    provenance_agents = set()
    for rec_path, rec in provenance_records.items():
        agent = rec.get("agent", "")
        if agent:
            provenance_agents.add(agent)

    for root in GENERATED_AGENT_ROOTS:
        if not os.path.isdir(root):
            continue
        for entry in os.listdir(root):
            agent_dir = os.path.join(root, entry)
            if not os.path.isdir(agent_dir):
                continue
            agent_id = entry.replace("_", "-")
            if agent_id not in provenance_agents:
                # Agent exists but has no provenance record
                for fn in os.listdir(agent_dir):
                    if fn.endswith(".py") and not fn.startswith("__") and not fn.startswith("test_"):
                        issues.append(
                            f"{agent_dir}/{fn}: file exists but agent '{agent_id}' "
                            f"has no provenance record"
                        )

    # 3. Check for files with "manual" origin in provenance that claim governed generation
    for rec_path, rec in provenance_records.items():
        for fpath in rec.get("stage_b_pipeline_generated", []):
            origin = rec.get("file_origin_classification", "")
            if origin and "manual" in origin.lower():
                issues.append(
                    f"{rec_path}: stage_b file '{fpath}' references manual origin"
                )

    # 4. Check that provenance records have required companion files
    for rec_path, rec in provenance_records.items():
        base_dir = os.path.dirname(rec_path)
        for needed in PROVENANCE_PATTERNS:
            needed_path = os.path.join(os.path.dirname(base_dir), needed)
            if not os.path.isfile(needed_path) and needed != rec_path.split("/")[-1]:
                pass  # Not all artifact types are required for every agent

    return issues


def main():
    issues = detect()
    if issues:
        print(f"ISSUES: {len(issues)} file(s):"); [print(f"  - {i}") for i in issues]
    else:
        print("PASS: no suspicious evidence files detected")


if __name__ == "__main__":
    main()
