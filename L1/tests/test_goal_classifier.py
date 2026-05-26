from __future__ import annotations

import dataclasses
import pathlib

import pytest

from L1.controller.goal_classifier import (
    GoalClassifier,
    GoalClassifierError,
    GoalPriority,
    GoalRecord,
    GoalScope,
    GoalType,
    classify_goal_file,
    classify_goal_text,
)


def test_classifies_feature_goal() -> None:
    result = classify_goal_text("Implement a new search feature for the registry")
    assert result.goal_type == GoalType.FEATURE


def test_classifies_bug_fix_goal() -> None:
    result = classify_goal_text("Fix the crash when loading empty manifest")
    assert result.goal_type == GoalType.BUG_FIX


def test_classifies_refactor_goal() -> None:
    result = classify_goal_text("Refactor the validator module to simplify logic")
    assert result.goal_type == GoalType.REFACTOR


def test_classifies_research_goal() -> None:
    result = classify_goal_text("Research alternative approaches for digest verification")
    assert result.goal_type == GoalType.RESEARCH


def test_classifies_documentation_goal() -> None:
    result = classify_goal_text("Add documentation for the FIC workflow steps")
    assert result.goal_type == GoalType.DOCUMENTATION


def test_classifies_infrastructure_goal() -> None:
    result = classify_goal_text("Set up CI pipeline for automated testing")
    assert result.goal_type == GoalType.INFRASTRUCTURE


def test_classifies_critical_priority() -> None:
    result = classify_goal_text("CRITICAL: fix the production outage immediately")
    assert result.priority == GoalPriority.CRITICAL


def test_classifies_high_priority() -> None:
    result = classify_goal_text("High priority: implement the payment module")
    assert result.priority == GoalPriority.HIGH


def test_classifies_low_priority() -> None:
    result = classify_goal_text("Low priority: nice to have feature")
    assert result.priority == GoalPriority.LOW


def test_classifies_system_scope() -> None:
    result = classify_goal_text("System-wide change to authentication")
    assert result.scope == GoalScope.SYSTEM


def test_classifies_cross_component_scope() -> None:
    result = classify_goal_text("Cross-component refactor of logging")
    assert result.scope == GoalScope.CROSS_COMPONENT


def test_defaults_on_empty_text() -> None:
    result = classify_goal_text("")
    assert result.goal_type == GoalType.FEATURE
    assert result.priority == GoalPriority.MEDIUM
    assert result.scope == GoalScope.COMPONENT
    assert result.summary == ""
    assert result.constraints == ()


def test_defaults_on_no_keywords() -> None:
    result = classify_goal_text("Do something with the thing")
    assert result.goal_type == GoalType.FEATURE
    assert result.priority == GoalPriority.MEDIUM
    assert result.scope == GoalScope.COMPONENT


def test_extracts_summary_from_first_line() -> None:
    result = classify_goal_text("Add user authentication\n\nThis adds login support.")
    assert "Add user authentication" in result.summary


def test_extracts_constraints() -> None:
    result = classify_goal_text(
        "Implement caching. Must not exceed 100MB. Must support TTL."
    )
    assert len(result.constraints) >= 1
    assert any("must not exceed" in c.lower() for c in result.constraints)


def test_classify_file_reads_and_classifies(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "goal.txt"
    doc.write_text("Fix the login bug", encoding="utf-8")
    result = classify_goal_file("goal.txt", root=tmp_path)
    assert result.goal_type == GoalType.BUG_FIX


def test_classify_file_rejects_missing_file(tmp_path: pathlib.Path) -> None:
    with pytest.raises(GoalClassifierError, match="not found"):
        classify_goal_file("nonexistent.txt", root=tmp_path)


def test_goal_record_is_frozen() -> None:
    r = classify_goal_text("test")
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.goal_type = GoalType.BUG_FIX  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.summary = "changed"  # type: ignore[misc]


def test_case_insensitive_keywords() -> None:
    result = classify_goal_text("REFACTOR THE DATABASE SCHEMA")
    assert result.goal_type == GoalType.REFACTOR


def test_goal_classifier_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/goal_classifier.py").read_text(
        encoding="utf-8"
    )
    forbidden = [
        "import os",
        "from os",
        "import subprocess",
        "from subprocess",
        "import requests",
        "import urllib",
        "import socket",
        "import http",
    ]
    for imp in forbidden:
        assert imp not in source, f"forbidden import found: {imp}"


def test_classifier_never_raises_on_unknown_content() -> None:
    result = classify_goal_text("xyzzx")
    assert isinstance(result, GoalRecord)


def test_only_whitespace_defaults() -> None:
    result = classify_goal_text("   \n\n  \t  ")
    assert result.goal_type == GoalType.FEATURE
    assert result.priority == GoalPriority.MEDIUM
    assert result.scope == GoalScope.COMPONENT
    assert result.summary == ""


def test_first_type_keyword_wins() -> None:
    result = classify_goal_text("Fix the bug and add documentation")
    assert result.goal_type == GoalType.BUG_FIX


def test_classifier_rejects_non_string() -> None:
    with pytest.raises(GoalClassifierError, match="must be a string"):
        classify_goal_text(123)  # type: ignore[arg-type]


def test_classify_file_rejects_absolute_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(GoalClassifierError, match="must be relative"):
        classify_goal_file("/absolute/path.txt", root=tmp_path)


def test_summary_strips_markdown_headers() -> None:
    result = classify_goal_text("## Feature: Add dark mode")
    assert result.summary != ""
