# L0 Seed Acceptance Checklist

This repository is accepted as an L0 governed universal seed kernel only when every item below passes.

## A. Commands (run `make clean && make seed-boot && make prove-seed && make run`)

- [ ] `make clean` removes generated artifacts without error
- [ ] `make seed-boot` compiles all CODE Python files without syntax errors
- [ ] `make prove-seed` runs validate_seed_manifests.py followed by pytest tests/seed_l0 — all pass
- [ ] `make run` executes one governed turn through KernelService and returns a valid answer

## B. Static manifest invariants (proved by `make prove-seed` → validate_seed_manifests.py)

- [ ] Every file in SEED_PACKAGE_MANIFEST.yaml exists on disk
- [ ] Every CODE/ Python file is listed in SEED_PACKAGE_MANIFEST.yaml
- [ ] No manifest file imports a forbidden module (subprocess, socket, requests, httpx, urllib, paramiko, ftplib, docker, torch, transformers, openai, anthropic, selenium, playwright, pip, setuptools, poetry, conda)
- [ ] No manifest file imports from extensions/ or examples/
- [ ] No manifest file imports an undeclared top-level package
- [ ] CAPABILITY_MANIFEST.yaml has all required keys and no duplicate capability ids
- [ ] Every blocked capability in CAPABILITY_MANIFEST.yaml maps to a forbidden_l0_tool_class in SEED_INVARIANTS.yaml
- [ ] Only emit_answer.py exists in CODE/tool_gateway/seed_tools/
- [ ] list_seed_tool_names() returns exactly {"seed.emit_answer"}
- [ ] Every builtin profile has id and allowed_tools fields

## C. Runtime invariants (proved by `make prove-seed` → pytest tests/seed_l0)

- [ ] KernelService boots and returns health without model, GPU, or network
- [ ] One public entrypoint: KernelService.run_turn()
- [ ] run_turn accepts KernelTurnRequest and returns KernelTurnResponse
- [ ] Planner runs before governance
- [ ] Governance runs before tool gateway execution
- [ ] Unknown tool requests are denied by governance
- [ ] Every governed turn records trace, checkpoint, evaluation, and memory evidence
- [ ] Checkpoint contains goal, governance decision, and phase sequence
- [ ] Profile specialization does not expand the L0 tool surface beyond seed.emit_answer
- [ ] Blocked capabilities (production_self_modification, uncontrolled_network_access, direct_shell_execution) are absent from the tool registry
- [ ] Test files do not import from examples/extensions

## D. Phase order invariants (proved by test_12)

- [ ] All phases in SEED_INVARIANTS.yaml runtime_order.required_phase_order exist in code REQUIRED_PHASES
- [ ] governance_checked precedes tool_requested in phase order

## E. Evolution invariants (proved by EVOLUTION_ACCEPTANCE.md)

- [ ] Any change must preserve make seed-boot, make prove-seed, make build-seed
- [ ] No new L0 tool bypasses ToolGatewayPort
- [ ] No action executes before GovernancePort
- [ ] No model, GPU, network, secrets, Docker is required for seed boot

## F. Optional method documents

- [ ] `DOCUMENTS/INVERSE_SCIENCE.txt`, if present, is advisory documentation only.
- [ ] It is not imported by any `CODE/` runtime module.
- [ ] It adds no L0 tool, profile, dependency, public entrypoint, runtime phase, or required capability.
- [ ] It does not weaken governance, replay, checkpointing, traceability, profile isolation, manifest closure, or the single ToolGatewayPort execution path.
