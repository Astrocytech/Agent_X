from __future__ import annotations
from pathlib import Path
import json
import hashlib

from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun, EvaluationCaseResult, EvaluationScore,
    EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR, EVAL_SKIPPED,
    utc_now_iso, new_eval_id, to_dict,
)
from agentx_evolve.evaluation.evaluation_errors import (
    EVAL_FIXTURE_INVALID, EVAL_SUITE_NOT_FOUND,
    EVAL_BASELINE_MISSING, EVAL_NOT_REPRODUCIBLE,
)
from agentx_evolve.evaluation.fixture_validator import validate_benchmark_case
from agentx_evolve.evaluation.benchmark_loader import (
    load_benchmark_suite, load_benchmark_case, load_threshold, resolve_case_refs,
)
from agentx_evolve.evaluation.case_executor import execute_benchmark_case
from agentx_evolve.evaluation.comparator_engine import compare_observed_to_expected, run_comparator
from agentx_evolve.evaluation.score_calculator import calculate_run_score
from agentx_evolve.evaluation.threshold_checker import check_thresholds
from agentx_evolve.evaluation.regression_comparator import compare_against_baseline, load_baseline_run
from agentx_evolve.evaluation.report_writer import write_evaluation_report
from agentx_evolve.evaluation.evaluation_evidence import (
    write_evaluation_evidence_manifest,
    append_evaluation_run_history,
    append_evaluation_result_history,
    append_evaluation_case_history,
    append_regression_comparison_history,
    append_threshold_decision_history,
    write_latest_run_artifact,
    write_latest_result_artifact,
    write_latest_regression_artifact,
    write_latest_threshold_artifact,
    write_benchmark_lockfile,
    write_promotion_gate_summary,
    write_completion_record,
)
from agentx_evolve.evaluation.baseline_manager import write_candidate_baseline
from agentx_evolve.evaluation.run_config import (
    load_run_config, validate_run_config, merge_run_config_defaults, normalize_execution_mode,
)
from agentx_evolve.evaluation.fixture_lock import build_fixture_lock, verify_fixture_lock
from agentx_evolve.evaluation.mutation_guard import capture_source_state, compare_source_state


