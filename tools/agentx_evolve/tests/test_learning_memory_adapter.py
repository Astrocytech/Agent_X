from agentx_evolve.learning.memory_adapter import build_memory_write_request, check_memory_write_ready


def test_build_memory_write_request_ready():
    candidate = {"text": "learned behavior"}
    context = {"memory_layer_available": True, "human_approval_id": "ap-1"}
    result = build_memory_write_request(candidate, context)
    assert result["status"] == "READY"
    assert result["data"]["ready"] is True


def test_build_memory_write_request_memory_unavailable():
    candidate = {"text": "learned behavior"}
    context = {"memory_layer_available": False}
    result = build_memory_write_request(candidate, context)
    assert result["status"] == "BLOCKED"
    assert result["dependency_status"] == "MISSING"
    assert "Memory layer unavailable" in result["errors"]


def test_build_memory_write_request_needs_approval():
    candidate = {"text": "learned behavior"}
    context = {"memory_layer_available": True, "human_approval_id": None}
    result = build_memory_write_request(candidate, context)
    assert result["status"] == "NEEDS_APPROVAL"
    assert result["data"]["requires_approval"] is True


def test_build_memory_write_request_no_approval_key():
    candidate = {"text": "learned behavior"}
    context = {"memory_layer_available": True}
    result = build_memory_write_request(candidate, context)
    assert result["status"] == "NEEDS_APPROVAL"


def test_check_memory_write_ready():
    result = check_memory_write_ready({}, {"memory_layer_available": True, "human_approval_id": "ap-1"})
    assert result["status"] == "READY"
    assert result["data"]["ready"] is True


def test_check_memory_write_ready_blocked():
    result = check_memory_write_ready({}, {"memory_layer_available": False})
    assert result["status"] == "BLOCKED"
    assert result["dependency_status"] == "BLOCKED"


def test_check_memory_write_ready_needs_approval():
    result = check_memory_write_ready({}, {"memory_layer_available": True})
    assert result["status"] == "NEEDS_APPROVAL"
    assert result["data"]["needs_approval"] is True
