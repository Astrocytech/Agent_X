import warnings
from agentx_evolve.orchestrator.orchestrator_models import OrchestratorCompletionRecord
warnings.warn(
    "agentx_evolve.monitoring.completion_record is deprecated; "
    "use agentx_evolve.orchestrator.orchestrator_models instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = ["OrchestratorCompletionRecord"]
