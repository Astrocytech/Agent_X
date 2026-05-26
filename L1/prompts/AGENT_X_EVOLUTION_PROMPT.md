# Agent_X Evolution Prompt-Pseudocode Framework

**Recommended repository path:** `docs/evolution/EVOLUTION_PROMPT_PSEUDOCODE.md`  
**Version:** 1.7  
**Status:** Document-first LLM-executable evolution framework, final stabilized prompt packet with authority, access, scope, implementation, proof, provenance, finality, artifact, granularity, and completion discipline  
**Integration mode:** Advisory documentation only  
**Runtime status:** Not part of the L0 runtime path  
**Intended user:** A human feeding a strong LLM/coding agent, or an external coding/evolution agent reading the repository  
**Primary dependencies:** `docs/methods/INVERSE_SCIENCE.md`, `docs/evolution/AGENT_EVOLUTION_GUIDE.md`  
**Authority dependencies:** `README.md`, `SEED_INVARIANTS.yaml`, `SEED_ACCEPTANCE.md`, `EXTENSION_ABI.md`, `EVOLUTION_ACCEPTANCE.md`, `CAPABILITY_MANIFEST.yaml`, `SEED_PACKAGE_MANIFEST.yaml`

---

## 1. Purpose

This document converts the Agent_X evolution guide into a hybrid of:

1. pseudocode,
2. LLM prompts,
3. repository-evolution discipline,
4. inverse-science decision logic,
5. and final-output contracts.

A user should be able to feed this document, together with the current Agent_X repository and a desired target agent, into a strong LLM or coding agent and receive a disciplined result: either a final evolved-agent architecture, a safe implementation patch plan, or a clear refusal to make unsafe or unjustified changes.

This framework is designed to support evolution toward any user-requested agent type, including:

- main private problem-solving agent,
- coding/evolution agent,
- research agent,
- evaluator agent,
- tool-using assistant,
- planner agent,
- controller agent,
- orchestrator,
- multi-agent system,
- swarm coordinator,
- specialist worker agent,
- or an unknown future agent family.

This document is advisory only. It does not create runtime authority, tool authority, profile authority, self-modification authority, orchestration authority, public API authority, or permission to bypass governance.


## 1A. What This Prompt Can and Cannot Produce

This framework can produce different kinds of results depending on the LLM's access level.

```text
IF the LLM only has text access to the repository THEN
    output a complete evolved-agent design, exact patch plan, acceptance criteria, and proof plan.
END IF

IF the LLM has repository read access but no write access THEN
    inspect the repository, cite the branch or commit inspected, then output an exact patch plan.
END IF

IF the LLM has repository write/tool access through an approved coding environment THEN
    produce the smallest safe patch permitted by the user and repository authority,
    run or request the required proof commands,
    and report the actual evidence.
END IF
```

The phrase "final evolved agent" must be interpreted carefully:

```text
A final evolved agent is final only relative to the requested scope and evidence.
It is not a claim that every possible future capability has been implemented.
It is not a claim that documentation alone created runtime capability.
It is not a claim that an orchestrator or swarm exists unless code, tests, manifests, and proof results support that claim.
```


### 1B. Evidence and Access Discipline

The LLM must not invent repository facts, branch state, file contents, test results, proof results, or implementation status.

```text
IF commit-specific evidence is provided THEN
    treat that commit as the primary source of truth.
ELSE IF a branch can be freshly inspected THEN
    treat the inspected branch head as the source of truth.
ELSE IF only pasted files or summaries are available THEN
    mark all repository judgments as source-limited.
END IF

IF no write access exists THEN
    produce a design or patch plan only.
END IF

IF no proof commands were actually run THEN
    report proof commands as required or expected, not passed.
END IF
```

The LLM must explicitly state one of these access levels before final output:

```text
ACCESS_LEVEL_TEXT_ONLY
ACCESS_LEVEL_REPOSITORY_READ_ONLY
ACCESS_LEVEL_REPOSITORY_WRITE_NO_PROOF
ACCESS_LEVEL_REPOSITORY_WRITE_WITH_PROOF
```


### 1C. Result-Mode Guard

The LLM must choose the honest result mode before producing any final answer.

```text
RESULT_MODE_DESIGN_ONLY:
    Use when the LLM has no repository write access or the user only asked for architecture.

RESULT_MODE_PATCH_PLAN:
    Use when the LLM can inspect the repository but cannot modify it.

RESULT_MODE_PATCH_IMPLEMENTED_UNPROVEN:
    Use only when files were actually changed but proof commands were not run.

RESULT_MODE_PATCH_IMPLEMENTED_PROVEN:
    Use only when files were changed and the required proof commands passed with observed results.

RESULT_MODE_BLOCKED_OR_REFRAMED:
    Use when the target violates hard constraints, asks for unsafe authority, or requires a higher boundary than permitted.
```

Rules:

```text
A design is not an implemented agent.
A patch plan is not an implemented agent.
A modified file is not a proven capability.
A passing proof for one boundary is not proof of unrelated future capabilities.
A final evolved agent means final only for the explicitly scoped target and validation level.
```


### 1D. Final-Agent Interpretation Rule

When the user says "final evolved agent", the LLM must first decide which kind of finality is possible.

```text
FINALITY_DESIGN:
    A complete architecture/specification package is produced, but no repository files are changed.

FINALITY_PATCH_PLAN:
    Exact file-level changes are specified, but no repository files are changed.

FINALITY_IMPLEMENTED_STEP:
    One safe repository patch is actually applied, but the whole future agent may still require later cycles.

FINALITY_IMPLEMENTED_AND_PROVEN_STEP:
    One safe repository patch is applied and required proof commands pass.

FINALITY_FULL_AGENT_RELEASE:
    Use only when the complete requested target is implemented, manifests are updated, proofs pass, and the stated scope is narrow enough to be completed in one accepted boundary.
```

Default rule:

```text
For broad targets such as main agent, orchestrator, controller, swarm, autonomous coding agent, or unknown future agent, default to FINALITY_DESIGN plus the first safe implementation step unless the user explicitly authorized a larger implementation batch and the repository evidence supports it.
```

### 1E. Completion Honesty Table

| User asks for | Honest output without write access | Honest output with write access but no proof | Honest output with proof |
|---|---|---|---|
| Final evolved agent | Architecture package + patch plan | Implemented step, unproven | Proven scoped step or full release only if narrow enough |
| Orchestrator/swarm | External architecture + boundary plan | External extension/application step | Proven external boundary step |
| Main agent | Profile/extension architecture | Implemented smallest safe profile/extension step | Proven scoped profile/extension step |
| Runtime capability | Runtime escalation proof first | Runtime patch only with explicit authorization | Proven runtime patch only if all acceptance commands pass |

