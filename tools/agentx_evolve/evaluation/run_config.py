from __future__ import annotations
from pathlib import Path
import json


def load_run_config(path: Path | None, repo_root: Path) -> dict:
    if path and path.exists():
        return json.loads(path.read_text())
    return {}


def validate_run_config(config: dict) -> tuple[bool, list[str]]:
    errors = []
    timeout = config.get("timeout_seconds", 300)
    if not isinstance(timeout, int) or timeout < 1:
        errors.append("timeout_seconds must be a positive integer")
    max_cases = config.get("max_case_count", 100)
    if not isinstance(max_cases, int) or max_cases < 1:
        errors.append("max_case_count must be a positive integer")
    return (len(errors) == 0, errors)


def merge_run_config_defaults(config: dict) -> dict:
    defaults = {
        "execution_mode": "OFFLINE_FIXTURE",
        "first_run": False,
        "case_filter": [],
        "include_tags": [],
        "exclude_tags": [],
        "policy_context_ref": None,
        "dry_run": False,
        "timeout_seconds": 300,
        "max_case_count": 100,
        "write_reports": True,
        "write_evidence": True,
        "allow_tool_adapter_cases": False,
        "allow_candidate_baseline_write": False,
    }
    for k, v in defaults.items():
        config.setdefault(k, v)
    return config


def normalize_execution_mode(config: dict) -> str:
    mode = config.get("execution_mode", "OFFLINE_FIXTURE")
    if mode.upper() in ("OFFLINE_FIXTURE", "CONTROLLED_TOOL_ADAPTER"):
        return mode.upper()
    return "OFFLINE_FIXTURE"
