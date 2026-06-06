from agentx_evolve.worker.worker_models import ConcurrencyLimit, ConcurrencySlot, acquire_slot, release_slot


def test_concurrency_limit_defaults():
    cl = ConcurrencyLimit()
    assert cl.max_slots == 1
    assert cl.used_slots == 0


def test_concurrency_limit_available():
    cl = ConcurrencyLimit(max_slots=3)
    assert cl.available_slots() == 3
    assert cl.is_full() is False


def test_acquire_slot_returns_slot():
    cl = ConcurrencyLimit(max_slots=2)
    slot = acquire_slot(cl, "slot-1")
    assert slot is not None
    assert slot.slot_id == "slot-1"
    assert slot.occupied is True
    assert cl.used_slots == 1


def test_acquire_slot_when_full():
    cl = ConcurrencyLimit(max_slots=1)
    acquire_slot(cl, "s1")
    result = acquire_slot(cl, "s2")
    assert result is None
    assert cl.is_full() is True


def test_release_slot():
    cl = ConcurrencyLimit(max_slots=2)
    slot = acquire_slot(cl, "s1")
    result = release_slot(cl, slot)
    assert result is True
    assert cl.used_slots == 0
    assert slot.occupied is False


def test_release_slot_no_slots():
    cl = ConcurrencyLimit()
    result = release_slot(cl, ConcurrencySlot(slot_id="ghost"))
    assert result is False
