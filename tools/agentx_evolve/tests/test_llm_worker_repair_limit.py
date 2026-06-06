from agentx_evolve.worker.worker_models import RepairLimit, RL_EXCEEDED, RL_OK


def test_repair_limit_defaults():
    rl = RepairLimit()
    assert rl.max_repairs == 3
    assert rl.current_repairs == 0
    assert rl.status == RL_OK


def test_repair_limit_can_repair():
    rl = RepairLimit(max_repairs=2)
    assert rl.can_repair() is True


def test_repair_limit_exceeded():
    rl = RepairLimit(max_repairs=2)
    rl.record_repair()
    rl.record_repair()
    assert rl.can_repair() is False
    assert rl.status == RL_EXCEEDED


def test_repair_limit_record_tracks_count():
    rl = RepairLimit(max_repairs=5)
    for _ in range(3):
        rl.record_repair()
    assert rl.current_repairs == 3
    assert rl.status == RL_OK


def test_rl_constants():
    assert RL_OK == "OK"
    assert RL_EXCEEDED == "EXCEEDED"
