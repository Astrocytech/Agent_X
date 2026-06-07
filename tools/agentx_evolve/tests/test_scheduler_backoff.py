import pytest

from agentx_evolve.scheduler.backoff import (
    compute_backoff_seconds,
    compute_next_run_at,
    jitter_backoff_seconds,
    linear_backoff_seconds,
    fibonacci_backoff_seconds,
)


class TestComputeBackoffSeconds:
    def test_attempt_zero(self):
        assert compute_backoff_seconds(0) == 30

    def test_attempt_one(self):
        assert compute_backoff_seconds(1) == 60

    def test_attempt_two(self):
        assert compute_backoff_seconds(2) == 120

    def test_exponential_growth(self):
        prev = 0
        for i in range(5):
            val = compute_backoff_seconds(i)
            assert val > prev
            prev = val

    def test_max_delay(self):
        val = compute_backoff_seconds(100, max_delay=3600)
        assert val == 3600

    def test_custom_base_and_multiplier(self):
        val = compute_backoff_seconds(2, base_seconds=10, multiplier=3)
        assert val == 90


class TestComputeNextRunAt:
    def test_returns_iso_string(self):
        result = compute_next_run_at(0)
        assert result.endswith("Z")
        assert "T" in result

    def test_increasing_delays(self):
        t1 = compute_next_run_at(0)
        t2 = compute_next_run_at(2)
        assert t2 > t1


class TestJitterBackoff:
    def test_returns_positive_int(self):
        val = jitter_backoff_seconds(1)
        assert isinstance(val, int)
        assert val > 0

    def test_jitter_differs(self):
        vals = {jitter_backoff_seconds(1) for _ in range(20)}
        assert len(vals) > 1


class TestLinearBackoff:
    def test_linear_increase(self):
        v0 = linear_backoff_seconds(0)
        v1 = linear_backoff_seconds(1)
        v2 = linear_backoff_seconds(2)
        assert v0 < v1 < v2

    def test_max_delay(self):
        val = linear_backoff_seconds(9999, max_delay=300)
        assert val == 300


class TestFibonacciBackoff:
    def test_fibonacci_sequence(self):
        v0 = fibonacci_backoff_seconds(0)
        v1 = fibonacci_backoff_seconds(1)
        v2 = fibonacci_backoff_seconds(2)
        v3 = fibonacci_backoff_seconds(3)
        assert v0 == 0
        assert v1 == 30
        assert v2 == 30
        assert v3 == 60

    def test_max_delay(self):
        val = fibonacci_backoff_seconds(100, max_delay=500)
        assert val <= 500
