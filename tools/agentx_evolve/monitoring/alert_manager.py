import warnings
from agentx_evolve.monitoring.monitoring_alerts import (
    AlertRule, AlertCondition,
    register_alert_rule, evaluate_alerts,
    get_active_alerts, acknowledge_alert, clear_alerts,
)
warnings.warn(
    "agentx_evolve.monitoring.alert_manager is deprecated; "
    "use agentx_evolve.monitoring.monitoring_alerts instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "AlertRule", "AlertCondition",
    "register_alert_rule", "evaluate_alerts",
    "get_active_alerts", "acknowledge_alert", "clear_alerts",
]
