import pytest
from agentx_initiator.core.patch_proposal_rules import build_default_actions, compute_proposal_status


def test_build_default_actions_read():
    actions = build_default_actions("read the scan output")
    types = [a.get("action_type") for a in actions]
    assert "NOOP" in types


def test_build_default_actions_schema():
    actions = build_default_actions("validate schema for L1")
    types = [a.get("action_type") for a in actions]
    assert "CREATE" in types


def test_build_default_actions_test():
    actions = build_default_actions("add test for governance")
    types = [a.get("action_type") for a in actions]
    assert "CREATE" in types


def test_build_default_actions_fic():
    actions = build_default_actions("create fic contract")
    types = [a.get("action_type") for a in actions]
    assert "CREATE" in types


def test_build_default_actions_default():
    actions = build_default_actions("do something general")
    types = [a.get("action_type") for a in actions]
    assert "REFACTOR" in types


def test_compute_proposal_status_empty():
    assert compute_proposal_status([]) == "DRAFT"


def test_compute_proposal_status_with_actions():
    assert compute_proposal_status([{"action_id": "a1"}]) == "REVIEW"
