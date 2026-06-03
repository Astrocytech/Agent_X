from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
import json
import uuid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_eval_id(prefix: str = "eval") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def stable_json_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def to_dict(obj: object) -> dict:
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dataclass_fields__"):
        return {f.name: _to_dict_val(getattr(obj, f.name)) for f in obj.__dataclass_fields__.values()}
    return dict(obj)


def _to_dict_val(val):
    if val is None or isinstance(val, (str, int, float, bool)):
        return val
    if isinstance(val, (list, tuple)):
        return [_to_dict_v2(v) for v in val]
    if isinstance(val, dict):
        return {k: _to_dict_v2(v) for k, v in val.items()}
    if hasattr(val, "__dataclass_fields__"):
        return to_dict(val)
    return str(val)


def _to_dict_v2(val):
    if val is None or isinstance(val, (str, int, float, bool)):
        return val
    if isinstance(val, (list, tuple)):
        return [_to_dict_v2(v) for v in val]
    if isinstance(val, dict):
        return {k: _to_dict_v2(v) for k, v in val.items()}
    if hasattr(val, "__dataclass_fields__"):
        return to_dict(val)
    return str(val)


EVAL_PASS = "EVAL_PASS"
EVAL_FAIL = "EVAL_FAIL"
EVAL_BLOCKED = "EVAL_BLOCKED"
EVAL_ERROR = "EVAL_ERROR"
EVAL_SKIPPED = "EVAL_SKIPPED"
REGRESSION_PASS = "REGRESSION_PASS"
REGRESSION_FAIL = "REGRESSION_FAIL"
REGRESSION_BASELINE_MISSING = "REGRESSION_BASELINE_MISSING"
REGRESSION_NOT_APPLICABLE = "REGRESSION_NOT_APPLICABLE"
THRESHOLD_PASS = "THRESHOLD_PASS"
THRESHOLD_FAIL = "THRESHOLD_FAIL"

ALL_EVAL_STATUSES = [
    EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR, EVAL_SKIPPED,
    REGRESSION_PASS, REGRESSION_FAIL, REGRESSION_BASELINE_MISSING, REGRESSION_NOT_APPLICABLE,
    THRESHOLD_PASS, THRESHOLD_FAIL,
]

STATIC_EXPECTED_RESULT = "STATIC_EXPECTED_RESULT"
TOOL_CALL_EXPECTED_RESULT = "TOOL_CALL_EXPECTED_RESULT"
POLICY_DENIAL_EXPECTED_RESULT = "POLICY_DENIAL_EXPECTED_RESULT"
REGRESSION_EXPECTED_FAILURE = "REGRESSION_EXPECTED_FAILURE"
ARTIFACT_EXPECTED_RESULT = "ARTIFACT_EXPECTED_RESULT"
REPORT_GENERATION_EXPECTED_RESULT = "REPORT_GENERATION_EXPECTED_RESULT"
NEGATIVE_FIXTURE_VALIDATION = "NEGATIVE_FIXTURE_VALIDATION"

ALL_CASE_TYPES = [
    STATIC_EXPECTED_RESULT, TOOL_CALL_EXPECTED_RESULT, POLICY_DENIAL_EXPECTED_RESULT,
    REGRESSION_EXPECTED_FAILURE, ARTIFACT_EXPECTED_RESULT, REPORT_GENERATION_EXPECTED_RESULT,
    NEGATIVE_FIXTURE_VALIDATION,
]

EXACT_MATCH = "EXACT_MATCH"
CONTAINS = "CONTAINS"
REGEX_MATCH = "REGEX_MATCH"
STATUS_MATCH = "STATUS_MATCH"
FAILURE_CLASS_MATCH = "FAILURE_CLASS_MATCH"
ARTIFACT_EXISTS = "ARTIFACT_EXISTS"
NUMERIC_EQUALS = "NUMERIC_EQUALS"
NUMERIC_AT_LEAST = "NUMERIC_AT_LEAST"
NUMERIC_AT_MOST = "NUMERIC_AT_MOST"
LIST_CONTAINS = "LIST_CONTAINS"
DICT_HAS_KEY = "DICT_HAS_KEY"
CUSTOM_STATIC_CHECK = "CUSTOM_STATIC_CHECK"

ALL_COMPARATOR_TYPES = [
    EXACT_MATCH, CONTAINS, REGEX_MATCH, STATUS_MATCH, FAILURE_CLASS_MATCH,
    ARTIFACT_EXISTS, NUMERIC_EQUALS, NUMERIC_AT_LEAST, NUMERIC_AT_MOST,
    LIST_CONTAINS, DICT_HAS_KEY, CUSTOM_STATIC_CHECK,
]


IS_SCHEMA_VALID_TOOL_RESULT = "IS_SCHEMA_VALID_TOOL_RESULT"
IS_SCHEMA_VALID_EVALUATION_RESULT = "IS_SCHEMA_VALID_EVALUATION_RESULT"
HAS_EVIDENCE_REFS = "HAS_EVIDENCE_REFS"
HAS_ARTIFACT_REFS = "HAS_ARTIFACT_REFS"
IS_REDACTED = "IS_REDACTED"

ALL_STATIC_CHECKS = [
    IS_SCHEMA_VALID_TOOL_RESULT, IS_SCHEMA_VALID_EVALUATION_RESULT,
    HAS_EVIDENCE_REFS, HAS_ARTIFACT_REFS, IS_REDACTED,
]


