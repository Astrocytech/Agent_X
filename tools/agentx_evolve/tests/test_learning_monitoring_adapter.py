from agentx_evolve.learning.monitoring_adapter import load_monitoring_observations, detect_runtime_degradation


def test_load_monitoring_observations_available():
    context = {
        "monitoring_observations": {"degradation_detected": False, "details": "all good"},
        "monitoring_evidence_refs": ["mref1"],
    }
    result = load_monitoring_observations(context)
    assert result["adapter_name"] == "monitoring_adapter"
    assert result["dependency_status"] == "AVAILABLE"
    assert result["status"] == "AVAILABLE"
    assert result["data"] == context["monitoring_observations"]
    assert result["evidence_refs"] == ["mref1"]


def test_load_monitoring_observations_missing():
    result = load_monitoring_observations({})
    assert result["adapter_name"] == "monitoring_adapter"
    assert result["dependency_status"] == "MISSING"
    assert result["status"] == "MISSING"
    assert result["warnings"] == ["Monitoring/Observability not available"]


def test_load_monitoring_observations_none_data():
    result = load_monitoring_observations({"monitoring_observations": None})
    assert result["dependency_status"] == "MISSING"


def test_detect_runtime_degradation_true():
    obs = {"degradation_detected": True, "details": "high latency", "affected_components": ["api"]}
    result = detect_runtime_degradation(obs)
    assert result["degradation_detected"] is True
    assert result["affected_components"] == ["api"]


def test_detect_runtime_degradation_false():
    result = detect_runtime_degradation({"degradation_detected": False})
    assert result["degradation_detected"] is False


def test_detect_runtime_degradation_empty():
    result = detect_runtime_degradation({})
    assert result["degradation_detected"] is False
    assert result["details"] == "no observations"
