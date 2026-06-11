import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DQ = os.path.join(BASE, "data_quality")


def test_log_parse_policy_defined():
    with open(os.path.join(DQ, "log_parse_policy.json")) as f:
        policy = json.load(f)
    assert "parse_rules" in policy
    assert len(policy["parse_rules"]) > 0


def test_xml_cleanup_policy_defined():
    with open(os.path.join(DQ, "xml_cleanup_policy.json")) as f:
        policy = json.load(f)
    assert "cleanup_steps" in policy
    assert len(policy["cleanup_steps"]) > 0


def test_input_output_pairing_contract_exists():
    path = os.path.join(DQ, "input_output_pairing_contract.md")
    assert os.path.exists(path)
    with open(path) as f:
        content = f.read()
    assert "Pairing Rules" in content


def test_field_quality_classification():
    with open(os.path.join(DQ, "field_quality_policy.json")) as f:
        policy = json.load(f)
    assert "finite_fields" in policy
    assert "noisy_fields" in policy
    assert len(policy["finite_fields"]) > 0


def test_evidence_fusion_requires_join_key():
    with open(os.path.join(DQ, "evidence_fusion_policy.json")) as f:
        policy = json.load(f)
    assert policy.get("join_key_required") is True


def test_sql_mapping_policy_exists():
    path = os.path.join(DQ, "sql_mapping_policy.json")
    assert os.path.exists(path)
    with open(path) as f:
        policy = json.load(f)
    assert "mapping_rules" in policy


def test_fusion_without_join_key_fails():
    with open(os.path.join(DQ, "evidence_fusion_policy.json")) as f:
        policy = json.load(f)
    assert policy.get("join_key_required") is True, \
        "fusion without join key should fail"


def test_noisy_field_treated_as_finite_fails():
    with open(os.path.join(DQ, "field_quality_policy.json")) as f:
        policy = json.load(f)
    noisy = set(policy.get("noisy_fields", []))
    finite = set(policy.get("finite_fields", []))
    overlap = noisy & finite
    assert not overlap, f"fields in both noisy and finite: {overlap}"


def test_sabotage_noisy_field_as_finite():
    """Sabotage: Noisy/free-text fields must not be silently treated as finite targets"""
    with open(os.path.join(DQ, "field_quality_policy.json")) as f:
        policy = json.load(f)
    assert len(policy.get("noisy_fields", [])) > 0 or policy.get("rationale_required_for_noisy", False), \
        "Must identify noisy fields or require rationale"
    assert policy.get("rationale_required_for_noisy", False), \
        "Rationale must be required for noisy fields"


def test_sabotage_fusion_without_join_key():
    """Sabotage: evidence fusion without join key must be rejected"""
    with open(os.path.join(DQ, "evidence_fusion_policy.json")) as f:
        policy = json.load(f)
    assert policy.get("join_key_required", False), "Join key must be required for evidence fusion"
    assert len(policy.get("allowed_join_keys", [])) > 0, "Must define allowed join keys"
