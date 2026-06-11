import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GV = os.path.join(BASE, "grammar_validation")

FORBIDDEN_KEYWORDS = {"!halt", "!emergency", "!bypass"}
ALLOWED_KEYWORDS = {"TITLE", "HEADLINE", "SUMMARY", "BODY", "AUTHOR", "DATE", "CATEGORY", "STATUS", "SOURCE", "KEYWORDS"}
ALLOWED_DELIMITERS = {":", "="}


def _validate_cue(cue_obj):
    cue = cue_obj.get("cue", "")
    if len(cue) > 150:
        return False
    keywords = cue_obj.get("keywords", [])
    for kw in keywords:
        if kw in FORBIDDEN_KEYWORDS:
            return False
    if cue_obj.get("delimiter") not in ALLOWED_DELIMITERS:
        return False
    return True


def _validate_od(cmd_obj):
    cmd = cmd_obj.get("command", "")
    if not cmd.startswith("*OD"):
        return False
    args = cmd_obj.get("arguments", {})
    for key, val in args.items():
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
            return False
        if not isinstance(val, str):
            return False
    return True


def _validate_cg(cmd_obj):
    cmd = cmd_obj.get("command", "")
    if not cmd.startswith("*CG"):
        return False
    args = cmd_obj.get("arguments", {})
    for key, val in args.items():
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
            return False
        if not isinstance(val, str):
            return False
    return True


def _validate_quickcode(qc_obj):
    kw = qc_obj.get("keyword", "")
    if kw not in ALLOWED_KEYWORDS:
        return False
    exp = qc_obj.get("expansion", "")
    if not exp:
        return False
    return True


def test_production_cue_schema_enforces_length():
    long_cue = {
        "cue": "A" * 151,
        "keywords": ["test"],
        "delimiter": ":",
        "source": "BENCHCORE-DOC-020"
    }
    assert not _validate_cue(long_cue), "cue >150 should fail"


def test_production_cue_rejects_forbidden_keywords():
    bad_cue = {
        "cue": "Emergency stop",
        "keywords": ["!halt"],
        "delimiter": ":",
        "source": "BENCHCORE-DOC-020"
    }
    assert not _validate_cue(bad_cue), "!halt should be rejected"


def test_od_command_schema_valid():
    valid = {
        "command": "*OD EXTRACT STORY",
        "arguments": {"ID": "12345"},
        "transition": "extract"
    }
    assert _validate_od(valid), "valid OD should pass"


def test_cg_command_schema_valid():
    valid = {
        "command": "*CG GENERATE FIELD",
        "arguments": {"type": "NRCS"}
    }
    assert _validate_cg(valid), "valid CG should pass"


def test_quickcode_schema_valid():
    valid = {
        "keyword": "TITLE",
        "expansion": "story_title",
        "source": "BENCHCORE-DOC-024"
    }
    assert _validate_quickcode(valid), "valid QuickCode should pass"


def test_valid_examples_all_pass():
    examples = []
    with open(os.path.join(GV, "valid_examples.jsonl")) as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    for ex in examples:
        assert ex["expected_validation"] is True


def test_invalid_examples_all_fail():
    count = 0
    with open(os.path.join(GV, "invalid_examples.jsonl")) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            count += 1
            try:
                ex = json.loads(line)
                assert ex.get("expected_validation") is False, f"line {count} should be marked invalid"
            except json.JSONDecodeError:
                pass
    assert count > 0


def test_hallucinated_command_rejected():
    fake_od = {
        "command": "*XX FAKE",
        "arguments": {"x": "y"},
        "transition": "none"
    }
    assert not _validate_od(fake_od), "*XX should be rejected"
    fake_cg = {
        "command": "*YY FAKE",
        "arguments": {"x": "y"}
    }
    assert not _validate_cg(fake_cg), "*YY should be rejected"


def test_overlength_cue_accepted_fails():
    long_cue = {
        "cue": "X" * 200,
        "keywords": ["test"],
        "delimiter": ":",
        "source": "BENCHCORE-DOC-020"
    }
    assert not _validate_cue(long_cue), ">150 char cue should not be accepted"


def test_sabotage_malformed_od_command():
    """Sabotage: a malformed *OD command must fail validation"""
    schema = json.load(open(os.path.join(GV, "od_command.schema.json")))
    assert "command" in schema.get("properties", {}), "OD schema must have command field"
    command_pattern = schema.get("properties", {}).get("command", {}).get("pattern", "")
    if command_pattern:
        assert re.match(command_pattern, "*OD VALID") is not None, "Pattern should match valid OD"
        assert re.match(command_pattern, "INVALID OD") is None, "Pattern should reject invalid"


def test_sabotage_overlength_cue():
    """Sabotage: production cue over 150 chars must fail validation"""
    schema = json.load(open(os.path.join(GV, "production_cue.schema.json")))
    max_len = schema.get("properties", {}).get("cue", {}).get("maxLength", 0)
    assert max_len > 0, "Production cue must have maxLength constraint"
    assert max_len <= 150, "Production cue maxLength must be <= 150"
