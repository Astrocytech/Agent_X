import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ_DIR = os.path.join(BASE, "requirements")


def _load_requirements():
    with open(os.path.join(REQ_DIR, "requirements.json")) as f:
        return json.load(f)


def _load_schema():
    with open(os.path.join(REQ_DIR, "requirements.schema.json")) as f:
        return json.load(f)


def _load_matrix():
    with open(os.path.join(REQ_DIR, "traceability_matrix.json")) as f:
        return json.load(f)


def _manual_validate(req, schema):
    required = set(schema.get("required", []))
    for r in req:
        for field in required:
            if field not in r:
                return False, f"{r.get('requirement_id', '?')} missing {field}"
        if r.get("accepted_for_agentx") is True:
            if not r.get("positive_tests"):
                return False, f"{r['requirement_id']} accepted but no positive_tests"
        if not r.get("source_ids"):
            return False, f"{r['requirement_id']} has no source_ids"
    return True, "ok"


def test_requirements_have_required_fields():
    req = _load_requirements()
    required = {"requirement_id", "source_ids", "statement", "accepted_for_agentx", "scope", "artifact_refs", "status"}
    for r in req:
        missing = required - set(r.keys())
        assert not missing, f"{r.get('requirement_id')} missing {missing}"


def test_requirement_id_format():
    req = _load_requirements()
    pattern = re.compile(r"^BENCHCORE-REQ-\d{4}$")
    for r in req:
        assert pattern.match(r["requirement_id"]), f"bad id: {r['requirement_id']}"


def test_accepted_reqs_have_tests():
    req = _load_requirements()
    for r in req:
        if r.get("accepted_for_agentx") is True:
            assert r.get("positive_tests"), f"{r['requirement_id']} accepted but no positive_tests"


def test_no_accepted_req_without_source():
    req = _load_requirements()
    for r in req:
        if r.get("accepted_for_agentx") is True:
            assert r.get("source_ids"), f"{r['requirement_id']} accepted but no source_ids"


def test_schema_validates():
    req = _load_requirements()
    schema = _load_schema()
    valid, msg = _manual_validate(req, schema)
    assert valid, msg


def test_traceability_matrix_matches_requirements():
    req = _load_requirements()
    matrix = _load_matrix()
    req_ids = {r["requirement_id"] for r in req}
    mat_ids = {m["requirement_id"] for m in matrix}
    extra = mat_ids - req_ids
    missing = req_ids - mat_ids
    assert not extra, f"matrix has unknown ids: {extra}"
    assert not missing, f"matrix missing ids: {missing}"


def test_accepted_req_without_test_fails_schema():
    req = _load_requirements()
    schema = _load_schema()
    mutated = []
    for r in req:
        entry = dict(r)
        if entry.get("accepted_for_agentx") is True:
            entry["positive_tests"] = []
        mutated.append(entry)
    valid, msg = _manual_validate(mutated, schema)
    assert not valid, "accepted req without tests should fail"


def test_sabotage_requirement_without_source():
    """Sabotage: no accepted requirement should lack a source_id"""
    req = _load_requirements()
    for r in req:
        if r.get("accepted_for_agentx", False):
            assert len(r.get("source_ids", [])) > 0, f"{r['requirement_id']} has no source"


def test_sabotage_requirement_without_test():
    """Sabotage: no accepted requirement should lack positive_tests"""
    req = _load_requirements()
    for r in req:
        if r.get("accepted_for_agentx", False):
            assert len(r.get("positive_tests", [])) > 0, f"{r['requirement_id']} has no test"
