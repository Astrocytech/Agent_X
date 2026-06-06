from agentx_evolve.learning.docsync_adapter import load_docsync_evidence, detect_documentation_drift


def test_load_docsync_evidence_available():
    context = {
        "docsync_evidence": {"drift_detected": False, "details": "ok", "affected_paths": []},
        "docsync_evidence_refs": ["ref1"],
    }
    result = load_docsync_evidence(context)
    assert result["adapter_name"] == "docsync_adapter"
    assert result["dependency_status"] == "AVAILABLE"
    assert result["status"] == "AVAILABLE"
    assert result["data"] == context["docsync_evidence"]
    assert result["evidence_refs"] == ["ref1"]


def test_load_docsync_evidence_missing():
    result = load_docsync_evidence({})
    assert result["adapter_name"] == "docsync_adapter"
    assert result["dependency_status"] == "MISSING"
    assert result["status"] == "MISSING"
    assert result["warnings"] == ["Documentation Sync not available"]


def test_load_docsync_evidence_empty_data():
    result = load_docsync_evidence({"docsync_evidence": None})
    assert result["dependency_status"] == "MISSING"


def test_detect_documentation_drift_detected():
    evidence = {"drift_detected": True, "details": "file mismatch", "affected_paths": ["README.md"]}
    result = detect_documentation_drift(evidence)
    assert result["drift_detected"] is True
    assert result["affected_paths"] == ["README.md"]


def test_detect_documentation_drift_not_detected():
    evidence = {"drift_detected": False, "details": "", "affected_paths": []}
    result = detect_documentation_drift(evidence)
    assert result["drift_detected"] is False


def test_detect_documentation_drift_empty():
    result = detect_documentation_drift({})
    assert result["drift_detected"] is False
    assert result["details"] == "no evidence"
