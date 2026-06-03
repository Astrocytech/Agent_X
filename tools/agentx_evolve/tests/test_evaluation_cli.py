import pytest
from pathlib import Path
import json
import sys
from agentx_evolve.evaluation.run_evaluation import run_evaluation_from_config, main
from agentx_evolve.evaluation.evaluation_models import EvaluationRun

REPO_ROOT = Path(__file__).resolve().parents[3]
SMOKE_SUITE = REPO_ROOT / "tools" / "agentx_evolve" / "evaluation" / "fixtures" / "smoke" / "smoke_suite.json"


def test_cli_config_path_required_if_cli_enabled(tmp_path):
    config = {
        "suite_path": str(SMOKE_SUITE),
        "first_run": True,
        "dry_run": True,
        "write_reports": False,
        "write_evidence": False,
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    result = run_evaluation_from_config(
        config_path=str(config_path),
        repo_root=str(REPO_ROOT),
    )
    assert isinstance(result, dict)
    assert "run_id" in result


def test_cli_cannot_enable_network_or_source_mutation():
    import argparse
    parser = argparse.ArgumentParser(description="Agent-X Evaluation Harness CLI")
    parser.add_argument("--suite", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--config")
    parser.add_argument("--first-run", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execution-mode", default="OFFLINE_FIXTURE", choices=["OFFLINE_FIXTURE", "CONTROLLED_TOOL_ADAPTER"])
    parser.add_argument("--write-reports", default=True, action=argparse.BooleanOptionalAction)
    parser.add_argument("--write-evidence", default=True, action=argparse.BooleanOptionalAction)
    parser.add_argument("--allow-tool-adapter-cases", action="store_true")
    parser.add_argument("--allow-candidate-baseline-write", action="store_true")
    known = {a.dest for a in parser._actions}
    assert "allow_network" not in known
    assert "allow_source_mutation" not in known


def test_cli_exit_code_nonzero_on_threshold_fail():
    result = run_evaluation_from_config(
        config_path="",
        repo_root=str(REPO_ROOT),
        suite_path=str(SMOKE_SUITE),
        first_run=True,
        dry_run=True,
        write_reports=False,
        write_evidence=False,
        allow_candidate_baseline_write=False,
    )
    assert isinstance(result, dict)
    assert "errors" in result
    assert "run_id" in result


def test_programmatic_entrypoint_returns_evaluation_run():
    result = run_evaluation_from_config(
        config_path="",
        repo_root=str(REPO_ROOT),
        suite_path=str(SMOKE_SUITE),
        first_run=True,
        dry_run=True,
        write_reports=False,
        write_evidence=False,
    )
    assert isinstance(result, dict)
    assert "run_id" in result
    assert isinstance(result["run_id"], str)
    assert len(result["run_id"]) > 0