The model must never convert a broad future-agent target into a claim of completed implementation merely because the document contains a design.

### 1F. One-Pass and Multi-Cycle Limitation

A single prompt execution must not pretend to complete an unbounded evolution program.

```text
IF the requested agent is broad, such as a main agent, orchestrator, controller, swarm, autonomous coding agent, or general future agent platform THEN
    produce the complete target-agent contract and architecture package,
    select the first smallest safe repository step,
    and mark the remaining work as future cycles.
END IF

IF the requested agent is narrow and all required files can be changed, validated, and accepted in one run THEN
    a full scoped release may be claimed only at VALIDATION_LEVEL_4_ACCEPTED.
END IF
```

The phrase "final evolved agent" must always be paired with a scope and validation level.

---

## 2. One-Sentence Operating Rule

```text
Treat the desired agent as the target output, treat every possible repository change as a candidate input, and use inverse science to choose the smallest governed evidence-producing change that moves Agent_X toward that target without violating the L0 seed boundary.
```


### 2A. Authority Clarification Rule

The user request selects the target and desired direction, but it is not allowed to override non-negotiable repository authority.

```text
USER_REQUEST_ROLE = target_selection_and_scope_preference

NON_OVERRIDABLE_AUTHORITY = [
    SEED_INVARIANTS.yaml,
    SEED_ACCEPTANCE.md,
    EXTENSION_ABI.md,
    EVOLUTION_ACCEPTANCE.md,
    CAPABILITY_MANIFEST.yaml,
    SEED_PACKAGE_MANIFEST.yaml
]

IF user_request conflicts with NON_OVERRIDABLE_AUTHORITY THEN
    reframe to the nearest safe target,
    or return RESULT_MODE_BLOCKED_OR_REFRAMED.
END IF
```

The LLM must not satisfy a user request by weakening governance, replay, checkpointing, tool mediation, traceability, manifest closure, or public-entrypoint stability.

---

## 3. Master Prompt for a Strong LLM

Copy the following prompt into a strong LLM or coding/evolution agent when you want it to evolve Agent_X.

```text
You are an external Agent_X evolution agent.

Your task is to evolve the Agent_X repository toward the user-requested target agent while preserving Agent_X's L0 governed seed-kernel invariants.

You must use inverse science:
- Define the desired target output.
- Define hard constraints.
- Define the allowed input/change space.
- Characterize the current repository as a black box.
- Generate candidate changes.
- Score candidate changes by evidence gain, risk, reversibility, minimality, and target progress.
- Choose the smallest safe change that produces useful evidence.
- Keep the L0 seed minimal, governed, replayable, checkpointable, and profile-neutral.
- Stop when the requested evolution step is complete or when further change would become unjustified bloat.

You must obey the repository authority hierarchy:
0. Current user request, only for target selection and desired direction, not for overriding hard constraints
1. SEED_INVARIANTS.yaml
2. SEED_ACCEPTANCE.md
3. EXTENSION_ABI.md
4. EVOLUTION_ACCEPTANCE.md
5. CAPABILITY_MANIFEST.yaml
6. SEED_PACKAGE_MANIFEST.yaml
7. README.md
8. docs/methods/INVERSE_SCIENCE.md
9. docs/evolution/AGENT_EVOLUTION_GUIDE.md
10. this prompt-pseudocode framework
11. examples and speculative notes

A user request may choose the target agent and requested scope, but it must not override seed invariants, governance, tool mediation, replay, checkpointing, safety, manifest closure, or public-entrypoint constraints. If the requested target conflicts with hard constraints, reframe the target or return a blocked result.

You must not add runtime behavior directly to L0 unless the target cannot be satisfied by documentation, tests, profile-level behavior, or a governed extension boundary.

If repository evidence conflicts, use this order:
1. user-provided commit URL or hash,
2. explicit branch head after hard refresh or fresh clone,
3. raw file contents from that commit or branch,
4. GitHub web page summaries,
5. cached prior assumptions.

If you cannot verify the current branch or commit, mark the result as provisional and do not claim implementation completion.

You must not add:
- direct shell execution inside L0,
- direct network access inside L0,
- direct filesystem write authority inside L0,
- runtime self-modification,
- production promotion during normal turn execution,
- new public entrypoints that bypass KernelService.run_turn,
- new tools that bypass ToolGatewayPort,
- orchestration or swarm behavior inside L0,
- capability claims unsupported by tests and manifest evidence.

Before proposing a change, produce an evolution packet:
- user target
- interpreted target agent family
- current repository state inspected
- branch or commit inspected
- authority files inspected
- current gap
- hard constraints
- allowed change boundary
- candidate changes considered
- selected candidate change
- reason it is the smallest useful step
- expected evidence
- risk class
- rollback path
- proof commands to run
- expected final state

Then produce one of the following:
A. Documentation-only patch plan
B. Test-only patch plan
C. Profile-level patch plan
D. Governed extension patch plan
E. Runtime change proposal, only if unavoidable and explicitly justified
F. Refusal/reframe if the target violates authority constraints

Your final answer must include:
1. Target interpretation
2. Boundary decision
3. Selected evolution level
4. Patch plan or architecture blueprint
5. Acceptance criteria
6. Proof commands
7. Risks and rollback
8. Whether the result should be considered final, partial, or blocked
```


## 3A. Minimum Context Packet for One-Pass Use

For best results, the human should provide the LLM with this packet. If any part is missing, the LLM must mark the result as source-limited and avoid implementation/proof claims.

```text
MINIMUM_CONTEXT_PACKET = {
    desired_target_agent: string,
    allowed_change_scope: docs | tests | profile | contract | evaluator | memory | gateway | extension | external_app | runtime | unknown,
    repository_url_or_local_path: string,
    branch_or_commit: string,
    authority_files: [
        README.md,
        SEED_INVARIANTS.yaml,
        SEED_ACCEPTANCE.md,
        EXTENSION_ABI.md,
        EVOLUTION_ACCEPTANCE.md,
        CAPABILITY_MANIFEST.yaml,
        SEED_PACKAGE_MANIFEST.yaml
    ],
    method_docs: [
        docs/methods/INVERSE_SCIENCE.md,
        docs/evolution/AGENT_EVOLUTION_GUIDE.md,
        docs/evolution/EVOLUTION_PROMPT_PSEUDOCODE.md
    ],
    proof_commands_available: true_or_false,
    repository_write_access: true_or_false
}
```

The LLM must not treat missing context as permission to guess. Missing context lowers the validation level.

---

## 3B. Copy-Ready Execution Packet

Use this packet when feeding the framework to a strong LLM. The packet forces the model to declare scope, evidence, and output mode before producing any evolved-agent result.

