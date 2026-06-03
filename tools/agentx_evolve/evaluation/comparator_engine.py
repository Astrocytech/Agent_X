from __future__ import annotations
import re

from agentx_evolve.evaluation.evaluation_models import (
    EvaluationExpectedResult,
    EXACT_MATCH, CONTAINS, REGEX_MATCH, STATUS_MATCH, FAILURE_CLASS_MATCH,
    ARTIFACT_EXISTS, NUMERIC_EQUALS, NUMERIC_AT_LEAST, NUMERIC_AT_MOST,
    LIST_CONTAINS, DICT_HAS_KEY, CUSTOM_STATIC_CHECK,
    IS_SCHEMA_VALID_TOOL_RESULT, IS_SCHEMA_VALID_EVALUATION_RESULT,
    HAS_EVIDENCE_REFS, HAS_ARTIFACT_REFS, IS_REDACTED,
)


def resolve_json_path(payload: dict, path: str) -> object:
    parts = path.split(".")
    current = payload
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, (list, tuple)) and part.isdigit():
            idx = int(part)
            if 0 <= idx < len(current):
                current = current[idx]
            else:
                return None
        else:
            return None
    return current


def run_comparator(comparator: dict, observed: dict) -> dict:
    ctype = comparator.get("type", "")
    path = comparator.get("path", "")
    expected = comparator.get("expected")
    tolerance = comparator.get("tolerance")
    actual = resolve_json_path(observed, path) if path else observed
    passed = False
    message = ""

    if ctype == EXACT_MATCH:
        passed = actual == expected
        message = f"EXACT_MATCH: {'pass' if passed else f'expected {expected!r}, got {actual!r}'}"
    elif ctype == CONTAINS:
        passed = isinstance(actual, (str, list)) and expected in actual
        message = f"CONTAINS: {'pass' if passed else f'expected to contain {expected!r}'}"
    elif ctype == REGEX_MATCH:
        if isinstance(actual, str) and isinstance(expected, str):
            try:
                passed = bool(re.search(expected, actual))
            except re.error:
                passed = False
            message = f"REGEX_MATCH: {'pass' if passed else f'no match for {expected!r}'}"
        else:
            message = f"REGEX_MATCH: invalid types actual={type(actual).__name__} expected={type(expected).__name__}"
    elif ctype == STATUS_MATCH:
        passed = str(actual) == str(expected)
        message = f"STATUS_MATCH: {'pass' if passed else f'expected {expected}, got {actual}'}"
    elif ctype == FAILURE_CLASS_MATCH:
        passed = str(actual) == str(expected)
        message = f"FAILURE_CLASS_MATCH: {'pass' if passed else f'expected {expected}, got {actual}'}"
    elif ctype == ARTIFACT_EXISTS:
        passed = actual is not None
        message = f"ARTIFACT_EXISTS: {'pass' if passed else 'artifact not found'}"
    elif ctype == NUMERIC_EQUALS:
        try:
            passed = float(actual) == float(expected)
        except (TypeError, ValueError):
            passed = False
        message = f"NUMERIC_EQUALS: {'pass' if passed else f'expected {expected}, got {actual}'}"
    elif ctype == NUMERIC_AT_LEAST:
        try:
            passed = float(actual) >= float(expected)
        except (TypeError, ValueError):
            passed = False
        message = f"NUMERIC_AT_LEAST: {'pass' if passed else f'expected >= {expected}, got {actual}'}"
    elif ctype == NUMERIC_AT_MOST:
        try:
            passed = float(actual) <= float(expected)
        except (TypeError, ValueError):
            passed = False
        message = f"NUMERIC_AT_MOST: {'pass' if passed else f'expected <= {expected}, got {actual}'}"
    elif ctype == LIST_CONTAINS:
        passed = isinstance(actual, list) and expected in actual
        message = f"LIST_CONTAINS: {'pass' if passed else f'expected list to contain {expected!r}'}"
    elif ctype == DICT_HAS_KEY:
        passed = isinstance(actual, dict) and expected in actual
        message = f"DICT_HAS_KEY: {'pass' if passed else f'expected dict with key {expected!r}'}"
    elif ctype == CUSTOM_STATIC_CHECK:
        passed, message = _run_static_check(expected, observed)
    else:
        message = f"Unknown comparator type: {ctype}"

    return {
        "comparator_type": ctype,
        "path": path,
        "expected": expected,
        "actual": actual,
        "passed": passed,
        "message": message,
    }


def _run_static_check(check_name: str, payload: dict) -> tuple[bool, str]:
    if check_name == IS_SCHEMA_VALID_TOOL_RESULT:
        has_refs = payload.get("evidence_refs") is not None
        return (has_refs, f"IS_SCHEMA_VALID_TOOL_RESULT: {'pass' if has_refs else 'no evidence_refs'}")
    elif check_name == IS_SCHEMA_VALID_EVALUATION_RESULT:
        has_status = payload.get("status") is not None
        return (has_status, f"IS_SCHEMA_VALID_EVALUATION_RESULT: {'pass' if has_status else 'no status'}")
    elif check_name == HAS_EVIDENCE_REFS:
        refs = payload.get("evidence_refs", [])
        return (bool(refs), f"HAS_EVIDENCE_REFS: {'pass' if refs else 'no evidence refs'}")
    elif check_name == HAS_ARTIFACT_REFS:
        refs = payload.get("artifact_refs", [])
        return (bool(refs), f"HAS_ARTIFACT_REFS: {'pass' if refs else 'no artifact refs'}")
    elif check_name == IS_REDACTED:
        text = str(payload)
        has_sensitive = any(kw in text.lower() for kw in ["secret", "password", "token", "api_key"])
        return (not has_sensitive, f"IS_REDACTED: {'pass' if not has_sensitive else 'sensitive content detected'}")
    return (False, f"Unknown static check: {check_name}")


def compare_observed_to_expected(observed: dict, expected: EvaluationExpectedResult) -> list[dict]:
    details = []
    for comp in expected.comparators:
        details.append(run_comparator(comp, observed))
    if not details:
        details.append(run_comparator({"type": EXACT_MATCH, "path": "", "expected": expected.expected_status}, observed))
    return details
