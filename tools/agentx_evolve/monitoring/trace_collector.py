import warnings
from agentx_evolve.monitoring.monitoring_traces import (
    start_trace_span, end_trace_span, write_trace_span,
    get_active_spans, get_trace, clear_traces,
)
warnings.warn(
    "agentx_evolve.monitoring.trace_collector is deprecated; "
    "use agentx_evolve.monitoring.monitoring_traces instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "start_trace_span", "end_trace_span", "write_trace_span",
    "get_active_spans", "get_trace", "clear_traces",
]