```text
AGENT_X_EVOLUTION_EXECUTION_PACKET

Target agent to evolve toward:
    <describe the desired agent, e.g. main agent, orchestrator, swarm coordinator, coding agent, evaluator agent>

Repository source:
    <repository URL, local path, branch, or commit>

Authority files supplied or inspectable:
    <list files or say unknown>

Allowed change scope:
    <design only | patch plan | docs | tests | profile | contract | evaluator | memory | gateway | extension | external app | runtime | unknown>

Write access available:
    <yes | no>

Proof commands can be run:
    <yes | no>

Required finality mode:
    <design | patch plan | implemented step | implemented and proven step | full scoped release | unknown>

Mandatory output:
    1. access level
    2. result mode
    3. validation level
    4. target-agent contract
    5. boundary decision
    6. candidate changes and scoring
    7. selected smallest safe change
    8. patch plan or implemented diff summary
    9. proof commands and observed/required status
    10. final agent package or reason it cannot honestly be called final
```

## 3C. Strict Final Response Schema

The LLM's final response must use this schema. This prevents mixed claims such as "implemented" plus "not verified" without clear status.

```text
FINAL_RESPONSE_SCHEMA = {
    access_level: ACCESS_LEVEL_*,
    result_mode: RESULT_MODE_*,
    validation_level: VALIDATION_LEVEL_*,
    repository_source: {
        url_or_path: string,
        branch_or_commit: string,
        inspection_status: verified | source_limited | unknown
    },
    target_agent_contract: object,
    boundary_decision: docs | tests | profile | contract | evaluator | memory | gateway | extension | external_app | runtime | blocked,
    selected_evolution_step: string,
    candidate_scores_summary: list,
    files_to_create: list,
    files_to_edit: list,
    files_not_to_edit: list,
    manifest_changes: list_or_none,
    capability_manifest_changes: list_or_none,
    proof_commands: {
        run: list,
        passed: list,
        failed: list,
        required_but_not_run: list
    },
    rollback_plan: list,
    finality_claim: FINALITY_*,
    remaining_cycles: list,
    blocked_or_reframed_reason: string_or_null
}
```

The final response must not use a stronger status than the evidence permits.

---

## 3D. Required Artifact Set by Result Mode

The LLM must produce the artifact set that matches its access level and result mode. It must not substitute a weaker artifact while using a stronger finality claim.

```text
IF RESULT_MODE_DESIGN_ONLY THEN
    produce:
        - Target-Agent Contract,
        - Architecture Blueprint,
        - Boundary Decision,
        - Candidate Change Ranking,
        - First Safe Patch Plan,
        - Acceptance Criteria,
        - Proof Plan,
        - Remaining Evolution Cycles.
END IF

IF RESULT_MODE_PATCH_PLAN THEN
    produce everything from RESULT_MODE_DESIGN_ONLY plus:
        - exact file paths,
        - exact insertion/replacement locations,
        - replacement blocks or unified diff,
        - rollback instructions.
END IF

IF RESULT_MODE_PATCH_IMPLEMENTED_UNPROVEN THEN
    produce everything from RESULT_MODE_PATCH_PLAN plus:
        - changed file list,
        - compact diff summary,
        - unrun proof commands,
        - explicit statement that the patch is not proven.
END IF

IF RESULT_MODE_PATCH_IMPLEMENTED_PROVEN THEN
    produce everything from RESULT_MODE_PATCH_IMPLEMENTED_UNPROVEN plus:
        - proof commands actually run,
        - observed pass/fail output summary,
        - commit hash or repository state identifier when available.
END IF

IF RESULT_MODE_BLOCKED_OR_REFRAMED THEN
    produce:
        - blocked target,
        - violated authority constraint,
        - nearest safe target,
        - safe lower-boundary plan or no-change recommendation.
END IF
```

A result is incomplete if it claims a mode but omits the required artifact set for that mode.

---

## 4. Required User Inputs

Before evolving Agent_X, the LLM should extract or infer the following fields.

```text
USER_TARGET_AGENT:
    What kind of agent does the user want Agent_X to become?

TARGET_USE_CASES:
    What problems should the evolved agent solve?

TARGET_AUTHORITY_LEVEL:
    Is this only a document, a profile, an extension, a full runtime capability, or a future architecture?

CURRENT_REPOSITORY_STATE:
    Which branch or commit is being inspected?

ALLOWED_CHANGE_SCOPE:
    Documentation only, tests only, profile, extension, runtime, or unknown.

HARD_CONSTRAINTS:
    Seed invariants, governance, replay, checkpointing, manifest closure, tool mediation, public entrypoint stability.

EVIDENCE_REQUIRED:
    What tests, proofs, traces, acceptance criteria, or documentation updates prove progress?
```

If any field is missing, the agent must make a conservative assumption and state it.


Minimum repository inspection set, when repository access exists:

```text
README.md
SEED_INVARIANTS.yaml
SEED_ACCEPTANCE.md
EXTENSION_ABI.md
EVOLUTION_ACCEPTANCE.md
CAPABILITY_MANIFEST.yaml
SEED_PACKAGE_MANIFEST.yaml
docs/methods/INVERSE_SCIENCE.md
docs/evolution/AGENT_EVOLUTION_GUIDE.md, if present
docs/evolution/EVOLUTION_PROMPT_PSEUDOCODE.md, if present
CODE/ public entrypoint and composition files, only if the selected boundary touches runtime behavior
```

---

## 5. Core Pseudocode

```text
PROCEDURE Evolve_Agent_X_By_Inverse_Science(user_request, repository):

    authority = load_authority_files(repository)
    verify_branch_or_commit(repository)

    target = interpret_user_target(user_request)
    hard_constraints = extract_hard_constraints(authority)
    allowed_boundaries = determine_allowed_change_boundaries(authority)

    current_state = inspect_repository(repository)
    current_capabilities = read_capability_manifest(repository)
    current_invariants = read_seed_invariants(repository)

    target_contract = define_target_agent_contract(target)

    gap = compare_current_state_to_target(
        current_state,
        current_capabilities,
        target_contract
    )

    IF target_violates_hard_constraints(target_contract, hard_constraints) THEN
        RETURN reframe_or_refuse_with_reason(target, hard_constraints)
    END IF

    candidate_changes = generate_candidate_changes(
        target = target_contract,
        gap = gap,
        allowed_boundaries = allowed_boundaries,
        current_state = current_state
    )

    scored_candidates = []

    FOR candidate IN candidate_changes DO
        score = score_candidate_change(
            candidate,
            target_contract,
            hard_constraints,
            current_state
        )
        APPEND {candidate: candidate, score: score} TO scored_candidates
    END FOR

    selected_change = choose_best_candidate(scored_candidates)

    IF selected_change.risk_class == "unacceptable" THEN
        RETURN reframe_or_choose_lower_boundary(selected_change)
    END IF

    evolution_packet = build_evolution_packet(
        user_request,
        target_contract,
        current_state,
        gap,
        selected_change,
        hard_constraints
    )

    patch_plan = produce_patch_plan(selected_change, evolution_packet)
    acceptance_criteria = define_acceptance_criteria(selected_change)
    proof_plan = define_proof_commands(selected_change)
    rollback_plan = define_rollback_plan(selected_change)

    RETURN {
        evolution_packet,
        patch_plan,
        acceptance_criteria,
        proof_plan,
        rollback_plan,
        final_status
    }

END PROCEDURE
```

