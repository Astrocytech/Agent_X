from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentx_evolve.models.model_models import new_id
from agentx_evolve.monitoring.monitoring_utils import append_jsonl, ensure_dir
from agentx_evolve.monitoring.monitoring_events import (
    TraceSpan,
    TRACE_STATUS_OK, TRACE_STATUS_ERROR, TRACE_STATUS_TIMEOUT,
)

TRACES_DIR = Path(__file__).resolve().parent.parent / ".agentx-init" / "monitoring" / "traces"


_traces: dict[str, TraceSpan] = {}


def start_trace_span(
    operation: str,
    component: str,
    parent_span_id: str = "",
    trace_id: str = "",
    metadata: dict | None = None,
) -> TraceSpan:
    span_id = new_id("spn")
    if not trace_id:
        trace_id = new_id("trc")
    span = TraceSpan(
        span_id=span_id,
        parent_span_id=parent_span_id,
        trace_id=trace_id,
        operation=operation,
        component=component,
        status=TRACE_STATUS_OK,
        started_at=__import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
        metadata=metadata or {},
    )
    _traces[span_id] = span
    return span


def end_trace_span(span_id: str, status: str = TRACE_STATUS_OK,
                   metadata: dict | None = None) -> TraceSpan | None:
    span = _traces.get(span_id)
    if span is None:
        return None
    span.ended_at = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc).isoformat()
    start = __import__("datetime").datetime.fromisoformat(span.started_at)
    end = __import__("datetime").datetime.fromisoformat(span.ended_at)
    span.duration_ms = (end - start).total_seconds() * 1000
    span.status = status
    if metadata:
        span.metadata = {**(span.metadata or {}), **metadata}
    return span


def write_trace_span(span: TraceSpan, base_dir: Path | None = None) -> Path:
    dir_path = ensure_dir(base_dir or TRACES_DIR)
    traces_path = dir_path / "traces.jsonl"
    return append_jsonl(traces_path, span.to_dict())


def get_active_spans() -> list[TraceSpan]:
    return [s for s in _traces.values() if not s.ended_at]


def get_trace(trace_id: str) -> list[TraceSpan]:
    return [s for s in _traces.values() if s.trace_id == trace_id]


def clear_traces() -> None:
    _traces.clear()
