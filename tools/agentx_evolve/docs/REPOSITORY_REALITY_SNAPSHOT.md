# Repository Reality Snapshot

**Generated**: 2026-06-09
**Repository**: https://github.com/Astrocytech/Agent_X
**Branch**: main
**Commit**: ebe0920e89c28ee294dc3d7c7f1c53a2006dbf74
**Python**: 3.12.3
**OS**: Linux x86_64

## 1. Commit and Branch

- **Branch**: `main`
- **Commit**: `ebe0920e` ("misc fixes and improvements")
- **Working tree**: 5 files modified (unstaged)
  - `tools/agentx_evolve/providers/opencode_provider.py`
  - `tools/agentx_evolve/runtime/chat_window.py`
  - `ui/src/App.css`
  - `ui/src/App.jsx`
  - `ui/src/components/ActivityPanel.jsx`

## 2. Relevant File Tree Summary

| Area | Files | Description |
|---|---|---|
| `L0/` | ~60+ source, ~20 tests | Governed seed kernel (protected) |
| `L1/` | ~100+ modules, 273 tests | Evolution controller / governance |
| `L2/` | ~40+ modules, 38 tests | Specialization profile layer |
| `tools/agentx_initiator/` | ~50 modules, 205 tests | Initiator tool |
| `tools/agentx_evolve/` | ~400+ modules, 805 test files | Self-evolution system |
| `tools/agentx_evolve/schemas/` | 478 JSON schemas | Structured data definitions |
| `tests/integration/` | 0 test files (placeholder only) | EMPTY |
| `tests/system/` | 0 test files (placeholder only) | EMPTY |
| `tests/smoke/` | 0 test files (placeholder only) | EMPTY |
| `tests/regression/` | 3 test files | Format guard tests |
| **Total** | ~6,233 tracked files | |

## 3. Makefile Target Inventory

| Target | Actual commands | Proves |
|---|---|---|
| `install` | `pip3 install -r requirements/seed.txt` | Dependency install |
| `seed-boot` | compileall + run prove_seed_boot.py | Seed boot |
| `prove-seed` | compileall + validate_seed_manifests.py + pytest L0/tests/seed_l0 | Seed correctness |
| `prove-l1` | compileall + pytest L1/tests + L1.validators.validate_all | L1 correctness |
| `prove-l2` | bootstrap_validate_l2_scaffold.py + pytest L2/tests | L2 correctness |
| `prove-format` | pytest tests/regression/ | Formatting |
| `prove-all` | audit-structure + prove-seed + prove-l1 + prove-l2 + prove-format | Full prove |
| `audit-structure` | tools/repo_audit/audit_repository_structure.py | Structure audit |
| `prove-organization` | audit-structure + collect-only + find + git status | Org acceptance |
| `test-smoke` | pytest tests/smoke | EMPTY |
| `test-l0` | alias for prove-seed | L0 tests |
| `test-l1` | alias for prove-l1 | L1 tests |
| `test-l2` | alias for prove-l2 | L2 tests |
| `test-initiator` | pytest tools/agentx_initiator/tests | Initiator tests |
| `test-evolve` | pytest tools/agentx_evolve/tests | Evolve tests |
| `test-integration` | pytest tests/integration | EMPTY |
| `test-system` | pytest tests/system | EMPTY |
| `test-regression` | pytest tests/regression | Format guard |
| `test-live` | pytest -m live | Live provider tests |
| `test-all` | pytest across all test dirs | BUG: ModuleNotFoundError |
| `prove-hygiene` | ruff + mypy + pip-audit | Code hygiene |
| `run` | KernelService.run_turn() | One seed turn |
| `build-seed` | build_seed_package.py | Build seed |
| `clean` | rm -rf cache + pycache | Clean artifacts |

## 4. CLI Command Inventory

From `tools/agentx_evolve/__main__.py`:

| Command | Description | Has help |
|---|---|---|
| `version` | Show version | Yes |
| `review <session_id>` | Review an implementation session | Yes |
| `approve <session_id>` | Approve a session | Yes |
| `reject <session_id>` | Reject a session | Yes |
| `explain <session_id>` | Show session details | Yes |
| `chat [options]` | Chat with LLM provider | Yes (detailed) |
| `self-upgrade [options]` | Self-upgrade plan or apply | Yes |
| `init-agent [options]` | Initialize a new agent | Yes |
| `evolve-agent [options]` | Evolve an external agent | Yes |
| `help` / `--help` / `-h` | Show help | Yes |

## 5. Schema/Validator Inventory

