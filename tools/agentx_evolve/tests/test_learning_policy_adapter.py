from agentx_evolve.learning.policy_adapter import (
    check_durable_learning_allowed, check_follow_up_task_allowed, check_report_write_allowed,
)


def test_check_durable_learning_allowed_available():
    context = {"policy_registry_decision": {"decision": "ALLOW"}}
    result = check_durable_learning_allowed({}, context)
    assert result["status"] == "CHECKED"
    assert result["dependency_status"] == "AVAILABLE"
    assert result["data"]["decision"] == "ALLOW"


def test_check_durable_learning_allowed_missing():
    result = check_durable_learning_allowed({}, {})
    assert result["status"] == "BLOCKED"
    assert result["dependency_status"] == "MISSING"
    assert "Policy/Capability Registry unavailable" in result["errors"]


def test_check_follow_up_task_allowed_allowed():
    context = {"policy_registry_decision": {"follow_up_tasks_allowed": True}}
    result = check_follow_up_task_allowed({}, context)
    assert result["status"] == "ALLOWED"
    assert result["data"]["allowed"] is True


def test_check_follow_up_task_allowed_blocked():
    context = {"policy_registry_decision": {"follow_up_tasks_allowed": False}}
    result = check_follow_up_task_allowed({}, context)
    assert result["status"] == "BLOCKED"
    assert result["data"]["allowed"] is False


def test_check_follow_up_task_allowed_missing():
    result = check_follow_up_task_allowed({}, {})
    assert result["status"] == "BLOCKED"
    assert result["dependency_status"] == "MISSING"


def test_check_report_write_allowed_allowed():
    context = {"policy_registry_decision": {"report_write_allowed": True}}
    result = check_report_write_allowed({}, context)
    assert result["status"] == "ALLOWED"
    assert result["data"]["allowed"] is True


def test_check_report_write_allowed_blocked():
    context = {"policy_registry_decision": {"report_write_allowed": False}}
    result = check_report_write_allowed({}, context)
    assert result["status"] == "BLOCKED"
    assert result["data"]["allowed"] is False


def test_check_report_write_allowed_missing():
    result = check_report_write_allowed({}, {})
    assert result["status"] == "ALLOWED"
    assert result["data"]["allowed"] is True
    assert len(result["warnings"]) > 0