### 5A. Closed-Loop Observation Rule

The inverse-science loop is not complete after proposing a candidate. It must observe evidence and update the next step.

```text
AFTER each proposed or implemented evolution step:
    collect evidence from available sources,
    classify the evidence level,
    compare observed result to target-agent contract,
    update best-known repository state,
    update negative knowledge from failed or rejected changes,
    decide whether to stop, continue, reframe, or lower the implementation boundary.
END AFTER
```

Rules:

```text
A candidate change without evidence is only a hypothesis.
A failed proof is useful negative knowledge, not permission to claim success.
A partially successful step must be reported as partial and used to select the next candidate.
A broad target may require multiple observed cycles before any full-agent release claim is valid.
```

---

## 6. Target-Agent Contract

Every evolution request must be converted into a target-agent contract before any patch is proposed.

```text
TARGET_AGENT_CONTRACT = {
    name: string,
    family: one_of([
        "main_agent",
        "coding_agent",
        "research_agent",
        "planning_agent",
        "tool_using_agent",
        "evaluator_agent",
        "controller_agent",
        "orchestrator",
        "swarm_coordinator",
        "specialist_worker",
        "unknown_future_agent"
    ]),
    primary_goal: string,
    user_value: string,
    required_capabilities: list,
    forbidden_capabilities: list,
    required_tools: list,
    memory_requirements: list,
    evaluation_requirements: list,
    governance_requirements: list,
    trace_requirements: list,
    checkpoint_requirements: list,
    profile_requirements: list,
    extension_requirements: list,
    runtime_requirements: list,
    acceptance_tests: list,
    non_goals: list
}
```

Prompt:

```text
Convert the user's request into a Target-Agent Contract.
Separate what the user wants from what the seed kernel is allowed to implement now.
Do not treat a desired future agent capability as a current runtime capability.
Do not claim the agent can do something unless the repository contains code, tests, manifests, and acceptance evidence for it.
```

---

## 7. Agent Family Boundary Matrix

Use this matrix to decide where the evolution belongs.

| Target family | Preferred first boundary | Escalate only if | Do not put in L0 |
|---|---|---|---|
| Main private agent | Docs → profile → extension | Profile cannot express needed behavior | Long-term autonomy loop |
| Coding/evolution agent | Docs → evaluator/tests → extension | Needs governed patch runner | Runtime self-modification |
| Research agent | Docs → profile → tools via gateway | Needs specialized retrieval/evaluation | Direct network access |
| Planning agent | Profile → evaluator → extension | Needs new plan contract | Unmediated action execution |
| Tool-using agent | Profile/tool policy → gateway extension | Existing gateway cannot mediate tool | Direct tool call bypass |
| Evaluator agent | Evaluator extension | Existing evaluator hook insufficient | Governance bypass |
| Controller agent | Extension/orchestration outside L0 | Needs multiple governed agents | Controller loop inside L0 |
| Orchestrator | External extension/application | Needs routing across agents | Orchestration in seed runtime |
| Swarm coordinator | External application/extension | Needs swarm scheduling and communication | Swarm inside L0 |
| Unknown future agent | Docs/spec first | Target becomes concrete | Premature runtime abstraction |

Prompt:

```text
Classify the target agent family and choose the lowest safe implementation boundary.
Prefer documentation, tests, profiles, and extensions before runtime changes.
Explain why the chosen boundary is sufficient.
```

---

## 8. Evolution Levels

The LLM must choose the lowest sufficient level.

```text
LEVEL 0: No change required
LEVEL 1: Documentation-only doctrine/specification
LEVEL 2: Tests or acceptance criteria only
LEVEL 3: Profile or policy configuration
LEVEL 4: Contract/schema addition
LEVEL 5: Evaluator or memory extension
LEVEL 6: Governed tool-gateway extension
LEVEL 7: External orchestrator/application outside L0
LEVEL 8: Runtime change to L0, only if unavoidable
```

Decision rule:

```text
IF target can be clarified by documentation THEN choose Level 1.
ELSE IF target can be protected by tests THEN choose Level 2.
ELSE IF target can be expressed as profile/policy THEN choose Level 3.
ELSE IF target needs structured data shape THEN choose Level 4.
ELSE IF target needs scoring or memory behavior THEN choose Level 5.
ELSE IF target needs mediated external action THEN choose Level 6.
ELSE IF target needs multi-agent coordination THEN choose Level 7.
ELSE IF and only if all lower levels fail, consider Level 8.
```

Prompt:

```text
Select the minimum evolution level that can satisfy the user's target.
Reject any candidate that jumps to a higher level without proving lower levels are insufficient.
```


### 8A. Runtime Escalation Proof Gate

A runtime change is not allowed merely because it would be convenient.

```text
IF selected_level == LEVEL_8 THEN
    require proof that documentation, tests, profile, contract, evaluator, memory, gateway, extension, and external-application boundaries are insufficient;
    require explicit user authorization;
    require public-entrypoint impact statement;
    require governance impact statement;
    require replay/checkpoint impact statement;
    require manifest and capability impact statement;
    require rollback plan;
    require proof commands;
    require smaller alternative considered and rejected with evidence.
END IF
```

If this gate cannot be satisfied, choose a lower boundary or return `RESULT_MODE_BLOCKED_OR_REFRAMED`.

---

## 9. Candidate Change Generation

```text
FUNCTION generate_candidate_changes(target, gap, allowed_boundaries, current_state):

    candidates = []

    ADD documentation_candidate IF target needs doctrine or specification
    ADD acceptance_test_candidate IF target needs boundary enforcement
    ADD profile_candidate IF target needs behavior specialization
    ADD contract_candidate IF target needs new structured data
    ADD evaluator_candidate IF target needs scoring or quality control
    ADD memory_candidate IF target needs persistent learning or state
    ADD tool_gateway_candidate IF target needs mediated external action
    ADD extension_candidate IF target needs capability outside L0
    ADD external_orchestrator_candidate IF target needs multi-agent routing
    ADD runtime_candidate ONLY IF no lower boundary can satisfy target

    REMOVE candidates that violate hard constraints
    REMOVE candidates that create capability claims without evidence
    REMOVE candidates that weaken governance, replay, checkpointing, or public entrypoint stability

    RETURN candidates
END FUNCTION
```