| Component | Schema files | Validator test files |
|---|---|---|
| `backup/` | 17 schemas | 2 validators |
| `context/` | 15 schemas | 2 validators |
| `docs_sync/` | 30 schemas | 2 validators |
| `evaluation/` | 25 schemas | 2 validators |
| `recovery/` | 6 schemas | 0 validators |
| `final_acceptance/` | 15 schemas | 1 validator + built-in |
| `git/` | 25 schemas | 2 validators |
| `patch/` | 10 schemas | 0 module validators |
| `human_review/` | 20 schemas | 1 validator |
| `llm_worker/` | 20 schemas | 2 validators |
| `model_runtime/` | 15 schemas | 1 validator |
| `learning/` | 10 schemas | 1 validator |
| `model_adapter/` | 15 schemas | 1 validator |
| `monitoring/` | 15 schemas | 1 validator |
| `packaging/` | 15 schemas | 1 validator |
| `policy/` | 12 schemas | 1 validator |
| `promotion/` | 15 schemas | 2 validators |
| `prompt/` | 20 schemas | 1 validator |
| `security/` | 10 schemas | 0 module validators |
| `orchestrator/` | 40 schemas | 2 validators |
| `scheduler/` | 25 schemas | 1 validator |
| `tool_mcp/` | 20 schemas | 1 validator |
| Root | 10+ schemas | 0 validators |
| **Total** | **~478 schemas** | **30 validator files** |

## 6. Existing Report Inventory

| Report path | Status |
|---|---|
| `tools/agentx_evolve/docs/README.md` | Exists (minimal) |
| `tools/agentx_evolve/docs/REPOSITORY_REALITY_SNAPSHOT.md` | Created by this pass |
| `tools/agentx_evolve/docs/BASELINE_DOCUMENT_ALIGNMENT_AUDIT.md` | Created by this pass |
| `tools/agentx_evolve/docs/BASELINE_SOURCE_HASH_MANIFEST.json` | Created by this pass |
| All other required reports under `tools/agentx_evolve/docs/` | MISSING |

Agent_X Evolve `.agentx-init/` runtime artifacts exist:
- `tools/agentx_evolve/.agentx-init/docs_sync/` — contains drift/broken-link/staleness reports
- `tools/agentx_evolve/.agentx-init/evaluation/` — empty

## 7. Test Inventory

| Test directory | Test files | Status | Notes |
|---|---|---|---|
| `tools/agentx_evolve/tests/` | 805 test files | **7482 passed, 1 failed** | Mostly comprehensive |
| `tools/agentx_initiator/tests/` | ~25 test files | **205 passed** | Complete |
| `L0/tests/seed_l0/` | ~5 test files | **52 passed** | Core seed tests |
| `L1/tests/` | ~20 test files | **273 passed** | L1 layer tests |
| `L2/tests/` | ~10 test files | **38 passed** | L2 layer tests |
| `tests/regression/` | 3 test files | **7 passed, 16 failed** | Format guard tests |
| `tests/integration/` | 0 | **EMPTY** | Placeholder only |
| `tests/system/` | 0 | **EMPTY** | Placeholder only |
| `tests/smoke/` | 0 | **EMPTY** | Placeholder only |

## 8. Placeholder/Scaffold Indicators

| Path | Indicator |
|---|---|
| `tests/integration/` | Only `.gitkeep` + `README.md` — no test files |
| `tests/system/` | Only `.gitkeep` + `README.md` — no test files |
| `tests/smoke/` | Only `.gitkeep` + `README.md` — no test files |
| `tools/agentx_evolve/evidence/` | Only `.gitkeep` — no evidence artifacts |
| `L2/bootstrap/` | Empty directory |
| `tools/agentx_evolve/docs/` | Only `README.md` — 14 required reports missing |
| `tools/README.md` | MISSING file |

## 9. Runtime Artifact Locations Found

| Location | Content | Canonical? |
|---|---|---|
| `.agentx-init/` (repo root) | Runtime evidence | YES (per ARCHITECTURE.md) |
| `.local/runtime/` | Local runtime state | YES |
| `L0/.local/runtime/checkpoints/` | ~700+ seed checkpoints | L0 internal |
| `tools/agentx_evolve/.agentx-init/` | Docs sync reports | NON-CANONICAL (nesting) |
| `.pytest_cache/`, `__pycache__/` (various) | Caches | Generated, excluded |

## 10. Initial Risk Notes

1. **Empty integration/system tests** — `make test-integration` and `make test-system` fail with "no tests ran"
2. **Missing reports** — `tools/agentx_evolve/docs/` lacks all 14 required reports for document-complete status
3. **Missing evidence artifacts** — `tools/agentx_evolve/evidence/` is empty
4. **`make test-all` broken** — ModuleNotFoundError for core_kernel due to missing PYTHONPATH
5. **`make test-regression` failing** — 16 of 23 regression tests fail (formatting/line-count checks)
6. **`make audit-structure` failing** — 1 issue: REV document outside archive
7. **`make prove-l1` WARNING** — release_evidence is false
8. **1 evolve test failing** — `test_config_precedence.py::test_builtin_defaults`
9. **`tools/README.md` missing** — noted in governance doc reading list
10. **Nested `.agentx-init/`** — under `tools/agentx_evolve/` is non-canonical per ARCHITECTURE.md
