from agentx_evolve.worker.worker_models import (
    WorkerFailure, WF_TIMEOUT, WF_MODEL_ERROR, classify_worker_failure,
)


def test_worker_failure_defaults():
    wf = WorkerFailure()
    assert wf.failure_type == "UNKNOWN"
    assert wf.message == ""


def test_worker_failure_timeout():
    wf = WorkerFailure(failure_id="f-1", failure_type=WF_TIMEOUT, message="request timed out")
    assert wf.failure_id == "f-1"
    assert wf.failure_type == WF_TIMEOUT
    assert wf.message == "request timed out"


def test_classify_worker_failure_from_object():
    wf = WorkerFailure(failure_type=WF_MODEL_ERROR)
    assert classify_worker_failure(wf) == WF_MODEL_ERROR


def test_classify_worker_failure_from_dict():
    d = {"failure_type": WF_TIMEOUT}
    assert classify_worker_failure(d) == WF_TIMEOUT


def test_classify_worker_failure_from_string():
    assert classify_worker_failure("timeout") == "UNKNOWN"


def test_wf_constants():
    assert WF_TIMEOUT == "TIMEOUT"
    assert WF_MODEL_ERROR == "MODEL_ERROR"
