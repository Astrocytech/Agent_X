import pytest
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    LocalModelInventory, LocalModelAvailabilityDecision,
    LocalRuntimeCompatibilityDecision, LocalModelSelectionConstraints,
    LocalRuntimeRequestLimits, LocalModelEligibilityDecision,
    RuntimeArtifactRecord, LocalRuntimeEvidenceManifest,
    LocalRuntimeReviewReport, LocalRuntimeCompletionRecord,
    RUNTIME_MODE_LOCAL_ONLY, DEVICE_CPU, AVAILABILITY_AVAILABLE,
    COMPATIBILITY_COMPATIBLE, ELIGIBILITY_ELIGIBLE,
    utc_now_iso, new_id, to_dict, stable_json_hash,
)


def test_all_dataclasses_instantiate():
    assert LocalModelProfile(model_id="m1").model_id == "m1"
    assert LocalRuntimeProfile(runtime_id="r1").runtime_id == "r1"
    assert LocalHardwareProfile(hardware_profile_id="hw1").hardware_profile_id == "hw1"
    assert LocalModelInventory(inventory_id="i1").inventory_id == "i1"
    assert LocalModelAvailabilityDecision(decision_id="d1").decision_id == "d1"
    assert LocalRuntimeCompatibilityDecision(decision_id="d2").decision_id == "d2"
    assert LocalModelSelectionConstraints().local_only is True
    assert LocalRuntimeRequestLimits().max_prompt_tokens == 4096
    assert LocalModelEligibilityDecision(decision_id="d3").eligibility == ""
    assert RuntimeArtifactRecord(artifact_path="/tmp/a").artifact_path == "/tmp/a"
    assert LocalRuntimeEvidenceManifest().component_id == "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE"
    assert LocalRuntimeReviewReport().component_id == "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE"
    assert LocalRuntimeCompletionRecord().component_id == "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE"


def test_constants_match():
    assert RUNTIME_MODE_LOCAL_ONLY == "LOCAL_ONLY"
    assert DEVICE_CPU == "CPU"
    assert AVAILABILITY_AVAILABLE == "AVAILABLE"
    assert COMPATIBILITY_COMPATIBLE == "COMPATIBLE"
    assert ELIGIBILITY_ELIGIBLE == "ELIGIBLE"


def test_utc_now_iso_returns_string():
    assert isinstance(utc_now_iso(), str)


def test_new_id_has_prefix():
    nid = new_id("test")
    assert nid.startswith("test-")


def test_to_dict_works():
    p = LocalModelProfile(model_id="m1")
    d = to_dict(p)
    assert d["model_id"] == "m1"


def test_stable_json_hash_is_deterministic():
    d = {"a": 1, "b": 2}
    h1 = stable_json_hash(d)
    h2 = stable_json_hash(dict(sorted(d.items())))
    assert h1 == h2
    assert len(h1) == 64
