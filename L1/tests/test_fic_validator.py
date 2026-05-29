from __future__ import annotations

import pathlib

import pytest

from L1.controller.fic_generator import FicTemplate
from L1.controller.fic_validator import (
    FicValidationResult,
    FicValidator,
    FicValidatorError,
    validate_fics,
)


def _valid_template(**kwargs) -> FicTemplate:
    fields = dict(
        fic_id="FIC-L1-PLAN-001",
        unit_id="UNIT-L1-PLAN-001",
        target_file="L1/controller/unit_001.py",
        description="Add login feature",
        status="draft",
        version="v0.1.0",
    )
    fields.update(kwargs)
    return FicTemplate(**fields)


def test_validates_valid_templates() -> None:
    t = _valid_template()
    result = validate_fics((t,))
    assert result.is_valid is True
    assert result.errors == ()


def test_rejects_empty_tuple() -> None:
    result = validate_fics(())
    assert result.is_valid is False
    assert "no templates" in result.errors[0]


def test_rejects_none() -> None:
    result = FicValidator().validate(None)  # type: ignore[arg-type]
    assert result.is_valid is False
    assert "must be a tuple" in result.errors[0]


def test_rejects_wrong_element_type() -> None:
    result = validate_fics(("not a template",))  # type: ignore[arg-type]
    assert result.is_valid is False
    assert "must be a FicTemplate" in result.errors[0]


def test_rejects_invalid_fic_id_pattern() -> None:
    t = _valid_template(fic_id="BAD-ID")
    result = validate_fics((t,))
    assert result.is_valid is False
    assert "invalid fic_id" in result.errors[0]


def test_rejects_invalid_unit_id_pattern() -> None:
    t = _valid_template(unit_id="BAD-UNIT")
    result = validate_fics((t,))
    assert result.is_valid is False
    assert "invalid unit_id" in result.errors[0]


def test_rejects_empty_description() -> None:
    t = _valid_template(description="")
    result = validate_fics((t,))
    assert result.is_valid is False
    assert "description must not be empty" in result.errors[0]


def test_rejects_empty_target_file() -> None:
    t = _valid_template(target_file="")
    result = validate_fics((t,))
    assert result.is_valid is False
    assert "target_file must not be empty" in result.errors[0]


def test_rejects_absolute_target_file() -> None:
    t = _valid_template(target_file="/etc/passwd")
    result = validate_fics((t,))
    assert result.is_valid is False
    assert "must not be absolute" in result.errors[0]


def test_rejects_wrong_status() -> None:
    t = _valid_template(status="ready-for-code")
    result = validate_fics((t,))
    assert result.is_valid is False
    assert "status must be 'draft'" in result.errors[0]


def test_rejects_wrong_version() -> None:
    t = _valid_template(version="v0.2.0")
    result = validate_fics((t,))
    assert result.is_valid is False
    assert "version must be 'v0.1.0'" in result.errors[0]


def test_rejects_duplicate_fic_ids() -> None:
    t1 = _valid_template()
    t2 = _valid_template(unit_id="UNIT-L1-PLAN-002", description="other")
    result = validate_fics((t1, t2))
    assert result.is_valid is False
    assert "duplicate fic_id" in result.errors[0]


def test_rejects_duplicate_unit_ids() -> None:
    t1 = _valid_template()
    t2 = _valid_template(fic_id="FIC-L1-PLAN-002", description="other")
    result = validate_fics((t1, t2))
    assert result.is_valid is False
    assert "duplicate unit_id" in result.errors[0]


def test_validator_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/fic_validator.py").read_text(encoding="utf-8")
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
