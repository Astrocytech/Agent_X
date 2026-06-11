from agentx_evolve.config.runtime_profile import (
    MvpRuntimeProfile, load_profile, VALID_PROFILE_IDS,
)


class TestMvpRuntimeProfile:
    def test_valid_profile_creates(self):
        p = MvpRuntimeProfile(profile_id="STRICT")
        assert p.profile_id == "STRICT"
        assert p.is_live()

    def test_unknown_profile_fails(self):
        try:
            MvpRuntimeProfile(profile_id="UNKNOWN")
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_dry_run_profile(self):
        p = MvpRuntimeProfile(profile_id="DRY_RUN", allow_live_execution=False)
        assert p.is_dry_run()

    def test_replay_profile(self):
        p = MvpRuntimeProfile(profile_id="REPLAY", allow_live_execution=False,
                              require_review=False, require_rollback_plan=False)
        assert p.is_replay()

    def test_from_dict_rejects_unknown_fields(self):
        try:
            MvpRuntimeProfile.from_dict({"profile_id": "STRICT", "unknown_field": "x"})
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_load_profile(self):
        p = load_profile("STRICT")
        assert p.profile_id == "STRICT"

    def test_load_unknown_profile_fails(self):
        try:
            load_profile("NONEXISTENT")
            assert False, "Should have raised"
        except ValueError:
            pass
