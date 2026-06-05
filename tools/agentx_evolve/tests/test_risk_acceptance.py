import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.risk_acceptance import (
    validate_risk_acceptance, has_blocking_risks,
    has_unaccepted_required_risks, load_risk_acceptance,
    write_risk_acceptance, compute_risk_acceptance_hash,
)
from agentx_evolve.promotion.promotion_models import (
    RiskAcceptance, ReleaseCandidate,
)


class TestRiskAcceptanceAcceptsNonBlockingRisks:
    def test_risk_acceptance_accepts_non_blocking_risks(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        ra = RiskAcceptance(
            risk_acceptance_id="ra-001",
            risk_acceptance_hash="b" * 64,
            candidate_id="rc-001",
            component_id="comp-1",
            risks=[
                {"risk_id": "risk-1", "description": "low impact",
                 "severity": "LOW", "required": False,
                 "accepted": True, "blocking": False,
                 "status": "identified", "mitigation": "none"},
            ],
            accepted_risks=["risk-1"],
            blocking_risks=[],
        )
        assert has_blocking_risks(ra) is False
        assert has_unaccepted_required_risks(ra) is False
        errors = validate_risk_acceptance(ra, candidate)
        assert errors == []


class TestBlockingRiskBlocks:
    def test_blocking_risk_blocks(self):
        ra = RiskAcceptance(
            risk_acceptance_id="ra-002",
            risk_acceptance_hash="b" * 64,
            candidate_id="rc-001",
            component_id="comp-1",
            blocking_risks=["risk-critical"],
        )
        assert has_blocking_risks(ra) is True


class TestUnacceptedRequiredRiskBlocks:
    def test_unaccepted_required_risk_blocks(self):
        ra = RiskAcceptance(
            risk_acceptance_id="ra-003",
            candidate_id="rc-001",
            component_id="comp-1",
            risks=[
                {"risk_id": "risk-req", "description": "required risk",
                 "severity": "HIGH", "required": True,
                 "accepted": False, "blocking": True,
                 "status": "identified", "mitigation": "none"},
            ],
            accepted_risks=[],
            blocking_risks=[],
        )
        assert has_unaccepted_required_risks(ra) is True


class TestLoadAndWriteRiskAcceptance:
    def test_load_and_write_risk_acceptance(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            ra = RiskAcceptance(
                risk_acceptance_id="ra-wl-001",
                risk_acceptance_hash="b" * 64,
                candidate_id="rc-001",
                component_id="comp-1",
            )
            path = write_risk_acceptance(ra, repo_root)
            assert path.exists()
            loaded = load_risk_acceptance(path)
            assert loaded is not None
            assert loaded.risk_acceptance_id == ra.risk_acceptance_id
