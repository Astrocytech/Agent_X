import warnings
from agentx_evolve.monitoring.monitoring_status import (
    register_component, set_component_status, update_session_count,
    build_runtime_status, get_component_status,
)
warnings.warn(
    "agentx_evolve.monitoring.status_reporter is deprecated; "
    "use agentx_evolve.monitoring.monitoring_status instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "register_component", "set_component_status", "update_session_count",
    "build_runtime_status", "get_component_status",
]
