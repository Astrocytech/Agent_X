from agentx_evolve.worker.worker_models import WorkerBudget, BudgetCheck, BC_OK, BC_EXCEEDED


def test_worker_budget_defaults():
    wb = WorkerBudget()
    assert wb.max_tokens == 0
    assert wb.used_tokens == 0
    assert wb.status == BC_OK


def test_budget_check_defaults():
    bc = BudgetCheck()
    assert bc.status == BC_OK
    assert bc.message == ""


def test_budget_remaining():
    wb = WorkerBudget(max_tokens=1000, used_tokens=300)
    assert wb.remaining() == 700


def test_budget_consume_within_limit():
    wb = WorkerBudget(max_tokens=1000)
    wb.consume(500)
    assert wb.used_tokens == 500
    assert wb.status == BC_OK


def test_budget_consume_exceeds():
    wb = WorkerBudget(max_tokens=100)
    wb.consume(150)
    assert wb.status == BC_EXCEEDED


def test_bc_constants():
    assert BC_OK == "OK"
    assert BC_EXCEEDED == "EXCEEDED"
