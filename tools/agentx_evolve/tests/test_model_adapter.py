import pytest
from agentx_evolve.models.model_models import (
    ModelProfile, ModelRequest, ModelResponse, ModelProviderProfile,
    CAPABILITY_SMALL_FAST, CAPABILITY_SMALL_CODER,
    CAPABILITY_MEDIUM_CODER_OPTIONAL, CAPABILITY_HOSTED_FALLBACK_OPTIONAL,
    MODEL_STATUS_SUCCESS, MODEL_STATUS_FAILED, MODEL_STATUS_INVALID,
    TASK_IMPLEMENT_PATCH, TASK_FIX_VALIDATION, TASK_WRITE_TEST,
    TASK_EXPLAIN_FAILURE, TASK_REVIEW_OUTPUT, TASK_GENERATE_PLAN,
    TASK_SUMMARIZE_CONTEXT,
    ALL_MODEL_STATUSES, ALL_TASK_TYPES,
    new_id, utc_now_iso, to_dict,
)
from agentx_evolve.models.json_output_validator import (
    parse_json_output, validate_json_output, make_invalid_json_response,
)


# ---------------------------------------------------------------------------
# ModelProfile tests
# ---------------------------------------------------------------------------

def test_model_profile_defaults():
    p = ModelProfile()
    assert p.model_id == ""
    assert p.context_window == 4096


def test_model_profile_custom():
    p = ModelProfile(model_id="custom", display_name="test-model", context_window=2048)
    assert p.model_id == "custom"
    assert p.display_name == "test-model"


def test_model_profile_to_dict():
    p = ModelProfile(model_id="p1")
    d = to_dict(p)
    assert d["model_id"] == "p1"


# ---------------------------------------------------------------------------
# ModelRequest tests
# ---------------------------------------------------------------------------

def test_model_request_defaults():
    r = ModelRequest()
    assert r.task_type == TASK_SUMMARIZE_CONTEXT
    assert r.json_only


def test_model_request_custom():
    r = ModelRequest(task_type=TASK_WRITE_TEST, json_only=False, model_id=CAPABILITY_SMALL_CODER)
    assert r.task_type == TASK_WRITE_TEST
    assert not r.json_only


# ---------------------------------------------------------------------------
# ModelResponse tests
# ---------------------------------------------------------------------------

def test_model_response_defaults():
    r = ModelResponse()
    assert r.status == MODEL_STATUS_BLOCKED
    assert r.model_response_id == ""


def test_model_response_custom():
    r = ModelResponse(status=MODEL_STATUS_FAILED, errors=["timeout"])
    assert r.status == MODEL_STATUS_FAILED


# ---------------------------------------------------------------------------
# Constants tests
# ---------------------------------------------------------------------------

def test_all_model_statuses():
    assert len(ALL_MODEL_STATUSES) == 6
    assert MODEL_STATUS_SUCCESS in ALL_MODEL_STATUSES


def test_all_task_types():
    assert TASK_IMPLEMENT_PATCH in ALL_TASK_TYPES


# ---------------------------------------------------------------------------
# Serialization tests
# ---------------------------------------------------------------------------

def test_model_provider_config():
    c = ModelProviderProfile(provider_id="ollama", provider_type="OLLAMA")
    assert c.provider_id == "ollama"


def test_to_dict():
    p = ModelProfile(model_id="p1", display_name="m1")
    d = to_dict(p)
    assert d["model_id"] == "p1"
    assert d["display_name"] == "m1"


def test_helpers():
    nid = new_id("model")
    assert nid.startswith("model")
    iso = utc_now_iso()
    assert "T" in iso