def run_evaluation(
    suite_path: Path,
    repo_root: Path,
    run_config_path: Path | None = None,
    first_run: bool = False,
    execution_mode: str = "OFFLINE_FIXTURE",
    dry_run: bool = False,
    allow_tool_adapter_cases: bool = False,
    write_reports: bool = True,
    write_evidence: bool = True,
    allow_candidate_baseline_write: bool = False,
) -> EvaluationRun:
    config_raw = load_run_config(run_config_path, repo_root)
    config_raw["execution_mode"] = execution_mode
    config_raw["first_run"] = first_run
    config_raw["dry_run"] = dry_run
    config_raw["allow_tool_adapter_cases"] = allow_tool_adapter_cases
    config_raw["write_reports"] = write_reports
    config_raw["write_evidence"] = write_evidence
    config_raw["allow_candidate_baseline_write"] = allow_candidate_baseline_write
    config = merge_run_config_defaults(config_raw)
    valid, errors = validate_run_config(config)
    if not valid:
        raise ValueError(f"Run config invalid: {errors}")

    if not suite_path.exists():
        raise FileNotFoundError(f"{EVAL_SUITE_NOT_FOUND}: {suite_path}")

    suite = load_benchmark_suite(suite_path)
    fixture_root = suite_path.parent

    case_refs = resolve_case_refs(suite, fixture_root)
    fixture_lock = build_fixture_lock(fixture_root, suite_path)
    lock_ok, lock_errors = verify_fixture_lock(fixture_lock, fixture_root)

    before_state = capture_source_state(repo_root)

    case_results: list[EvaluationCaseResult] = []
    for ref in case_refs:
        if not ref.exists():
            case_results.append(_make_skipped(ref.stem, "case_not_found"))
            continue
        case = load_benchmark_case(ref)
        case_dict = {
            "schema_version": "1.0",
            "schema_id": "evaluation_benchmark_case.schema.json",
            "case_id": case.case_id,
            "case_type": case.case_type,
            "warnings": case.warnings,
            "errors": case.errors,
        }
        valid_fixture, fixture_errors = validate_benchmark_case(case_dict)
        if not valid_fixture:
            case_results.append(_make_skipped(case.case_id, EVAL_FIXTURE_INVALID, "; ".join(fixture_errors)))
            continue
        case_result = execute_benchmark_case(case, repo_root, dry_run=dry_run)
        if case_result.expected_result:
            from agentx_evolve.evaluation.evaluation_models import EvaluationExpectedResult
            expected_obj = EvaluationExpectedResult(**{
                k: v for k, v in case_result.expected_result.items()
                if k in EvaluationExpectedResult.__dataclass_fields__
            })
            details = compare_observed_to_expected(case_result.observed_result, expected_obj)
            case_result.comparison_details = details
            case_result.passed = all(d.get("passed", False) for d in details)
            case_result.score = 1.0 if case_result.passed else 0.0
            case_result.weighted_score = case_result.score * case_result.weight
            if not case_result.passed:
                case_result.status = EVAL_FAIL
        case_results.append(case_result)

    score = calculate_run_score(case_results)
    score_summary = to_dict(score)

    threshold = None
    if suite.default_threshold_id:
        threshold_path = fixture_root / f"{suite.default_threshold_id}.json"
        if threshold_path.exists():
            threshold = load_threshold(threshold_path)

    threshold_summary = {}
    if threshold is not None:
        threshold_summary = check_thresholds(score, threshold, case_results)

    regression_summary = None
    if suite.baseline_ref:
        baseline_path = fixture_root / suite.baseline_ref
        if baseline_path.exists():
            try:
                baseline_run = load_baseline_run(baseline_path)
                current_run_for_comp = EvaluationRun(
                    run_id=new_eval_id("run_comp"),
                    suite_id=suite.suite_id,
                    case_results=case_results,
                    score_summary=score_summary,
                )
                regression_comparison = compare_against_baseline(
                    current_run_for_comp,
                    baseline_run,
                    first_run=first_run,
                )
                regression_summary = to_dict(regression_comparison)
            except Exception as e:
                regression_summary = {"error": str(e)}
        elif first_run:
            regression_summary = {"status": "REGRESSION_BASELINE_MISSING", "message": "First run, no baseline"}
        else:
            regression_summary = {"error": f"{EVAL_BASELINE_MISSING}: baseline {suite.baseline_ref} not found"}

    run = EvaluationRun(
        run_id=new_eval_id("run"),
        suite_id=suite.suite_id,
        timestamp=utc_now_iso(),
        source_component="EvaluationHarness",
        execution_mode=normalize_execution_mode(config),
        case_results=case_results,
        score_summary=score_summary,
        threshold_summary=threshold_summary,
        regression_summary=regression_summary,
    )

    after_state = capture_source_state(repo_root)
    mutation_result = compare_source_state(before_state, after_state, repo_root / ".agentx-init")
    if mutation_result["source_mutated"]:
        run.warnings.append(f"{EVAL_NOT_REPRODUCIBLE}: Source mutation detected: {mutation_result['changes']}")

    if write_evidence:
        write_evaluation_evidence_manifest(run, repo_root)
        append_evaluation_run_history(run, repo_root)
        for cr in case_results:
            append_evaluation_case_history(cr, repo_root)
        completion = write_completion_record(run, repo_root)
        completion_path = repo_root / ".agentx-init" / "evaluation" / "evaluation_completion_record.json"
        if completion_path.exists():
            completion_sha256 = hashlib.sha256(completion_path.read_bytes()).hexdigest()
            completion["completion_record_sha256"] = completion_sha256
            completion_path.write_text(json.dumps(completion, indent=2))
        for cr in case_results:
            append_evaluation_result_history(cr, repo_root)
        if regression_summary:
            append_regression_comparison_history(regression_summary, repo_root)
        if threshold_summary:
            append_threshold_decision_history(threshold_summary, repo_root)
        write_latest_run_artifact(run, repo_root)
        write_latest_result_artifact(run, repo_root)
        if regression_summary:
            write_latest_regression_artifact(regression_summary, repo_root)
        if threshold_summary:
            write_latest_threshold_artifact(threshold_summary, repo_root)
        write_benchmark_lockfile(to_dict(fixture_lock), repo_root)
        if regression_summary:
            gate_data = {
                "gate_id": f"gate_{run.run_id}",
                "suite_id": run.suite_id,
                "run_id": run.run_id,
                "timestamp": utc_now_iso(),
                "status": "PASS" if regression_summary.get("status") == "REGRESSION_PASS" else "BLOCKED",
            }
            write_promotion_gate_summary(gate_data, repo_root)

    if write_reports:
        write_evaluation_report(run, repo_root)

    if allow_candidate_baseline_write and not suite.baseline_ref:
        write_candidate_baseline(run, repo_root)

    return run


def _make_skipped(case_id: str, reason: str, detail: str | None = None) -> EvaluationCaseResult:
    msg = f"{reason}"
    if detail:
        msg += f": {detail}"
    return EvaluationCaseResult(
        case_result_id=new_eval_id("cr"),
        case_id=case_id,
        run_id="",
        timestamp=utc_now_iso(),
        status=EVAL_SKIPPED,
        score=0.0,
        max_score=1.0,
        weight=1.0,
        weighted_score=0.0,
        passed=False,
        message=msg,
    )
