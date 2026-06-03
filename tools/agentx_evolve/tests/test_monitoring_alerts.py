from pathlib import Path

import pytest

from agentx_evolve.monitoring.monitoring_alerts import (
    AlertRule, _rules, _alerts,
    register_alert_rule, evaluate_alerts,
    get_active_alerts, acknowledge_alert, clear_alerts,
)
from agentx_evolve.monitoring.monitoring_events import (
    ALERT_SEVERITY_CRITICAL, ALERT_SEVERITY_HIGH,
    ALERT_SEVERITY_MEDIUM, ALERT_SEVERITY_LOW,
)


def setup_function():
    _rules.clear()
    _alerts.clear()


def teardown_function():
    _rules.clear()
    _alerts.clear()


def test_alert_rule_defaults():
    rule = AlertRule(name="test_rule")
    assert rule.name == "test_rule"
    assert rule.condition is None
    assert rule.severity == ALERT_SEVERITY_MEDIUM
    assert rule.component == ""
    assert rule.enabled is True


def test_register_alert_rule():
    def condition():
        return True, "fired", ALERT_SEVERITY_HIGH
    rule = register_alert_rule("high_cpu", condition,
                               severity=ALERT_SEVERITY_CRITICAL,
                               component="cmp")
    assert rule.name == "high_cpu"
    assert rule.severity == ALERT_SEVERITY_CRITICAL
    assert rule.component == "cmp"


def test_evaluate_alerts_fires(tmp_path):
    def condition():
        return True, "cpu > 90%", ALERT_SEVERITY_CRITICAL
    register_alert_rule("high_cpu", condition)
    alerts = evaluate_alerts(base_dir=tmp_path)
    assert len(alerts) == 1
    assert alerts[0].rule_name == "high_cpu"
    assert alerts[0].severity == ALERT_SEVERITY_CRITICAL


def test_evaluate_alerts_no_fire(tmp_path):
    def condition():
        return False, "", ALERT_SEVERITY_LOW
    register_alert_rule("quiet", condition)
    alerts = evaluate_alerts(base_dir=tmp_path)
    assert alerts == []


def test_evaluate_alerts_multiple_rules():
    def fired():
        return True, "fired", ALERT_SEVERITY_HIGH
    def not_fired():
        return False, "", ALERT_SEVERITY_LOW
    register_alert_rule("rule_a", fired)
    register_alert_rule("rule_b", not_fired)
    alerts = evaluate_alerts()
    assert len(alerts) == 1
    assert alerts[0].rule_name == "rule_a"


def test_evaluate_alerts_exception():
    def broken():
        raise RuntimeError("something broke")
    register_alert_rule("broken", broken)
    alerts = evaluate_alerts()
    assert len(alerts) == 1
    assert alerts[0].severity == ALERT_SEVERITY_HIGH
    assert "something broke" in alerts[0].message


def test_evaluate_alerts_disabled_rule():
    def fired():
        return True, "fired", ALERT_SEVERITY_HIGH
    rule = register_alert_rule("disabled_rule", fired)
    rule.enabled = False
    alerts = evaluate_alerts()
    assert alerts == []


def test_evaluate_alerts_writes_file(tmp_path):
    def condition():
        return True, "alert!", ALERT_SEVERITY_MEDIUM
    register_alert_rule("test", condition)
    evaluate_alerts(base_dir=tmp_path)
    alert_file = tmp_path / "alerts.jsonl"
    assert alert_file.exists()
    import json
    data = json.loads(alert_file.read_text().strip().split("\n")[0])
    assert data["rule_name"] == "test"


def test_get_active_alerts():
    def fired():
        return True, "fired", ALERT_SEVERITY_HIGH
    register_alert_rule("test", fired)
    evaluate_alerts()
    active = get_active_alerts()
    assert len(active) == 1
    assert active[0].acknowledged is False


def test_acknowledge_alert():
    def fired():
        return True, "fired", ALERT_SEVERITY_HIGH
    register_alert_rule("test", fired)
    alerts = evaluate_alerts()
    alert_id = alerts[0].alert_id
    result = acknowledge_alert(alert_id)
    assert result is True
    assert get_active_alerts() == []


def test_acknowledge_alert_nonexistent():
    result = acknowledge_alert("nonexistent")
    assert result is False


def test_clear_alerts():
    def fired():
        return True, "fired", ALERT_SEVERITY_HIGH
    register_alert_rule("test", fired)
    evaluate_alerts()
    assert len(get_active_alerts()) == 1
    clear_alerts()
    assert get_active_alerts() == []