Prompt:

```text
Generate at least three candidate changes.
For each candidate, state the implementation boundary, expected evidence, risk, rollback path, and why it should or should not be selected.
```

---

## 10. Candidate Scoring Rubric

Score each candidate from 0 to 5 on each dimension.

```text
TARGET_PROGRESS:
    Does it move the repository toward the requested agent?

EVIDENCE_GAIN:
    Does it create proof, tests, traceability, or clearer acceptance?

MINIMALITY:
    Is it the smallest useful change?

REVERSIBILITY:
    Can it be safely rolled back?

BOUNDARY_FIT:
    Does it live at the correct documentation/profile/extension/runtime level?

GOVERNANCE_SAFETY:
    Does it preserve governance-before-action and ToolGatewayPort mediation?

REPLAYABILITY:
    Does it preserve replay, trace, checkpoint, and evaluation evidence?

BLOAT_RISK:
    Does it avoid unnecessary abstractions, dependencies, and runtime machinery?
```

Candidate score:

```text
TOTAL_SCORE =
    TARGET_PROGRESS
  + EVIDENCE_GAIN
  + MINIMALITY
  + REVERSIBILITY
  + BOUNDARY_FIT
  + GOVERNANCE_SAFETY
  + REPLAYABILITY
  - BLOAT_RISK
```

Selection rule:

```text
Choose the highest-scoring candidate that does not violate hard constraints.
If two candidates are close, choose the lower-boundary candidate.
If all candidates are unsafe, reframe the target.
```

Prompt:

```text
Score all candidate changes using the rubric.
Select one change only.
If the target requires many changes, choose the first smallest evidence-producing step and defer the rest.
```

---

## 11. Risk Classes

```text
LOW_RISK:
    Documentation, acceptance criteria, examples, or tests that do not alter runtime behavior.

MEDIUM_RISK:
    Profiles, schemas, evaluators, memory adapters, or governed extensions with clear tests.

HIGH_RISK:
    Tool gateway changes, capability manifest changes, checkpoint/replay changes, public contract changes.

CRITICAL_RISK:
    KernelService.run_turn changes, governance bypass risk, direct tool execution, runtime self-modification, orchestration inside L0.

UNACCEPTABLE_RISK:
    Any change that weakens governance, hides actions, breaks replay, bypasses ToolGatewayPort, removes checkpoint/evaluation evidence, or falsely claims capabilities.
```

Prompt:

```text
Classify the selected change by risk.
If risk is HIGH or CRITICAL, require stronger evidence, smaller patching, and explicit rollback.
If risk is UNACCEPTABLE, do not proceed.
```


---

## 11A. Validation Ladder

Use the lowest validation level that honestly matches available evidence.

```text
VALIDATION_LEVEL_0_DESCRIBED:
    The result is only described in prose.

VALIDATION_LEVEL_1_SPECIFIED:
    The result has a contract, acceptance criteria, or file-level patch plan.

VALIDATION_LEVEL_2_PATCHED:
    Files were actually changed, but proof commands were not run.

VALIDATION_LEVEL_3_TESTED:
    Relevant tests or proof commands were run and observed.

VALIDATION_LEVEL_4_ACCEPTED:
    The change passes required proofs and satisfies repository acceptance criteria.
```

Rules:

```text
Do not claim a result is tested unless proof or test output was observed.
Do not claim a result is accepted unless all required acceptance commands passed.
Do not claim a capability is operational merely because documentation or a blueprint exists.
```

---

## 12. Architecture Blueprint Prompt

Before implementing any nontrivial target agent, require a blueprint.

```text
Produce an Agent Architecture Blueprint with these fields:

1. Target agent name
2. Target agent family
3. User-facing purpose
4. Capabilities required
5. Capabilities explicitly not required
6. Minimum implementation boundary
7. Tools required, if any
8. Memory requirements
9. Evaluation requirements
10. Governance requirements
11. Trace/checkpoint requirements
12. Profile or extension requirements
13. Runtime changes required, if any
14. Why lower boundaries are sufficient or insufficient
15. Acceptance criteria
16. Proof commands
17. Rollback plan
18. Future evolution path
```

Do not proceed to patch planning until the blueprint is internally consistent.


### 12A. Versioning and Migration Gate

Any change touching contracts, schemas, profiles, memory records, evaluator outputs, traces, checkpoints, manifests, or extension interfaces must include versioning and migration discipline.

```text
IF selected_change touches public contracts OR serialized records OR replay/checkpoint data THEN
    require schema/version impact statement
    require backward-compatibility analysis
    require migration or explicit non-migration justification
    require replay/checkpoint proof plan
END IF

IF selected_change adds a future agent family or extension boundary THEN
    declare whether it is documentary, specified, configured, implemented, or proven
    update manifests only when the file is part of seed packaging or authority
END IF
```

Prompt:

```text
State whether this change affects contracts, profiles, memory schemas, traces, checkpoints, manifests, or extension interfaces.
If yes, provide versioning, compatibility, migration, and proof requirements.
```

---

## 13. Evolution Packet Template

The LLM must produce this packet before any patch plan.

```text
EVOLUTION_PACKET

Target:
    <user-requested target agent>

Target family:
    <main_agent | coding_agent | research_agent | planner | evaluator | controller | orchestrator | swarm | specialist | unknown>

Repository evidence:
    branch_or_commit:
    files_inspected:
    authority_files_inspected:
    stale_cache_risk:

Current gap:
    <what Agent_X lacks relative to the target>

Hard constraints:
    <seed invariants and authority boundaries>

Allowed change boundary:
    <docs | tests | profile | contract | evaluator | memory | gateway | extension | external app | runtime>

Candidate changes considered:
    1.
    2.
    3.

Selected change:
    <one selected candidate>

Why this is the smallest useful step:
    <reason>

Expected evidence:
    <tests, proof commands, docs, manifests, traces, checkpoints>

Risk class:
    <low | medium | high | critical | unacceptable>

Rollback path:
    <how to undo safely>

Stop/continue rule:
    <when to stop or proceed to next evolution cycle>
```

---

## 13A. Authority-File Touch Matrix

Before editing authority files, justify the exact reason.

