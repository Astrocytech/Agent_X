import pytest
from agentx_initiator.core.patch_proposal_model import PatchSpec, PatchAction, PatchContext, PatchValidation, PatchManifest, PatchAudit


def test_patch_action_defaults():
    a = PatchAction()
    assert a.action_type == "NOOP"
    assert a.priority == "P2"


def test_patch_action_to_dict():
    a = PatchAction(action_id="a1", action_type="CREATE", target_path="L1/tests/", content_ref="", description="add tests", priority="P1")
    d = a.to_dict()
    assert d["action_type"] == "CREATE"
    assert d["priority"] == "P1"


def test_patch_spec_defaults():
    s = PatchSpec()
    assert s.spec_id == ""


def test_patch_context_defaults():
    c = PatchContext()
    assert c.action_refs == []


def test_patch_validation_defaults():
    v = PatchValidation()
    assert v.status == "PENDING"


def test_patch_manifest_to_dict():
    m = PatchManifest(manifest_id="m1", proposal_id="p1", action_count=2, applied_count=0, total_dependencies=0, created_at="now", updated_at="now")
    d = m.to_dict()
    assert d["action_count"] == 2


def test_patch_audit_defaults():
    a = PatchAudit()
    assert a.source_component == "PatchProposalGenerator"