@dataclass
class BenchmarkSuite:
    schema_version: str = "1.0"
    schema_id: str = "evaluation_benchmark_suite.schema.json"
    suite_id: str = ""
    suite_name: str = ""
    description: str = ""
    created_at: str = ""
    source_component: str = ""
    case_refs: list[str] = field(default_factory=list)
    default_threshold_id: str | None = None
    baseline_ref: str | None = None
    first_run_allowed: bool = False
    tags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class BenchmarkCase:
    schema_version: str = "1.0"
    schema_id: str = "evaluation_benchmark_case.schema.json"
    case_id: str = ""
    case_name: str = ""
    description: str = ""
    case_type: str = ""
    target_component: str = ""
    severity: str = "normal"
    weight: float = 1.0
    input_ref: str | None = None
    input_payload: dict = field(default_factory=dict)
    expected_result: dict = field(default_factory=dict)
    threshold_id: str | None = None
    timeout_seconds: int = 30
    tags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class EvaluationCaseInput:
    schema_version: str = "1.0"
    schema_id: str = "evaluation_case_input.schema.json"
    input_id: str = ""
    source_component: str = ""
    input_type: str = ""
    payload: dict = field(default_factory=dict)
    artifact_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class EvaluationExpectedResult:
    schema_version: str = "1.0"
    schema_id: str = "evaluation_expected_result.schema.json"
    expected_result_id: str = ""
    expected_status: str = ""
    expected_failure_class: str | None = None
    comparators: list[dict] = field(default_factory=list)
    required_artifacts: list[str] = field(default_factory=list)
    minimum_score: float | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class EvaluationCaseResult:
    schema_version: str = "1.0"
    schema_id: str = "evaluation_case_result.schema.json"
    case_result_id: str = ""
    case_id: str = ""
    run_id: str = ""
    timestamp: str = ""
    status: str = ""
    score: float = 0.0
    max_score: float = 1.0
    weight: float = 1.0
    weighted_score: float = 0.0
    passed: bool = False
    message: str = ""
    observed_result: dict = field(default_factory=dict)
    expected_result: dict = field(default_factory=dict)
    comparison_details: list[dict] = field(default_factory=list)
    failure_class: str | None = None
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class EvaluationRun:
    schema_version: str = "1.0"
    schema_id: str = "evaluation_run.schema.json"
    run_id: str = ""
    suite_id: str = ""
    timestamp: str = ""
    source_component: str = ""
    repo_commit: str | None = None
    runner_version: str = "1.0.0"
    execution_mode: str = "OFFLINE_FIXTURE"
    case_results: list[EvaluationCaseResult] = field(default_factory=list)
    score_summary: dict = field(default_factory=dict)
    threshold_summary: dict = field(default_factory=dict)
    regression_summary: dict | None = None
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class EvaluationScore:
    schema_version: str = "1.0"
    schema_id: str = "evaluation_score.schema.json"
    score_id: str = ""
    run_id: str = ""
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    blocked_cases: int = 0
    error_cases: int = 0
    skipped_cases: int = 0
    raw_score: float = 0.0
    normalized_score: float = 0.0
    weighted_score: float = 0.0
    pass_rate: float = 0.0
    failure_rate: float = 0.0
    blocked_rate: float = 0.0
    error_rate: float = 0.0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class EvaluationThreshold:
    schema_version: str = "1.0"
    schema_id: str = "evaluation_threshold.schema.json"
    threshold_id: str = ""
    minimum_pass_rate: float = 1.0
    minimum_weighted_score: float = 1.0
    maximum_regression_count: int = 0
    maximum_error_count: int = 0
    maximum_blocked_count: int = 0
    allow_blocked_cases: bool = False
    allow_error_cases: bool = False
    required_case_ids: list[str] = field(default_factory=list)
    allowed_score_delta: float = 0.05
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class RegressionComparison:
    schema_version: str = "1.0"
    schema_id: str = "evaluation_regression_comparison.schema.json"
    comparison_id: str = ""
    current_run_id: str = ""
    baseline_run_id: str | None = None
    timestamp: str = ""
    status: str = ""
    score_delta: float = 0.0
    weighted_score_delta: float = 0.0
    new_failures: list[str] = field(default_factory=list)
    fixed_failures: list[str] = field(default_factory=list)
    unchanged_failures: list[str] = field(default_factory=list)
    new_blocked_cases: list[str] = field(default_factory=list)
    new_error_cases: list[str] = field(default_factory=list)
    regression_count: int = 0
    improvement_count: int = 0
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class EvaluationReport:
    schema_version: str = "1.0"
    schema_id: str = "evaluation_report.schema.json"
    report_id: str = ""
    run_id: str = ""
    suite_id: str = ""
    timestamp: str = ""
    status: str = ""
    summary: str = ""
    score_summary: dict = field(default_factory=dict)
    threshold_summary: dict = field(default_factory=dict)
    regression_summary: dict | None = None
    case_summaries: list[dict] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class EvaluationBaseline:
    schema_version: str = "1.0"
    schema_id: str = "evaluation_baseline.schema.json"
    baseline_id: str = ""
    suite_id: str = ""
    baseline_run_id: str = ""
    baseline_commit: str | None = None
    created_at: str = ""
    source_component: str = ""
    score_summary: dict = field(default_factory=dict)
    case_result_index: dict = field(default_factory=dict)
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    sha256: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