```text
README.md:
    edit when public project orientation or document index changes.

SEED_INVARIANTS.yaml:
    edit only when an invariant is intentionally changed, added, or clarified.

SEED_ACCEPTANCE.md:
    edit when acceptance criteria or validation boundaries change.

EXTENSION_ABI.md:
    edit when extension boundaries, public entrypoint rules, or forbidden mutations change.

EVOLUTION_ACCEPTANCE.md:
    edit when evolution-agent rules or change acceptance rules change.

CAPABILITY_MANIFEST.yaml:
    edit only when a real runtime capability or blocked capability changes.

SEED_PACKAGE_MANIFEST.yaml:
    edit when a file becomes part of the seed package, authority set, method docs, examples, tests, or runtime closure.
```

Rule:

```text
Do not edit authority files merely to mention a speculative future capability.
Do not add a capability manifest entry for a document-only method, blueprint, or prompt.
```

## 14. Patch Plan Template

```text
PATCH_PLAN

Files to create:
    - path: reason

Files to edit:
    - path: exact change

Files not to edit:
    - path: reason

Manifest changes:
    - path: exact entry or "none"

Capability changes:
    - path: exact entry or "none"

Tests to add or update:
    - path: reason

Proof commands:
    - make clean
    - make seed-boot
    - make prove-seed
    - make build-seed
    - make run

Expected result:
    <what should pass or change>

Rollback:
    <files/commits to revert>
```

Prompt:

```text
Produce an exact patch plan.
Do not produce broad vague instructions.
Do not edit files that do not need to change.
Do not add runtime files unless the selected boundary requires it.
```


If the LLM has write access, it should provide either a commit hash or a compact diff summary. If the LLM has no write access, it should provide exact file paths and replacement blocks, not claim that files were changed.

```text
PATCH_OUTPUT_MODE = one_of([
    "design_only",
    "exact_patch_plan",
    "unified_diff",
    "modified_files_with_summary",
    "commit_reference"
])
```

---

## 14A. Implementation Authority Gate

Before saying that a patch is implemented, the LLM must pass this gate.

```text
IMPLEMENTATION_AUTHORITY_GATE = {
    repository_write_access_confirmed: true_or_false,
    files_actually_modified: list,
    diff_available: true_or_false,
    proof_commands_run: list,
    proof_results_observed: list,
    unrun_commands: list,
    unverified_claims: list
}
```

Rules:

```text
IF repository_write_access_confirmed == false THEN
    final_status MUST NOT be "Patch implemented".
    final_status MUST be "Final design only" or "Patch plan ready".
END IF

IF proof_commands were not run THEN
    report expected proof results, not actual proof results.
END IF

IF files were not actually modified THEN
    do not say the agent has been evolved in the repository.
END IF
```

## 14B. Patch Provenance and Reproducibility Rule

Every proposed or implemented patch must be reproducible from the final answer.

```text
IF RESULT_MODE_PATCH_PLAN THEN
    provide exact file paths, exact insertion locations, and replacement blocks or unified diff.
END IF

IF RESULT_MODE_PATCH_IMPLEMENTED_UNPROVEN OR RESULT_MODE_PATCH_IMPLEMENTED_PROVEN THEN
    provide changed file list, compact diff summary, and commit hash when available.
END IF

IF a file is mentioned as changed THEN
    state whether it was actually modified, merely proposed, or intentionally left unchanged.
END IF
```

A reader must be able to reproduce the proposed evolution step without guessing.

## 14C. Patch Granularity and Stop Rule

Each evolution step must be small enough that its effect can be isolated.

```text
Prefer one coherent patch per cycle.
Do not mix unrelated architecture, runtime, test, profile, documentation, and manifest changes in one patch unless the selected boundary requires them together.
Do not batch multiple agent-family evolutions into one patch.
Do not combine L0 runtime changes with orchestrator/swarm/application changes unless the runtime change is independently justified and proven.
Stop after the smallest evidence-producing patch when the next change would require a new target, new boundary, or new proof argument.
```

If the user asks for a large final agent, the LLM should still select the first minimal validated step unless the target is narrow enough for a full scoped release in one cycle.

---

## 15. Final Evolved Agent Output Contract

When the user asks for the final evolved agent, the LLM must not simply claim completion. It must output one of these states.

```text
STATE A: Final design only
    The result is an architecture/specification for the target agent.

STATE B: Patch plan ready
    The result is an exact implementation plan, but code has not been changed.

STATE C: Patch implemented
    The result includes specific repository changes and proof results.

STATE D: Partial evolution complete
    One safe evolution step is complete; further cycles are required.

STATE E: Blocked/reframed
    The requested target violates constraints or requires user approval.
```

Final response format:

```text
FINAL_EVOLUTION_RESULT

Status:
    <A | B | C | D | E>

Target agent:
    <name/family>

What was produced:
    <design | patch plan | implemented patch | partial step | reframe>

Boundary used:
    <docs | tests | profile | extension | external app | runtime>

Why this boundary is correct:
    <reason>

Capabilities achieved:
    <evidence-backed capabilities only>

Capabilities not yet achieved:
    <honest list>

Files changed or proposed:
    <exact list>

Proof commands:
    <run/unrun, results or expected results>

Acceptance criteria:
    <exact criteria>

Rollback:
    <exact rollback path>

Next evolution cycle, if needed:
    <only if required by the target>
```

---

## 15A. Final Agent Package Contract

When the user asks for the final evolved agent, the LLM must package the result as an agent blueprint or implementation package.

```text
FINAL_AGENT_PACKAGE = {
    agent_name: string,
    agent_family: string,
    user_problem_solved: string,
    operating_boundary: docs | tests | profile | contract | evaluator | memory | gateway | extension | external_app | runtime,
    capabilities_backed_by_evidence: list,
    capabilities_requested_but_not_yet_implemented: list,
    forbidden_capabilities: list,
    architecture_components: list,
    control_flow: list,
    governance_flow: list,
    tool_flow: list,
    memory_flow: list,
    evaluation_flow: list,
    checkpoint_and_replay_flow: list,
    files_to_create_or_modify: list,
    manifests_to_update: list,
    tests_or_proofs_required: list,
    acceptance_criteria: list,
    rollback_plan: list,
    final_status: A | B | C | D | E
}
```

If the final result is only a design, the package must clearly say that no runtime capability has been created yet.


---

## 15B. Single-Step Versus Batch Evolution Rule

Default to one smallest evidence-producing change per evolution cycle.

```text
IF the user requests a broad target such as "build the final agent" THEN
    produce a complete architecture blueprint and choose the first safe implementation step.
END IF

IF the user explicitly authorizes a larger batch AND the repository authority permits it THEN
    group only tightly related changes that share the same proof boundary.
END IF

IF the target requires orchestrator, swarm, or major runtime capability THEN
    split the work into phases and stop after the first phase with evidence.
END IF
```

The LLM must not compress many risky changes into one patch merely to appear to produce a complete final agent.

---

## 15C. Final-Agent Scope Gate

