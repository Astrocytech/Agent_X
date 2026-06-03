from pathlib import Path

import pytest

from agentx_evolve.monitoring.monitoring_traces import (
    start_trace_span, end_trace_span,
    write_trace_span, get_active_spans, get_trace, clear_traces,
)
from agentx_evolve.monitoring.monitoring_events import (
    TRACE_STATUS_OK, TRACE_STATUS_ERROR, TRACE_STATUS_TIMEOUT,
)


def setup_function():
    clear_traces()


def teardown_function():
    clear_traces()


def test_start_trace_span():
    span = start_trace_span(operation="query", component="cmp")
    assert span.span_id.startswith("spn")
    assert span.trace_id.startswith("trc")
    assert span.operation == "query"
    assert span.component == "cmp"
    assert span.status == TRACE_STATUS_OK
    assert span.started_at != ""
    assert span.ended_at == ""
    assert span.duration_ms == 0.0


def test_start_trace_span_with_parent():
    parent = start_trace_span(operation="parent", component="cmp")
    child = start_trace_span(operation="child", component="cmp",
                             parent_span_id=parent.span_id,
                             trace_id=parent.trace_id)
    assert child.parent_span_id == parent.span_id
    assert child.trace_id == parent.trace_id


def test_start_trace_span_explicit_trace_id():
    span = start_trace_span(operation="op", component="cmp",
                            trace_id="custom-trace")
    assert span.trace_id == "custom-trace"


def test_end_trace_span():
    span = start_trace_span(operation="query", component="cmp")
    result = end_trace_span(span.span_id, status=TRACE_STATUS_OK)
    assert result is not None
    assert result.span_id == span.span_id
    assert result.ended_at != ""
    assert result.duration_ms >= 0
    assert result.status == TRACE_STATUS_OK


def test_end_trace_span_error():
    span = start_trace_span(operation="query", component="cmp")
    result = end_trace_span(span.span_id, status=TRACE_STATUS_ERROR)
    assert result.status == TRACE_STATUS_ERROR


def test_end_trace_span_with_metadata():
    span = start_trace_span(operation="query", component="cmp")
    result = end_trace_span(span.span_id, metadata={"result": "ok"})
    assert result.metadata == {"result": "ok"}


def test_end_trace_span_merges_metadata():
    span = start_trace_span(operation="query", component="cmp",
                            metadata={"initial": "data"})
    result = end_trace_span(span.span_id, metadata={"result": "ok"})
    assert result.metadata == {"initial": "data", "result": "ok"}


def test_end_trace_span_nonexistent():
    result = end_trace_span("nonexistent")
    assert result is None


def test_write_trace_span(tmp_path):
    span = start_trace_span(operation="op", component="cmp")
    end_trace_span(span.span_id)
    path = write_trace_span(span, base_dir=tmp_path)
    assert path.parent == tmp_path
    assert path.name == "traces.jsonl"
    assert path.exists()
    import json
    data = json.loads(path.read_text().strip())
    assert data["span_id"] == span.span_id


def test_get_active_spans():
    span = start_trace_span(operation="active", component="cmp")
    active = get_active_spans()
    assert span in active


def test_get_active_spans_after_end():
    span = start_trace_span(operation="done", component="cmp")
    end_trace_span(span.span_id)
    assert span not in get_active_spans()


def test_get_active_spans_empty():
    clear_traces()
    assert get_active_spans() == []


def test_get_trace():
    span1 = start_trace_span(operation="op1", component="cmp")
    span2 = start_trace_span(operation="op2", component="cmp",
                             trace_id=span1.trace_id)
    spans = get_trace(span1.trace_id)
    assert len(spans) == 2
    assert span1 in spans
    assert span2 in spans


def test_get_trace_no_match():
    spans = get_trace("nonexistent")
    assert spans == []


def test_clear_traces():
    start_trace_span(operation="op", component="cmp")
    assert len(get_active_spans()) == 1
    clear_traces()
    assert get_active_spans() == []
