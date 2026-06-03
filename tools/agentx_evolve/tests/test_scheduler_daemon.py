import pytest
from agentx_evolve.scheduler.scheduler_daemon import SchedulerDaemon


class TestSchedulerDaemon:
    def test_default_status(self):
        daemon = SchedulerDaemon()
        status = daemon.status()
        assert status["running"] is False
        assert status["pid"] is None

    def test_start(self):
        daemon = SchedulerDaemon()
        result = daemon.start()
        assert result["status"] == "started"
        assert result["pid"] is not None

    def test_stop(self):
        daemon = SchedulerDaemon()
        daemon.start()
        result = daemon.stop()
        assert result["status"] == "stopped"

    def test_status_after_start(self):
        daemon = SchedulerDaemon()
        daemon.start()
        status = daemon.status()
        assert status["running"] is True
