import pytest

from agentx_evolve.blackboard.blackboard import MvpBlackboard, MvpBlackboardRecord


@pytest.fixture
def board() -> MvpBlackboard:
    return MvpBlackboard()


def make_record(
    record_id: str = "rec-1",
    record_type: str = "observation",
    owner: str = "agent-a",
    run_id: str = "run-1",
    data: dict | None = None,
) -> MvpBlackboardRecord:
    return MvpBlackboardRecord(
        record_id=record_id,
        record_type=record_type,
        owner=owner,
        run_id=run_id,
        data=data or {},
    )


class TestMvpBlackboard:
    def test_record_creation(self) -> None:
        record = make_record()
        assert record.record_id == "rec-1"
        assert record.record_type == "observation"
        assert record.owner == "agent-a"
        assert record.run_id == "run-1"
        assert record.data == {}
        assert record.version == 1
        assert record.created_at == ""

    def test_write_and_read(self, board: MvpBlackboard) -> None:
        record = make_record()
        written = board.write(record)
        assert board.read("rec-1") is written

    def test_write_increments_version(self, board: MvpBlackboard) -> None:
        record = make_record()
        v1 = board.write(record)
        assert v1.version == 1
        v2 = board.write(make_record(record_id="rec-1"))
        assert v2.version == 2

    def test_query_by_run_id(self, board: MvpBlackboard) -> None:
        r1 = make_record(record_id="r1", run_id="run-x")
        r2 = make_record(record_id="r2", run_id="run-y")
        r3 = make_record(record_id="r3", run_id="run-x")
        board.write(r1)
        board.write(r2)
        board.write(r3)
        results = board.query(run_id="run-x")
        assert {r.record_id for r in results} == {"r1", "r3"}

    def test_query_by_record_type(self, board: MvpBlackboard) -> None:
        r1 = make_record(record_id="r1", record_type="observation")
        r2 = make_record(record_id="r2", record_type="critique")
        board.write(r1)
        board.write(r2)
        results = board.query(record_type="critique")
        assert len(results) == 1
        assert results[0].record_id == "r2"

    def test_query_by_owner(self, board: MvpBlackboard) -> None:
        r1 = make_record(record_id="r1", owner="alice")
        r2 = make_record(record_id="r2", owner="bob")
        board.write(r1)
        board.write(r2)
        results = board.query(owner="alice")
        assert len(results) == 1
        assert results[0].record_id == "r1"

    def test_get_latest(self, board: MvpBlackboard) -> None:
        r1 = MvpBlackboardRecord(
            record_id="r1",
            record_type="observation",
            owner="agent-a",
            run_id="run-1",
            data={},
            created_at="2025-01-01T00:00:00",
        )
        r2 = MvpBlackboardRecord(
            record_id="r2",
            record_type="observation",
            owner="agent-a",
            run_id="run-1",
            data={},
            created_at="2025-01-02T00:00:00",
        )
        board.write(r1)
        board.write(r2)
        latest = board.get_latest("observation", "run-1")
        assert latest is not None
        assert latest.record_id == "r2"

    def test_nonexistent_record_returns_none(self, board: MvpBlackboard) -> None:
        assert board.read("does-not-exist") is None
