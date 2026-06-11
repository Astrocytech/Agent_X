from agentx_evolve.runtime.runtime_context import (
    MvpRuntimeContext, MvpDeterministicClock, MvpSeededRandomness,
)


class TestMvpDeterministicClock:
    def test_fixed_clock_produces_stable_timestamp(self):
        clock = MvpDeterministicClock("2026-06-10T12:00:00+00:00")
        assert clock.now_iso() == "2026-06-10T12:00:00+00:00"
        assert clock.now_iso() == "2026-06-10T12:00:00+00:00"

    def test_serialize_deserialize(self):
        clock = MvpDeterministicClock("2026-06-10T12:00:00+00:00")
        data = clock.serialize()
        restored = MvpDeterministicClock.deserialize(data)
        assert restored.now_iso() == "2026-06-10T12:00:00+00:00"


class TestMvpSeededRandomness:
    def test_same_seed_produces_same_sequence(self):
        a = MvpSeededRandomness("test-seed-123")
        b = MvpSeededRandomness("test-seed-123")
        assert a.next_hex(8) == b.next_hex(8)
        assert a.next_hex(8) == b.next_hex(8)

    def test_different_seed_different_output(self):
        a = MvpSeededRandomness("seed-a")
        b = MvpSeededRandomness("seed-b")
        assert a.next_hex(8) != b.next_hex(8)

    def test_serialize_deserialize(self):
        rng = MvpSeededRandomness("test-seed")
        rng.next_hex(8)
        data = rng.serialize()
        restored = MvpSeededRandomness.deserialize(data)
        assert restored.next_hex(8) == rng.next_hex(8)


class TestMvpRuntimeContext:
    def test_initialize_sets_ids(self):
        ctx = MvpRuntimeContext()
        ctx.randomness = MvpSeededRandomness("ctx-seed")
        ctx.clock = MvpDeterministicClock("2026-06-10T12:00:00+00:00")
        ctx.initialize(goal_text="test goal", profile_id="test-profile")
        assert ctx.run_id.startswith("run_")
        assert ctx.goal_id.startswith("goal_")
        assert ctx.profile_id == "test-profile"

    def test_serialize_deserialize(self):
        ctx = MvpRuntimeContext()
        ctx.randomness = MvpSeededRandomness("ctx-seed")
        ctx.clock = MvpDeterministicClock("2026-06-10T12:00:00+00:00")
        ctx.initialize(goal_text="test", profile_id="p1")
        data = ctx.serialize()
        restored = MvpRuntimeContext.deserialize(data)
        assert restored.run_id == ctx.run_id
        assert restored.goal_id == ctx.goal_id
        assert restored.profile_id == ctx.profile_id
