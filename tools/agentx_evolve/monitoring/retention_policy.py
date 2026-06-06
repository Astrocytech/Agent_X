import warnings
from agentx_evolve.monitoring.monitoring_retention import (
    RetentionPolicy, apply_retention_policy, apply_monitoring_retention_policy,
)
warnings.warn(
    "agentx_evolve.monitoring.retention_policy is deprecated; "
    "use agentx_evolve.monitoring.monitoring_retention instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "RetentionPolicy", "apply_retention_policy", "apply_monitoring_retention_policy",
]
