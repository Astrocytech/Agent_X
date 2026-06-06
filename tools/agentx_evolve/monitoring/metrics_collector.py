import warnings
from agentx_evolve.monitoring.monitoring_metrics import (
    Counter, Gauge,
    register_counter, register_gauge,
    collect_metrics, write_metrics, collect_monitoring_metrics,
    reset_metrics,
)
warnings.warn(
    "agentx_evolve.monitoring.metrics_collector is deprecated; "
    "use agentx_evolve.monitoring.monitoring_metrics instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "Counter", "Gauge",
    "register_counter", "register_gauge",
    "collect_metrics", "write_metrics", "collect_monitoring_metrics",
    "reset_metrics",
]
