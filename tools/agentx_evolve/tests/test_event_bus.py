import tempfile
from pathlib import Path

from agentx_evolve.bus.event_bus import MvpEventBus, MvpEvent


class TestMvpEventBus:
    def setup_method(self):
        self._log = Path(tempfile.mkdtemp(prefix="test_evt_")) / "events.jsonl"
        self.bus = MvpEventBus(log_path=self._log)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self._log.parent, ignore_errors=True)

    def test_publish_and_history(self):
        evt = MvpEvent(message_id="m1", event_type="test", run_id="r1",
                       sender_id="s1", created_at="now")
        self.bus.publish(evt)
        hist = self.bus.history("r1")
        assert len(hist) == 1

    def test_publish_invalid_event_fails(self):
        try:
            self.bus.publish(MvpEvent())
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_subscribe_and_receive(self):
        received = []
        self.bus.subscribe("custom", lambda e: received.append(e))
        evt = MvpEvent(message_id="m2", event_type="custom", run_id="r2",
                       sender_id="s2", created_at="now")
        self.bus.publish(evt)
        assert len(received) == 1
        assert received[0].message_id == "m2"

    def test_persist_and_replay(self):
        evt = MvpEvent(message_id="m3", event_type="persist", run_id="r3",
                       sender_id="s3", created_at="now")
        self.bus.publish(evt)
        assert self._log.exists()

        bus2 = MvpEventBus(log_path=self._log)
        replayed = bus2.replay_log()
        assert len(replayed) == 1
        assert replayed[0].message_id == "m3"

    def test_clear(self):
        self.bus.publish(MvpEvent(message_id="m4", event_type="t", run_id="r4",
                                  sender_id="s4", created_at="now"))
        self.bus.clear()
        assert len(self.bus.history()) == 0