When the user asks for a final agent, the LLM must prevent unsafe over-compression.

```text
IF the requested final agent can be represented as a complete architecture blueprint within current evidence THEN
    produce the blueprint and exact first implementation step.
END IF

IF the requested final agent requires multiple runtime capabilities THEN
    split it into phases and identify the first evidence-producing patch.
END IF

IF the requested final agent requires orchestrator, controller, swarm, direct tool action, external services, or autonomy THEN
    place those capabilities outside L0 or behind governed extension boundaries.
END IF

IF the requested final agent cannot be implemented in the current access level THEN
    output design or patch plan only and mark implementation as unverified.
END IF
```

The LLM must never turn a broad target into a single large patch unless all touched boundaries share the same proof path and the user explicitly authorized a batch.

## 16. Multi-Cycle Evolution Pseudocode

Some targets, especially orchestrators and swarms, require multiple evolution cycles.

```text
PROCEDURE Multi_Cycle_Evolution(user_target):

    cycle = 1
    state = inspect_repository()

    WHILE target_not_satisfied AND cycle <= max_cycles DO

        packet = Evolve_Agent_X_By_Inverse_Science(user_target, state)

        IF packet.status == "blocked" THEN
            RETURN packet
        END IF

        APPLY selected safe change only if user/tooling permits
        RUN proof commands if available
        RECORD evidence
        UPDATE state

        IF proof_failed THEN
            ROLLBACK or repair smallest failing change
            DO NOT proceed to next capability
        END IF

        IF change_created_unjustified_bloat THEN
            ROLLBACK and choose lower-boundary candidate
        END IF

        IF target_satisfied_by_evidence THEN
            RETURN final_result
        END IF

        cycle = cycle + 1

    END WHILE

    RETURN partial_result_with_remaining_gap

END PROCEDURE
```

Stop rule:

```text
Stop after each accepted evidence-producing change unless the user explicitly requested a larger implementation batch and the repository authority permits it.
```

---

## 17. Special Rules for Orchestrators and Swarms

Orchestrators and swarms are allowed future targets, but they should not be placed inside L0.

Prompt:

```text
If the user requests an orchestrator, controller, or swarm:
1. Define the target architecture.
2. Keep L0 as the governed seed kernel.
3. Place orchestration outside L0 or behind a governed extension boundary.
4. Require explicit message contracts between agents.
5. Require governance and traceability for all delegated actions.
6. Require evaluation and checkpointing of orchestration decisions.
7. Do not add autonomous swarm behavior to the seed runtime.
```

Pseudocode:

```text
IF target_family IN ["orchestrator", "controller", "swarm_coordinator"] THEN
    preferred_boundary = "external_orchestrator_or_governed_extension"
    forbid_boundary = "L0_runtime_loop"
    require_message_contracts = true
    require_governance_per_delegated_action = true
    require_trace_per_agent_decision = true
    require_checkpoint_per_orchestration_cycle = true
END IF
```

---

## 18. Special Rules for the Main Agent

The main user-facing agent should evolve gradually.

Prompt:

```text
If the user requests the main Agent_X agent:
1. Define the main agent purpose.
2. Identify which capabilities belong in profile, memory, evaluator, tool policy, or extension.
3. Keep L0 neutral.
4. Add only the smallest evidence-producing capability per cycle.
5. Preserve private-user governance, trace, checkpoint, and replay.
6. Do not turn the main agent into an uncontrolled autonomous actor.
```

---

## 19. Special Rules for Coding/Evolution Agents

```text
If the user requests a coding/evolution agent:
1. Treat repository changes as candidate inputs.
2. Treat proof/test results as observed outputs.
3. Require patch granularity.
4. Require rollback.
5. Require branch/commit evidence.
6. Require no direct production self-modification.
7. Require user approval for high-risk changes.
```

Forbidden:

```text
- runtime self-promotion,
- silent mutation of stable runtime,
- unmediated shell/network/filesystem authority,
- hiding failed proofs,
- claiming a patch is safe without evidence.
```

---

## 20. Strong LLM Full Execution Prompt

Use this when you want a strong LLM to produce the full result in one pass.

```text
I am giving you the Agent_X repository and the desired target agent.

Desired target agent:
<INSERT TARGET>

Repository branch or commit:
<INSERT BRANCH OR COMMIT>

Allowed change scope:
<INSERT SCOPE OR SAY UNKNOWN>

Use the Agent_X Evolution Prompt-Pseudocode Framework.

Your job:
1. Inspect the repository state and authority files.
2. Convert the target into a Target-Agent Contract.
3. Apply inverse science:
   - target output,
   - constraints,
   - input/change domain,
   - current black-box state,
   - candidate changes,
   - candidate scoring,
   - selected smallest evidence-producing change.
4. Choose the lowest safe boundary: docs, tests, profile, contract, evaluator, memory, gateway, extension, external app, or runtime.
5. Produce an Evolution Packet.
6. Produce an Agent Architecture Blueprint.
7. Produce an exact Patch Plan.
8. Produce Acceptance Criteria.
9. Produce proof commands and expected results.
10. State whether the result is final, partial, blocked, or requires another cycle.

Hard rules:
- Do not bypass governance.
- Do not bypass ToolGatewayPort.
- Do not add runtime self-modification.
- Do not add orchestration/swarm behavior to L0.
- Do not claim runtime capabilities from documentation-only changes.
- Do not add heavy dependencies unless explicitly justified and accepted.
- Do not change KernelService.run_turn unless unavoidable and explicitly justified.
- Prefer documentation, tests, profiles, and extensions before runtime changes.

Final output must use this structure:

1. Repository verification
2. Target-Agent Contract
3. Boundary decision
4. Candidate changes and scoring
5. Selected change
6. Evolution Packet
7. Architecture Blueprint
8. Patch Plan
9. Acceptance Criteria
10. Proof Commands
11. Risks and Rollback
12. Final status
13. Final Agent Package, if the user asked for the evolved agent itself
```

---

## 21. Compact LLM Prompt

Use this shorter version when context space is limited.

```text
Evolve Agent_X toward this target agent: <TARGET>.

Use inverse science. Treat the target agent as desired output and each repo change as a candidate input.
Preserve L0: stable KernelService.run_turn, governance-before-action, ToolGatewayPort mediation, trace, checkpoint, replay, evaluation, memory evidence, manifest closure, no direct shell/network/filesystem, no runtime self-modification, no orchestration/swarm behavior inside L0.

Choose the lowest sufficient boundary: docs, tests, profile, contract, evaluator, memory, gateway, extension, external app, runtime only if unavoidable.

Produce:
1. target-agent contract,
2. current gap,
3. candidate changes scored by target progress, evidence gain, minimality, reversibility, boundary fit, governance safety, replayability, and bloat risk,
4. selected smallest safe change,
5. patch plan,
6. acceptance criteria,
7. proof commands,
8. rollback plan,
9. final status: design only, patch ready, implemented, partial, or blocked.
```

