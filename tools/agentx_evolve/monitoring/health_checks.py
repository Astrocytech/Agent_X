import warnings
from agentx_evolve.monitoring.monitoring_health import (
    HealthCheckFunc,
    register_health_check, deregister_health_check,
    run_health_check, run_all_health_checks, run_monitoring_health_checks,
    is_healthy,
)
warnings.warn(
    "agentx_evolve.monitoring.health_checks is deprecated; "
    "use agentx_evolve.monitoring.monitoring_health instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "HealthCheckFunc",
    "register_health_check", "deregister_health_check",
    "run_health_check", "run_all_health_checks", "run_monitoring_health_checks",
    "is_healthy",
]
