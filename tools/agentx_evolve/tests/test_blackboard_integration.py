import os
import tempfile

from agentx_evolve.blackboard.blackboard import MvpBlackboard, MvpBlackboardRecord


class TestBlackboardPersistence:
    def test_persists_to_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            bb = MvpBlackboard(base_path=tmp)
            rec = MvpBlackboardRecord(
                record_id="persisted-1",
                record_type="observation",
                owner="test",
                run_id="run-persist",
                data={"key": "value"},
            )
            bb.write(rec)
            jsonl_path = os.path.join(tmp, "run-persist.jsonl")
            assert os.path.isfile(jsonl_path)
            with open(jsonl_path) as f:
                content = f.read()
            assert "persisted-1" in content
            assert "observation" in content

    def test_loads_from_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            bb1 = MvpBlackboard(base_path=tmp)
            bb1.write(MvpBlackboardRecord(
                record_id="loaded-1", record_type="plan_draft",
                owner="a", run_id="run-load", data={"step": 1},
            ))
            bb1.write(MvpBlackboardRecord(
                record_id="loaded-2", record_type="observation",
                owner="b", run_id="run-load", data={"step": 2},
            ))
            bb2 = MvpBlackboard(base_path=tmp)
            bb2.load_run("run-load")
            r1 = bb2.read("loaded-1")
            assert r1 is not None
            assert r1.record_type == "plan_draft"
            assert r1.data == {"step": 1}
            r2 = bb2.read("loaded-2")
            assert r2 is not None
            assert r2.record_type == "observation"

    def test_flush_rewrites_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            bb = MvpBlackboard(base_path=tmp)
            bb.write(MvpBlackboardRecord(
                record_id="flush-1", record_type="observation",
                owner="a", run_id="run-flush", data={"v": 1},
            ))
            bb.write(MvpBlackboardRecord(
                record_id="flush-2", record_type="critique",
                owner="b", run_id="run-flush", data={"v": 2},
            ))
            bb.write(MvpBlackboardRecord(
                record_id="flush-3", record_type="critique",
                owner="c", run_id="run-other", data={"v": 3},
            ))
            bb.flush()
            assert os.path.isfile(os.path.join(tmp, "run-flush.jsonl"))
            assert os.path.isfile(os.path.join(tmp, "run-other.jsonl"))

    def test_search_by_data_key(self):
        bb = MvpBlackboard()
        bb.write(MvpBlackboardRecord(
            record_id="s1", record_type="observation",
            owner="a", run_id="run-s", data={"type": "file_created", "path": "/x"},
        ))
        bb.write(MvpBlackboardRecord(
            record_id="s2", record_type="observation",
            owner="b", run_id="run-s", data={"type": "file_deleted", "path": "/y"},
        ))
        results = bb.search_data("run-s", "type", "file_created")
        assert len(results) == 1
        assert results[0].record_id == "s1"
