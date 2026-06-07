import pytest
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    LocalModelInventory, LocalModelAvailabilityDecision,
    LocalRuntimeCompatibilityDecision, LocalModelSelectionConstraints,
    LocalRuntimeRequestLimits, LocalModelEligibilityDecision,
    RuntimeArtifactRecord, LocalRuntimeEvidenceManifest,
    LocalRuntimeReviewReport, LocalRuntimeCompletionRecord,
    RUNTIME_MODE_LOCAL_ONLY, RUNTIME_MODE_LOCAL_PREFERRED, RUNTIME_MODE_DISABLED,
    DEVICE_CPU, DEVICE_GPU, DEVICE_AUTO,
    AVAILABILITY_AVAILABLE, AVAILABILITY_MISSING, AVAILABILITY_BLOCKED,
    COMPATIBILITY_COMPATIBLE, COMPATIBILITY_INCOMPATIBLE, COMPATIBILITY_DEGRADED,
    ELIGIBILITY_ELIGIBLE, ELIGIBILITY_INELIGIBLE, ELIGIBILITY_BLOCKED, ELIGIBILITY_DEGRADED,
    QUANT_F32, QUANT_F16, QUANT_Q8, QUANT_Q6, QUANT_Q5, QUANT_Q4, QUANT_UNKNOWN,
    utc_now_iso, new_id, to_dict, stable_json_hash, normalize_decision_status,
    make_local_default_runtime, make_hosted_default_runtime,
    RuntimeProfile, HostedProviderProfile, RuntimeProfileAlias,
)


def test_constants_exist():
    assert RUNTIME_MODE_LOCAL_ONLY == "LOCAL_ONLY"
    assert RUNTIME_MODE_LOCAL_PREFERRED == "LOCAL_PREFERRED"
    assert RUNTIME_MODE_DISABLED == "DISABLED"
    assert DEVICE_CPU == "CPU"
    assert DEVICE_GPU == "GPU"
    assert DEVICE_AUTO == "AUTO"
    assert AVAILABILITY_AVAILABLE == "AVAILABLE"
    assert AVAILABILITY_MISSING == "MISSING"
    assert AVAILABILITY_BLOCKED == "BLOCKED"
    assert COMPATIBILITY_COMPATIBLE == "COMPATIBLE"
    assert COMPATIBILITY_INCOMPATIBLE == "INCOMPATIBLE"
    assert COMPATIBILITY_DEGRADED == "DEGRADED"
    assert QUANT_F32 == "F32"
    assert QUANT_Q4 == "Q4"
    assert QUANT_UNKNOWN == "UNKNOWN"


def test_utc_now_iso_returns_string():
    result = utc_now_iso()
    assert isinstance(result, str)
    assert "T" in result


def test_new_id_generates_unique():
    id1 = new_id("test")
    id2 = new_id("test")
    assert id1.startswith("test-")
    assert id1 != id2


def test_to_dict_with_dataclass():
    profile = LocalModelProfile(model_id="m1")
    d = to_dict(profile)
    assert d["model_id"] == "m1"
    assert d["schema_id"] == "local_model_profile.schema.json"


def test_stable_json_hash_is_deterministic():
    data = {"a": 1, "b": 2}
    h1 = stable_json_hash(data)
    h2 = stable_json_hash({"b": 2, "a": 1})
    assert h1 == h2
    assert isinstance(h1, str)


def test_normalize_decision_status():
    assert normalize_decision_status("block") == "BLOCK"
    assert normalize_decision_status("  allow  ") == "ALLOW"
    assert normalize_decision_status("unknown_value") == "UNKNOWN"
    assert normalize_decision_status("HOSTED_ALTERNATIVE_FORBIDDEN") == "HOSTED_ALTERNATIVE_FORBIDDEN"


def test_local_model_profile_defaults():
    p = LocalModelProfile()
    assert p.model_id == ""
    assert p.model_format == ""
    assert p.quantization == QUANT_UNKNOWN
    assert p.enabled is True
    assert p.priority == 100


def test_local_runtime_profile_post_init():
    r = LocalRuntimeProfile(runtime_id="rt1", max_context_tokens=4096)
    assert r.max_total_context_tokens == 4096


def test_local_hardware_profile_defaults():
    h = LocalHardwareProfile()
    assert h.probe_mode == "STATIC_ONLY"
    assert h.gpu_present is False
    assert h.conservative_ram_limit_bytes == 0


def test_local_model_inventory():
    inv = LocalModelInventory(inventory_id="inv1", models=[{"model_id": "m1"}])
    assert inv.inventory_id == "inv1"
    assert len(inv.models) == 1


def test_local_model_availability_decision():
    d = LocalModelAvailabilityDecision(
        decision_id="avail-1", model_id="m1", availability=AVAILABILITY_AVAILABLE
    )
    assert d.availability == AVAILABILITY_AVAILABLE
    assert d.path_allowed is False


def test_local_runtime_compatibility_decision():
    d = LocalRuntimeCompatibilityDecision(
        decision_id="compat-1", model_id="m1", runtime_id="rt1",
        compatibility=COMPATIBILITY_COMPATIBLE,
    )
    assert d.compatibility == COMPATIBILITY_COMPATIBLE
    assert d.degradation_applied is False


def test_local_model_selection_constraints():
    c = LocalModelSelectionConstraints(local_only=True, max_model_size_bytes=1_000_000)
    assert c.local_only is True
    assert c.network_allowed is False


def test_local_runtime_request_limits():
    l = LocalRuntimeRequestLimits(max_total_context_tokens=4096)
    assert l.max_prompt_tokens == 4096
    assert l.max_response_tokens == 2048


def test_local_model_eligibility_decision():
    d = LocalModelEligibilityDecision(
        decision_id="elig-1", eligibility=ELIGIBILITY_ELIGIBLE
    )
    assert d.eligibility == ELIGIBILITY_ELIGIBLE


def test_runtime_artifact_record():
    r = RuntimeArtifactRecord(artifact_path="/tmp/art.json", artifact_type="snapshot")
    assert r.artifact_path == "/tmp/art.json"
    assert r.sha256 == ""


def test_local_runtime_evidence_manifest():
    m = LocalRuntimeEvidenceManifest()
    assert m.component_id == "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE"


def test_local_runtime_review_report():
    r = LocalRuntimeReviewReport()
    assert r.review_document_id == "LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_REVIEW_AND_DOD"
    assert r.implementation_rating == 10.0


def test_local_runtime_completion_record():
    c = LocalRuntimeCompletionRecord()
    assert c.status == "VALIDATED"
    assert c.final_decision == ""


def test_make_local_default_runtime():
    r = make_local_default_runtime()
    assert r.runtime_id == "local_default"
    assert "gguf" in r.supported_model_formats
    assert r.enabled is True


def test_make_hosted_default_runtime():
    r = make_hosted_default_runtime()
    assert r.runtime_id == "hosted_default"
    assert r.uses_network is True


def test_runtime_profile_class():
    rp = RuntimeProfile(profile_id="rp1", max_total_context_tokens=16384, max_loaded_models=2)
    assert rp.profile_id == "rp1"
    assert rp.max_total_context_tokens == 16384
    assert rp.max_loaded_models == 2


def test_hosted_provider_profile():
    hp = HostedProviderProfile(profile_id="hp1", local_only=True)
    assert hp.profile_id == "hp1"
    assert hp.local_only is True
    assert hp.max_total_context_tokens == 65536


def test_runtime_profile_alias():
    assert RuntimeProfileAlias is LocalRuntimeProfile
