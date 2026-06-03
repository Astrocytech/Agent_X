from agentx_evolve.worker.worker_models import ContextProvenance, ProvenanceCheck, PC_PASS, PC_FAIL


def test_provenance_check_defaults():
    pc = ProvenanceCheck()
    assert pc.status == PC_PASS
    assert pc.details == ""


def test_provenance_check_fail():
    pc = ProvenanceCheck(status=PC_FAIL, details="checksum mismatch")
    assert pc.status == PC_FAIL
    assert pc.details == "checksum mismatch"


def test_context_provenance_defaults():
    cp = ContextProvenance()
    assert cp.source == ""
    assert cp.verified is True
    assert cp.check is None


def test_context_provenance_with_check():
    pc = ProvenanceCheck(status=PC_PASS, details="verified")
    cp = ContextProvenance(provenance_id="p-1", source="worker-1", checksum="abc123", check=pc)
    assert cp.provenance_id == "p-1"
    assert cp.source == "worker-1"
    assert cp.checksum == "abc123"
    assert cp.check is not None
    assert cp.check.details == "verified"


def test_pc_constants():
    assert PC_PASS == "PASS"
    assert PC_FAIL == "FAIL"
