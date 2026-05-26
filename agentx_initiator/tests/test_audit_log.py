from agentx_initiator.core.audit_log import append_event, read_events
from agentx_initiator.core.paths import ensure_state_dirs


def test_append_and_read_event():
    ensure_state_dirs()
    test_event = {"event_type": "test", "detail": "unit test event"}
    append_event(test_event)
    events = read_events(limit=10)
    found = any(e.get("event_type") == "test" for e in events)
    assert found