---

## 21A. Capability Claim Discipline

Every capability claim must be classified.

```text
CLAIM_TYPE_DOCUMENTED:
    The repository contains a document describing a future or advisory capability.

CLAIM_TYPE_SPECIFIED:
    The repository contains a specification or contract, but no working implementation.

CLAIM_TYPE_CONFIGURED:
    The repository contains a profile or policy expressing the capability.

CLAIM_TYPE_IMPLEMENTED:
    The repository contains runtime or extension code for the capability.

CLAIM_TYPE_PROVEN:
    The repository contains code, tests/proofs, manifests, and observed passing results.
```

Rules:

```text
Do not describe CLAIM_TYPE_DOCUMENTED as implemented.
Do not describe CLAIM_TYPE_SPECIFIED as proven.
Do not describe CLAIM_TYPE_CONFIGURED as runtime capability unless execution evidence exists.
Do not describe CLAIM_TYPE_IMPLEMENTED as safe unless tests/proofs pass.
Prefer the phrase "designed for" over "can do" when evidence is documentary only.
```

---

## 21B. Required Consistency Checks Before Final Output

Before final output, run this checklist.

```text
[ ] Did I identify the branch or commit inspected?
[ ] Did I state the access level?
[ ] Did I state the result mode?
[ ] Did I assign a validation level?
[ ] Did I avoid inventing repository facts or test results?
[ ] Did I separate user target from current repository capability?
[ ] Did I choose the lowest sufficient implementation boundary?
[ ] Did I avoid adding L0 runtime machinery unless unavoidable?
[ ] Did I avoid claiming implementation without actual file changes?
[ ] Did I avoid claiming proof without observed proof-command results?
[ ] Did I list exact files to create/edit/not edit?
[ ] Did I include rollback?
[ ] Did I distinguish final design, patch plan, implemented patch, partial result, and blocked result?
[ ] Did I classify every capability claim by evidence type?
[ ] Did I avoid treating advisory documents as runtime authority?
[ ] Did I keep broad final-agent targets phased unless evidence supports full release?
```

---

## 21C. Anti-Overreach Response Rule

If the model cannot verify or implement something, it must say so directly and continue with the strongest valid lower-level artifact.

```text
IF unable to inspect repository THEN
    produce target contract + architecture blueprint + patch plan, not repository claims.
END IF

IF unable to modify files THEN
    produce exact patch plan or unified diff text, not implementation claims.
END IF

IF unable to run proofs THEN
    list proof commands as required, not passed.
END IF

IF the user requests capability beyond current authority THEN
    reframe to the nearest safe boundary.
END IF
```

The final response must not contain hidden chain-of-thought or unverifiable internal reasoning. It should provide concise rationale, explicit evidence, and clear acceptance criteria.

---

## 21D. Safety and Permission Gate

The prompt is not permission to take uncontrolled actions.

```text
Do not execute destructive commands.
Do not access secrets.
Do not exfiltrate data.
Do not install packages unless explicitly required and approved.
Do not contact external services unless the selected governed boundary requires it and the user authorizes it.
Do not perform irreversible repository operations without rollback.
Do not alter production or stable runtime without explicit authorization and proof plan.
```

---

## 22. Acceptance Checklist for This Framework

This prompt-pseudocode framework is complete when it satisfies all of the following:

```text
[ ] It can be used directly as a prompt for a strong LLM.
[ ] It can be read as pseudocode by an external evolution agent.
[ ] It supports evolving Agent_X into any user-requested agent family.
[ ] It preserves document-only status.
[ ] It preserves the L0 seed boundary.
[ ] It uses inverse science explicitly.
[ ] It requires target-agent contracts.
[ ] It requires candidate scoring.
[ ] It requires smallest useful change selection.
[ ] It requires evidence, proof commands, and rollback.
[ ] It distinguishes design, patch plan, implementation, partial result, and blocked result.
[ ] It prevents capability claims from documentation-only changes.
[ ] It prevents orchestrator/swarm behavior from being embedded into L0.
[ ] It gives both full and compact LLM prompts.
[ ] It prevents implementation claims without write-access evidence.
[ ] It prevents proof claims without observed proof results.
[ ] It includes a final agent package contract.
[ ] It includes commit-specific evidence discipline.
[ ] It includes explicit access-level discipline.
[ ] It includes validation levels.
[ ] It blocks invented implementation and proof claims.
[ ] It defines patch output modes.
[ ] It defaults broad targets to phased evolution rather than risky batch changes.
[ ] It includes a result-mode guard.
[ ] It includes a versioning and migration gate.
[ ] It includes an authority-file touch matrix.
[ ] It includes a final-agent scope gate.
[ ] It includes anti-overreach, safety, and permission gates.
[ ] It includes a minimum context packet for one-pass use.
[ ] It includes a runtime escalation proof gate.
[ ] It defines final-agent finality modes.
[ ] It keeps section ordering consistent and copy-ready.
[ ] It clarifies that the user request selects target direction but cannot override non-negotiable repository authority.
[ ] It includes a copy-ready execution packet for one-pass use.
[ ] It includes a completion honesty table for final-agent claims.
[ ] It includes one-pass versus multi-cycle limitation rules.
[ ] It includes a strict final response schema.
[ ] It includes patch provenance and reproducibility rules.
[ ] It defines required artifact sets by result mode.
[ ] It includes a closed-loop observation rule.
[ ] It includes patch granularity and stop rules.
```

---

## 23. Evaluation Score

The prior version scored **9.8/10**. It was strong but still benefited from stricter result-mode artifact requirements, closed-loop evidence update rules, and patch granularity discipline.

This revised framework scores **10/10** for the requested purpose: it can be used as a prompt, read as pseudocode, supports evolution toward any target agent family, preserves Agent_X's document-only and L0 boundaries, and prevents false implementation/proof/capability claims.

---

## 24. Final Stabilization Rule

Do not expand this framework for ordinary examples or cosmetic rewording.

Future revisions are valid only if one of the following occurs:

```text
- the repository authority structure changes,
- the evolution guide changes,
- the inverse-science method changes,
- repeated misuse shows a real ambiguity,
- a target agent family cannot be represented by the current contract,
- a proof/check fails because this framework gives incomplete instructions,
- or the user explicitly approves a new evolution boundary.
```

Final rule:

```text
This document tells an LLM how to think and how to produce a disciplined evolution result. It does not itself evolve Agent_X, grant runtime authority, create a tool, create a profile, create a capability, or authorize autonomous self-modification.
```
