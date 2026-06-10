import json, os, sys, tempfile
from pathlib import Path
from agentx_evolve.docs_sync.coverage_matrix import CoverageMatrix


REPO_ROOT = Path("/home/glompy/Desktop/ASTROCYTECH/Agent_X")


class TestDocumentCoverageMatrix:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_coverage_matrix_can_be_created_as_json(self):
        matrix = CoverageMatrix()
        matrix.add_entry("L0", True)
        matrix.add_entry("L1", True)
        matrix.add_entry("L2", False)
        s = matrix.summary()
        assert s["total_layers"] == 3
        assert s["covered"] == 2
        assert s["uncovered"] == 1
        assert s["coverage_pct"] == 66.66666666666666

    def test_coverage_matrix_can_be_serialized_to_json(self):
        matrix = CoverageMatrix()
        matrix.add_entry("L0", True)
        json_str = json.dumps({"entries": matrix.entries, "summary": matrix.summary()})
        parsed = json.loads(json_str)
        assert parsed["entries"][0]["layer"] == "L0"
        assert parsed["entries"][0]["covered"] is True
        assert parsed["summary"]["coverage_pct"] == 100.0

    def test_coverage_matrix_json_is_valid_and_parseable(self):
        matrix = CoverageMatrix()
        matrix.add_entry("kernel", True)
        matrix.add_entry("security", True)
        matrix.add_entry("orchestrator", False)
        raw = json.dumps(matrix.summary())
        data = json.loads(raw)
        assert "total_layers" in data
        assert isinstance(data["total_layers"], int)
        assert isinstance(data["coverage_pct"], float)
