import pytest
from agentx_evolve.orchestrator.orchestrator_audit import create_evidence_manifest, write_evidence_manifest


class TestMonitoringEvidenceManifest:
    def test_create_evidence_manifest(self):
        manifest = create_evidence_manifest(run_id="test-run", session_id="test-session")
        assert manifest is not None

    def test_write_evidence_manifest(self, tmp_path):
        manifest = create_evidence_manifest(run_id="test-run", session_id="test-session")
        write_evidence_manifest(manifest, tmp_path)
