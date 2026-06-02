import pytest
from agentx_initiator.core.memory_model import MemoryRecord, MemoryReference, MemoryIndex, MemorySnapshot, MemoryQuery, MemoryQueryResult, MemoryManifest, MemoryWriteResult


def test_memory_record_defaults():
    r = MemoryRecord(memory_id="r1", source_component="scan")
    assert r.payload == {}
    assert r.status == "ACTIVE"


def test_memory_record_to_dict():
    r = MemoryRecord(memory_id="r1", source_component="scan", payload={"files": 10})
    d = r.to_dict()
    assert d["memory_id"] == "r1"


def test_memory_reference_defaults():
    ref = MemoryReference()
    assert ref.reference_type == ""


def test_memory_index_to_dict():
    idx = MemoryIndex(index_id="i1")
    d = idx.to_dict()
    assert d["index_id"] == "i1"


def test_memory_snapshot_defaults():
    snap = MemorySnapshot(snapshot_id="s1")
    assert snap.record_count == 0


def test_memory_query_defaults():
    q = MemoryQuery()
    assert q.memory_id is None


def test_memory_query_result_defaults():
    r = MemoryQueryResult()
    assert r.result_count == 0


def test_memory_manifest_defaults():
    m = MemoryManifest(manifest_id="m1")
    assert m.record_count == 0


def test_memory_write_result_defaults():
    wr = MemoryWriteResult()
    assert wr.status == "SUCCESS"
