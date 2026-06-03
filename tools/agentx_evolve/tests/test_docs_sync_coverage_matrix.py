import pytest
from agentx_evolve.docs_sync.coverage_matrix import CoverageMatrix


class TestCoverageMatrix:
    def test_default(self):
        m = CoverageMatrix()
        assert m.entries == []

    def test_add_entry(self):
        m = CoverageMatrix()
        m.add_entry("context", True)
        assert len(m.entries) == 1
        assert m.entries[0]["layer"] == "context"
        assert m.entries[0]["covered"] is True

    def test_summary_all_covered(self):
        m = CoverageMatrix()
        m.add_entry("context", True)
        m.add_entry("git", True)
        s = m.summary()
        assert s["total_layers"] == 2
        assert s["covered"] == 2
        assert s["uncovered"] == 0
        assert s["coverage_pct"] == 100.0

    def test_summary_partial(self):
        m = CoverageMatrix()
        m.add_entry("context", True)
        m.add_entry("git", False)
        s = m.summary()
        assert s["total_layers"] == 2
        assert s["covered"] == 1
        assert s["coverage_pct"] == 50.0

    def test_summary_empty(self):
        m = CoverageMatrix()
        s = m.summary()
        assert s["total_layers"] == 0
        assert s["coverage_pct"] == 100.0
