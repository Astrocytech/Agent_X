from agentx_evolve.scheduler.scheduler_network import SchedulerNetworkConfig


class TestSchedulerNetworkConfig:
    def test_defaults(self):
        config = SchedulerNetworkConfig()
        assert config.host == "127.0.0.1"
        assert config.port == 0
        assert config.use_ssl is False

    def test_custom_values(self):
        config = SchedulerNetworkConfig(host="0.0.0.0", port=8080, use_ssl=True)
        assert config.host == "0.0.0.0"
        assert config.port == 8080
        assert config.use_ssl is True
