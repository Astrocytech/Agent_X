from pathlib import Path

import pytest

from agentx_evolve.monitoring.monitoring_metrics import (
    Counter, Gauge,
    register_counter, register_gauge,
    collect_metrics, collect_monitoring_metrics,
    write_metrics, reset_metrics,
)


def setup_method():
    reset_metrics()


def teardown_method():
    reset_metrics()


def test_counter_defaults():
    c = Counter(name="test_counter")
    assert c.name == "test_counter"
    assert c.value == 0.0
    assert c.labels == {}


def test_counter_inc():
    c = Counter(name="c")
    c.inc()
    assert c.value == 1.0
    c.inc(5.0)
    assert c.value == 6.0


def test_gauge_defaults():
    g = Gauge(name="test_gauge")
    assert g.name == "test_gauge"
    assert g.value == 0.0


def test_gauge_set():
    g = Gauge(name="g")
    g.set(42.0)
    assert g.value == 42.0
    g.set(-1.0)
    assert g.value == -1.0


def test_register_counter():
    reset_metrics()
    c = register_counter("requests_total", {"method": "GET"})
    assert c.name == "requests_total"
    assert c.labels == {"method": "GET"}
    assert c.value == 0.0


def test_register_counter_reuses_existing():
    reset_metrics()
    c1 = register_counter("requests_total")
    c2 = register_counter("requests_total")
    assert c1 is c2


def test_register_gauge():
    reset_metrics()
    g = register_gauge("cpu_usage", {"host": "h1"})
    assert g.name == "cpu_usage"
    assert g.value == 0.0


def test_register_gauge_reuses_existing():
    reset_metrics()
    g1 = register_gauge("cpu_usage")
    g2 = register_gauge("cpu_usage")
    assert g1 is g2


def test_collect_metrics_empty():
    reset_metrics()
    records = collect_metrics(component="test")
    assert records == []


def test_collect_metrics():
    reset_metrics()
    c = register_counter("reqs")
    c.inc(3)
    g = register_gauge("temp")
    g.set(36.5)
    records = collect_metrics(component="cmp")
    assert len(records) == 2
    names = {r.name for r in records}
    assert names == {"reqs", "temp"}
    for r in records:
        assert r.component == "cmp"
        assert r.timestamp != ""


def test_collect_metrics_values():
    reset_metrics()
    c = register_counter("reqs")
    c.inc(7)
    records = collect_metrics()
    counter_records = [r for r in records if r.name == "reqs"]
    assert len(counter_records) == 1
    assert counter_records[0].value == 7.0
    assert counter_records[0].unit == "count"


def test_collect_monitoring_metrics():
    reset_metrics()
    register_counter("test")
    records = collect_monitoring_metrics(component="cmp")
    assert len(records) == 1


def test_write_metrics(tmp_path):
    reset_metrics()
    c = register_counter("reqs")
    c.inc(3)
    records = collect_metrics(component="cmp")
    path = write_metrics(records, base_dir=tmp_path)
    assert path.exists()
    assert path.name == "metrics.jsonl"
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 1
    import json
    data = json.loads(lines[0])
    assert data["value"] == 3.0


def test_write_metrics_multiple(tmp_path):
    reset_metrics()
    c = register_counter("reqs")
    c.inc(3)
    register_gauge("temp")
    records = collect_metrics()
    write_metrics(records, base_dir=tmp_path)
    lines = (tmp_path / "metrics.jsonl").read_text().strip().split("\n")
    assert len(lines) == 2


def test_write_metrics_default_dir(tmp_path):
    reset_metrics()
    records = collect_metrics()
    path = write_metrics(records, base_dir=tmp_path)
    assert path.parent == tmp_path


def test_reset_metrics():
    reset_metrics()
    register_counter("c")
    register_gauge("g")
    assert len(collect_metrics()) == 2
    reset_metrics()
    assert collect_metrics() == []
