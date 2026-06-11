from agentx_evolve.safety.circuit_breaker import MvpCircuitBreaker, TRIGGER_SELF_PROMOTION


class TestMvpCircuitBreaker:
    def setup_method(self):
        self.cb = MvpCircuitBreaker(max_failures=3)

    def test_initial_not_tripped(self):
        assert not self.cb.is_tripped

    def test_trip_activates_breaker(self):
        evt = self.cb.trip(TRIGGER_SELF_PROMOTION, "Self-promotion attempt", "act-1", "run-1")
        assert self.cb.is_tripped
        assert evt.trigger == TRIGGER_SELF_PROMOTION

    def test_too_many_failures_trips(self):
        for i in range(2):
            self.cb.record_failure("act-1", "run-1")
        assert not self.cb.is_tripped
        evt = self.cb.record_failure("act-1", "run-1")
        assert evt is not None
        assert self.cb.is_tripped

    def test_manual_stop(self):
        evt = self.cb.manual_stop("Operator requested stop", "act-1", "run-1")
        assert self.cb.is_tripped
        assert evt.trigger == "manual_stop_request"

    def test_reset(self):
        self.cb.trip(TRIGGER_SELF_PROMOTION, "test")
        self.cb.reset()
        assert not self.cb.is_tripped
        assert self.cb._failure_count == 0

    def test_events_filtered(self):
        self.cb.trip(TRIGGER_SELF_PROMOTION, "sp")
        self.cb.trip("manual_stop_request", "ms")
        sp_events = self.cb.events(TRIGGER_SELF_PROMOTION)
        assert len(sp_events) == 1

    def test_circuit_breaker_records_unsafe_self_promotion_event(self):
        evt = self.cb.trip(TRIGGER_SELF_PROMOTION, "Self-promotion attempt", "act-1", "run-1")
        assert evt.trigger == TRIGGER_SELF_PROMOTION
        assert "self-promotion" in evt.reason.lower()
        assert evt.action_id == "act-1"
        assert evt.run_id == "run-1"
        assert self.cb.is_tripped
        events = self.cb.events(TRIGGER_SELF_PROMOTION)
        assert len(events) == 1
        assert events[0].trigger == TRIGGER_SELF_PROMOTION
