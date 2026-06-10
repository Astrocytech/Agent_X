import json, os, sys, tempfile
import pytest
from pathlib import Path
from agentx_evolve.security.security_models import (
    SandboxDecision, DECISION_ALLOW, DECISION_BLOCK,
    new_id, utc_now_iso, to_dict,
)
import jsonschema


SCHEMAS_DIR = Path("/home/glompy/Desktop/ASTROCYTECH/Agent_X/tools/agentx_evolve/schemas")


class TestEvidenceSchemaValidation:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_evidence_artifact_can_be_created_and_validated(self):
        evidence = SandboxDecision(
            decision_id=new_id("dec"),
            timestamp=utc_now_iso(),
            operation="READ",
            target="src/main.py",
            decision=DECISION_ALLOW,
        )
        d = to_dict(evidence)
        assert d["decision_id"].startswith("dec-")
        assert d["decision"] == DECISION_ALLOW
        assert d["target"] == "src/main.py"

    def test_invalid_evidence_is_rejected_by_schema_validation(self):
        schema_file = SCHEMAS_DIR / "sandbox_decision.schema.json"
        assert schema_file.exists()
        schema = json.loads(schema_file.read_text())

        valid = SandboxDecision(
            decision_id=new_id("dec"), timestamp=utc_now_iso(),
            operation="READ", target="test.py", decision=DECISION_ALLOW,
        )
        jsonschema.validate(instance=to_dict(valid), schema=schema)

        invalid = {"decision_id": 123, "timestamp": None, "operation": None}
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid, schema=schema)

    def test_evidence_schema_file_exists(self):
        schema_file = SCHEMAS_DIR / "evidence_manifest.schema.json"
        assert schema_file.exists()
        data = json.loads(schema_file.read_text())
        assert data["schema_id"] == "evidence_manifest.schema.json"
        assert "required" in data
