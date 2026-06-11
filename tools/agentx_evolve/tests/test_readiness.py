from agentx_evolve.health.readiness import MvpReadinessCheck, ReadinessCheckItem


class TestMvpReadinessCheck:
    def test_all_checks_pass(self):
        r = MvpReadinessCheck()
        r.add("check1", lambda: True)
        r.add("check2", lambda: True)
        result = r.run_all()
        assert result.all_pass

    def test_critical_check_fails(self):
        r = MvpReadinessCheck()
        r.add("good", lambda: True)
        r.add("bad", lambda: False, critical=True)
        result = r.run_all()
        assert not result.all_pass

    def test_non_critical_failure_allowed(self):
        r = MvpReadinessCheck()
        r.add("good", lambda: True)
        r.add("bad", lambda: False, critical=False)
        result = r.run_all()
        assert result.all_pass

    def test_is_ready(self):
        r = MvpReadinessCheck()
        r.add("ok", lambda: True)
        assert r.is_ready()

        r.add("fail", lambda: False)
        assert not r.is_ready()

    def test_check_exception_handled(self):
        r = MvpReadinessCheck()
        r.add("crash", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        result = r.run_all()
        assert not result.all_pass
