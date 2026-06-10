# Baseline Document Alignment Audit

**Generated**: 2026-06-09
**Repository**: https://github.com/Astrocytech/Agent_X
**Branch**: main
**Commit**: ebe0920e89c28ee294dc3d7c7f1c53a2006dbf74

## Baseline Commands

| Command | Exists? | Exit code | Result | Failure type | Affected component | Notes |
|---|---|---|---|---|---|---|
| `git status --short` | YES | 0 | 5 modified files (see below) | N/A | N/A | Working tree has intentional unstaged changes |
| `python -m compileall L0 L1 L2 tools tests` | YES | 0 | Compiled all files | N/A | All | No errors |
| `make prove-seed` | YES | ? | ? | ? | L0 | Run needed |
| `make prove-l1` | YES | ? | ? | ? | L1 | Run needed |
| `make prove-l2` | YES | ? | ? | ? | L2 | Run needed |
| `make test-initiator` | YES | ? | ? | ? | Initiator | Run needed |
| `make test-evolve` | YES | 2 | 1 failed, 7482 passed | Implementation defect | config_precedence | One test failure: test_builtin_defaults |
| `make test-integration` | YES | 5 | No tests ran | Missing tests | tests/integration | Empty directory |
| `make test-system` | YES | 5 | No tests ran | Missing tests | tests/system | Empty directory |
| `make test-regression` | YES | ? | ? | ? | Regression | Run needed |
| `make test-all` | YES | ? | ? | ? | All | Run needed |
| `make prove-all` | YES | ? | ? | ? | All | Run needed |
| `make audit-structure` | YES | ? | ? | ? | Audit | Run needed |

## Working Tree Status
- `tools/agentx_evolve/providers/opencode_provider.py`: modified (intentional)
- `tools/agentx_evolve/runtime/chat_window.py`: modified (intentional)
- `ui/src/App.css`: modified (intentional)
- `ui/src/App.jsx`: modified (intentional)
- `ui/src/components/ActivityPanel.jsx`: modified (intentional)

## Key Findings
1. `tests/integration/` is empty (only `.gitkeep` and `README.md`)
2. `tests/system/` is empty (only `.gitkeep` and `README.md`)
3. `tests/smoke/` is empty (only `.gitkeep` and `README.md`)
4. `tools/agentx_evolve/docs/` has only `README.md` (all 14 required reports missing)
5. `tools/agentx_evolve/evidence/` is empty (only `.gitkeep`)
6. `tools/README.md` is MISSING
7. One test failure in `test_config_precedence.py::test_builtin_defaults`
