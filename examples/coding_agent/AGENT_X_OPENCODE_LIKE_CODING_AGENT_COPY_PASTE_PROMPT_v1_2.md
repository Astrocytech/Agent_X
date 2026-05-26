# Copy-Paste Prompt for Coding LLM: Agent_X OpenCode-like Plan-Only MVP

**Version:** `v1.2.0`

You are working inside the Agent_X repository.

Your task is to evolve Agent_X toward an OpenCode-like coding agent by implementing **only the first Agent_X-governed plan-only MVP slice**.

Use these two source documents as context:

```text
examples/evolutions/opencode_like_coding_agent.md
AGENT_X_OPENCODE_LIKE_CODING_AGENT_MVP_BUILD_GUIDE_v0_5.md
```

Also follow this TODO document:

```text
AGENT_X_OPENCODE_LIKE_CODING_AGENT_CODING_LLM_TODO_v1_2.md
```

## Non-negotiable scope

Do **not** implement full OpenCode.

Do **not** copy OpenCode source code.

Do **not** create runtime code under L2.

Do **not** modify L0.

Do **not** implement autonomous patching.

Do **not** implement GitHub writes.

Do **not** implement model-provider calls.

Do **not** run arbitrary shell.

Do **not** implement apply/edit behavior in the first slice.

The first MVP is **plan-only**.

## Implementation location

Create the implementation package only here:

```text
L1/implementation_packages/coding_agent_mvp/
```

## Required first working commands

The first successful implementation must support:

```bash
agentx-code inspect --repo <repo>
agentx-code plan --repo <repo> --task "<task>"
agentx-code validate-plan --plan <repo>/.agentx/plans/<plan_id>.yaml
```

Plan mode may write only:

```text
<repo>/.agentx/plans/
<repo>/.agentx/evidence/
```

Plan mode must modify no source files.

## Required package layout

Create:

```text
L1/implementation_packages/coding_agent_mvp/
  README.md
  pyproject.toml
  fic/
    fic_package_manifest.yaml
    FIC-MVP-001-repo-context-reader.md
    FIC-MVP-002-task-classifier.md
    FIC-MVP-003-file-candidate-selector.md
    FIC-MVP-004-patch-plan-builder.md
    FIC-MVP-006-permission-gate.md
    FIC-MVP-008-evidence-writer.md
    FIC-MVP-009-cli-entrypoint.md
  src/agentx_code/
    __init__.py
    cli.py
    models.py
    config_loader.py
    repo_context_reader.py
    task_classifier.py
    file_candidate_selector.py
    patch_plan_builder.py
    permission_gate.py
    evidence_writer.py
  tests/
  scripts/
    smoke_test_plan_only.py
  evidence/
    .gitkeep
```

## Required behavior

Implement:

```text
1. Safe config loading.
2. Repository-root canonicalization.
3. Deterministic bounded repository inspection.
4. Deterministic task classification.
5. Deterministic candidate-file selection.
6. Patch-plan generation with edit_authorized=false.
7. Permission gate blocking apply/check/network/GitHub/model operations.
8. Append-only evidence writing.
9. CLI for inspect, plan, validate-plan.
10. Tests proving plan mode does not write source files.
```



## Preflight before coding

Before creating code, inspect the repo and report blockers:

```text
[ ] L0/, L1/, L2/ exist.
[ ] No L0 files will be modified.
[ ] No executable code will be created under L2.
[ ] Source documents are present or supplied in context.
[ ] Existing L1/implementation_packages/coding_agent_mvp/ is inspected before edits.
```

If any preflight item fails, stop and return `BLOCKED`.

## Required additional proof

In addition to compileall, pytest, and smoke test, prove:

```text
[ ] forbidden import scan passes;
[ ] no-write test proves only .agentx/plans/ and .agentx/evidence/ changed in the target repo;
[ ] package audit manifest is written under L1/implementation_packages/coding_agent_mvp/evidence/;
[ ] release_evidence=false appears in generated plans, evidence, and package audit files.
```

## Strict implementation sequence

Implement in this order:

```text
1. FIC manifest and FIC stubs.
2. pyproject.toml and README.md.
3. models.py and config_loader.py.
4. repo_context_reader.py.
5. task_classifier.py.
6. file_candidate_selector.py.
7. patch_plan_builder.py.
8. permission_gate.py.
9. evidence_writer.py.
10. cli.py.
11. tests/fixtures and tests.
12. scripts/smoke_test_plan_only.py.
13. package evidence and audit manifest.
```

Stop before implementing apply, run-checks, model provider, GitHub integration, autonomous loops, or arbitrary shell execution.


## Required validation commands

Run from package root:

```bash
python -m compileall src
python -m pytest tests -q
python scripts/smoke_test_plan_only.py
# also run the forbidden import scan specified in the TODO
```

## Final response format

End with this exact machine-readable shape:

```yaml
agentx_coding_llm_result:
  status: "PLAN_ONLY_MVP_WORKING|BLOCKED|FAILED|PARTIAL|REJECTED_SCOPE_DRIFT"
  package_root: "L1/implementation_packages/coding_agent_mvp"
  implementation_phase: "plan-only"
  files_created: []
  files_modified: []
  commands_run: []
  commands_not_run: []
  tests_passed: true
  compile_passed: true
  smoke_test_passed: true
  source_files_modified_by_plan_mode: false
  unsafe_features_implemented: false
  release_evidence: false
  implementation_notes: []
  deferred_features: []
  evidence_paths: []
```

Do not give a prose-only final answer.

If you cannot complete the plan-only MVP safely, return `BLOCKED`, `FAILED`, or `PARTIAL`. Do not claim success unless the commands pass and the no-write test passes.


---

## v1.2 extra requirements

Also obey the v1.2 completion rules:

```text
[ ] Use YAML only for CLI stdout.
[ ] Every source file must have exactly one matching FIC stub.
[ ] Use the exact authorization vocabulary from the TODO: user task may authorize creating the L1 package, but target-repo edits remain unauthorized and release_evidence=false.
[ ] Run the copy-paste forbidden import/side-effect scan from the TODO.
[ ] Add idempotency tests: plan twice does not overwrite, validate-plan twice does not mutate, evidence is append-only.
[ ] If apply/run-checks/deferred modules exist, they must be blocked stubs with no side effects.
[ ] Record a clean verification pass in the audit manifest.
[ ] Scan README files for false claims such as OpenCode clone, OpenCode-compatible, autonomous coding agent, GitHub integration working, model-provider integration working, release-ready, or production-ready.
```

Do not report `PLAN_ONLY_MVP_WORKING` unless all v1.1 and v1.2 gates pass.
