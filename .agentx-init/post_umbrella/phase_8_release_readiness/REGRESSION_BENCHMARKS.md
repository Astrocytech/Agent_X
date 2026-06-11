# Regression Benchmarks

## Categories (B001-B020)

| ID | Category | Coverage |
|----|----------|----------|
| B001 | Umbrella positive behavior | Agent suite tests |
| B002 | Umbrella safe-failure | Agent tests |
| B003 | Clothing positive behavior | Agent suite tests |
| B004 | Clothing safe-failure | Agent tests |
| B005 | Planning positive behavior | Agent suite tests |
| B006 | Planning safe-failure | Agent tests |
| B007 | Policy rejection | Governance benchmarks |
| B008 | Path boundary rejection | Governance benchmarks |
| B009 | Invalid model output rejection | Governance benchmarks |
| B010 | Rollback behavior | Governance benchmarks |
| B011 | Review/promotion gate | Governance benchmarks |
| B012 | Evidence manifest integrity | Governance benchmarks |
| B013 | Source hash integrity | Governance benchmarks |
| B014 | Clean-checkout replay | Replay documentation |
| B015 | No-op command rejection | Governance benchmarks |
| B016 | Manual insertion rejection | Governance benchmarks |
| B017 | Secret-in-evidence rejection | Governance benchmarks |
| B018 | Dependency change rejection | Governance benchmarks |
| B019 | Unsupported claim rejection | Governance benchmarks |
| B020 | Event log integrity | Governance benchmarks |

## Test Files

| File | Coverage |
|------|----------|
| `tests/release/test_governance_benchmarks.py` | B007-B013, B015-B020 |
| `tests/quick/umbrella_agent/` | B001-B002 |
| `tests/quick/clothing_advice_agent/` | B003-B004 |
| `tests/quick/daily_planning_agent/` | B005-B006 |
| Replay documentation | B014 |

## Running

```bash
python3 -m pytest tests/release/test_governance_benchmarks.py -v
python3 -m pytest tests/quick/ -v
```
