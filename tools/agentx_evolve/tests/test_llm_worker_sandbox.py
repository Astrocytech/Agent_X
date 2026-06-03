from agentx_evolve.worker.worker_models import WorkerSandbox, SandboxResult, SR_ALLOW, SR_BLOCK


def test_sandbox_result_defaults():
    sr = SandboxResult()
    assert sr.allowed is True
    assert sr.status == SR_ALLOW
    assert sr.reason == ""


def test_sandbox_result_block():
    sr = SandboxResult(allowed=False, status=SR_BLOCK, reason="policy blocked")
    assert sr.allowed is False
    assert sr.status == SR_BLOCK
    assert sr.reason == "policy blocked"


def test_worker_sandbox_defaults():
    ws = WorkerSandbox()
    assert ws.allowed is True
    assert ws.result is None


def test_worker_sandbox_with_result():
    sr = SandboxResult(allowed=False, status=SR_BLOCK)
    ws = WorkerSandbox(sandbox_id="sb-1", allowed=False, reason="blocked", result=sr)
    assert ws.sandbox_id == "sb-1"
    assert ws.allowed is False
    assert ws.result is not None
    assert ws.result.status == SR_BLOCK


def test_sr_constants():
    assert SR_ALLOW == "ALLOW"
    assert SR_BLOCK == "BLOCK"
