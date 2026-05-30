# Agent_X OpenCode-like Coding Agent Status README

**Document ID:** `AGENT-X-OPENCODE-LIKE-STATUS-README-001`  
**Version:** `v1.1.0`  
**Status:** `plain-english-status-readme`  
**Purpose:** Explain, in plain English, what the current OpenCode-like Agent_X documents allow us to build, what the first agent can do, what it cannot do yet, and what is still missing for a full OpenCode-like coding agent.

---

## 1. Plain-English Summary

Agent_X is not becoming OpenCode directly.

The current goal is to evolve Agent_X toward an **OpenCode-like coding assistant**, but in the Agent_X way: controlled, documented, evidence-producing, and governed through L1.

The current document set is enough to build the **first safe version** of that coding assistant.

That first version is not a full coding agent yet. It is a **planning agent**.

In simple terms:

```text
You give it a code task and a repo path.
It looks at the repo.
It decides what kind of task this is.
It identifies likely relevant files.
It writes a plan.
It writes evidence.
It does not edit the repo.
```

So the first completed agent will be:

```text
A safe repo-aware coding planner.
```

It will not yet be:

```text
A full code-editing agent.
A full OpenCode clone.
An autonomous programming agent.
A GitHub PR agent.
A model-provider coding agent.
```

---

## 2. What the Current Four Documents Are For

The current OpenCode-like document set has four files.

```text
1. AGENT_X_EXAMPLE_OPENCODE_LIKE_CODING_AGENT_EVOLUTION_v0_5.md
2. AGENT_X_OPENCODE_LIKE_CODING_AGENT_MVP_BUILD_GUIDE_v0_5.md
3. AGENT_X_OPENCODE_LIKE_CODING_AGENT_CODING_LLM_TODO_v1_2.md
4. AGENT_X_OPENCODE_LIKE_CODING_AGENT_COPY_PASTE_PROMPT_v1_2.md
```

Each file has a different role.

### 2.1 Evolution example

This file explains the idea.

It says how Agent_X could grow toward an OpenCode-like coding agent without copying OpenCode and without pretending to be OpenCode.

It is an example document. It is not implementation authority.

Plain-English meaning:

```text
This explains the direction.
It does not build the agent by itself.
```

### 2.2 MVP build guide

This file explains the first useful version that can be built.

It defines the first working version as **plan-only**.

Plain-English meaning:

```text
This explains what the first working coding-agent package should do.
```

### 2.3 Coding-LLM TODO

This is the main instruction file for a coding LLM.

It tells the coding model exactly what files to create, where to put them, what tests to write, what commands to run, what to block, and what final result to return.

Plain-English meaning:

```text
This is the detailed build checklist for the coding LLM.
```

### 2.4 Copy-paste prompt

This is the shorter prompt that can be pasted into a coding model.

It tells the model to use the other documents and implement only the first plan-only MVP.

Plain-English meaning:

```text
This is the short instruction wrapper to start the coding task.
```

---

## 3. What Can Be Built Now

Using the four files, a coding LLM should be able to build the first Agent_X coding-agent MVP here:

```text
L1/implementation_packages/coding_agent_mvp/
```

The package should provide these commands:

```bash
agentx-code inspect --repo <repo>
agentx-code plan --repo <repo> --task "<task>"
agentx-code validate-plan --plan <repo>/.agentx/plans/<plan_id>.yaml
```

### 3.1 `inspect`

This command looks at the repository safely.

It should report things such as:

```text
- where the repo is;
- how many files were scanned;
- which files were skipped;
- what languages seem to be present;
- whether test files exist;
- whether the repo has risky or secret-like files.
```

It should not change anything.

### 3.2 `plan`

This command takes a user task and creates a coding plan.

Example:

```bash
agentx-code plan --repo /home/user/my_project --task "Update README wording"
```

The agent should then produce something like:

```text
Task type: documentation update
Likely file: README.md
Risk level: low
Plan: review README.md and propose a wording change later
Approval required: true
Editing authorized: false
```

It writes the plan under:

```text
<target_repo>/.agentx/plans/
```

It writes evidence under:

```text
<target_repo>/.agentx/evidence/
```

It must not edit the actual source files.

### 3.3 `validate-plan`

This command checks whether a generated plan is structurally valid.

It should confirm that:

```text
- the plan file has the expected fields;
- edit_authorized is false;
- release_evidence is false;
- selected file paths are safe;
- no forbidden operation is authorized.
```

---

## 4. What the First Agent Can Do Exactly

If the current documents are followed correctly, the first completed agent can do this:

```text
[ ] Inspect a repository.
[ ] Identify files, languages, tests, and risky paths.
[ ] Classify a coding task.
[ ] Detect unsafe requests such as deleting files or exposing secrets.
[ ] Choose likely relevant files.
[ ] Create a patch plan.
[ ] Write a YAML plan file.
[ ] Write an evidence record.
[ ] Validate its own plan file.
[ ] Prove that plan mode did not modify source files.
[ ] Block future unsafe features until they are separately implemented.
```

A more human description:

```text
It can help decide what should probably be changed.
It can help identify where the work is likely located.
It can record why it made that decision.
It can prepare the next step for a future editing agent.
```

It is useful as a first step before code editing because it creates a safe planning layer.

---

## 5. What the First Agent Cannot Do Yet

The first completed agent cannot do these things:

```text
[ ] It cannot edit files.
[ ] It cannot apply patches.
[ ] It cannot run tests.
[ ] It cannot run arbitrary shell commands.
[ ] It cannot call OpenAI, Anthropic, Claude, Gemini, local LLMs, or any model provider.
[ ] It cannot create Git commits.
[ ] It cannot push branches.
[ ] It cannot open GitHub pull requests.
[ ] It cannot comment on GitHub issues.
[ ] It cannot operate autonomously.
[ ] It cannot act as a full OpenCode clone.
```

This is intentional.

The first agent must stay safe and simple. It plans work, but it does not perform the work yet.

---

## 6. What Files the First Agent May Write

When the agent is run against a target repository, it may write only generated Agent_X files under `.agentx/`.

Allowed generated paths:

```text
<target_repo>/.agentx/plans/
<target_repo>/.agentx/evidence/
```

It may also use temporary files internally when writing safely, but those temporary files must not become source-code changes.

It must not silently modify:

```text
- source files;
- tests;
- README files;
- docs;
- config files;
- CI files;
- Git files;
- dependency files;
- external repositories.
```

Plain-English rule:

```text
The first agent may write its own notes and evidence.
It may not change the project itself.
```

---

## 7. Why This Is Still Useful

Even though it does not edit code yet, the plan-only agent is useful because it creates the safe foundation for a later coding agent.

It can answer questions such as:

```text
What kind of task is this?
Which files are probably relevant?
Is this task risky?
Does this request look unsafe?
What should the next coding step be?
What evidence should be recorded?
What must remain blocked?
```

This gives Agent_X a controlled path from:

```text
unstructured user coding request
```

to:

```text
reviewable, bounded, evidence-producing coding plan
```

That is the correct first step before allowing the system to edit files.

---

## 8. What the Coding LLM Should Create

The coding LLM should create this package:

```text
L1/implementation_packages/coding_agent_mvp/
  README.md
  pyproject.toml
  fic/
  src/agentx_code/
  tests/
  scripts/
  evidence/
```

Core source files should include:

```text
src/agentx_code/cli.py
src/agentx_code/models.py
src/agentx_code/config_loader.py
src/agentx_code/repo_context_reader.py
src/agentx_code/task_classifier.py
src/agentx_code/file_candidate_selector.py
src/agentx_code/patch_plan_builder.py
src/agentx_code/permission_gate.py
src/agentx_code/evidence_writer.py
```

Core tests should prove:

```text
- inspect works;
- plan works;
- validate-plan works;
- unsafe tasks are blocked;
- source files are not modified;
- generated evidence is written;
- forbidden imports are absent;
- deferred features are blocked.
```

---

## 9. What Must Be Proven Before Calling It Working

The first MVP is working only if these commands pass from the package root:

```bash
python -m compileall src
python -m pytest tests -q
python scripts/smoke_test_plan_only.py
```

It must also pass the forbidden import and side-effect scan from the coding-LLM TODO.

The final coding LLM result may say:

```text
PLAN_ONLY_MVP_WORKING
```

only if all of this is true:

```text
[ ] inspect command works.
[ ] plan command works.
[ ] validate-plan command works.
[ ] tests pass.
[ ] smoke test passes.
[ ] no-write proof passes.
[ ] forbidden import scan passes.
[ ] no L0 files were modified.
[ ] no executable code was created under L2.
[ ] no OpenCode source was copied.
[ ] no GitHub/model/shell/apply behavior was implemented.
[ ] release_evidence remains false.
```

---

## 10. What Remains Missing for a Full OpenCode-like Agent

The current documents do not yet cover a full OpenCode-like agent.

After the plan-only MVP works, later stages would be needed.

### Stage 1: Diff-only mode

The agent can generate a proposed diff, but still does not apply it.

Missing documents/work:

```text
- diff builder FIC;
- diff validation rules;
- review packet format;
- tests proving no files are edited.
```

### Stage 2: Apply-with-approval mode

The agent can edit declared files after explicit approval.

Missing documents/work:

```text
- bounded file editor FIC;
- approval gate;
- atomic file write rules;
- rollback or backup policy;
- edit evidence schema;
- tests proving only allowed files change.
```

### Stage 3: Check runner

The agent can run approved validation commands.

Missing documents/work:

```text
- check runner FIC;
- command whitelist;
- timeout rules;
- output capture rules;
- no arbitrary shell rule;
- command evidence schema.
```

### Stage 4: Git workflow

The agent can safely read Git state and later create branches or commits only with approval.

Missing documents/work:

```text
- Git status reader;
- branch creation policy;
- commit policy;
- dirty worktree policy;
- no-push-by-default rule.
```

### Stage 5: Model-provider integration

The agent can use an LLM to propose changes.

Missing documents/work:

```text
- model provider adapter;
- prompt privacy policy;
- secret redaction;
- model output validator;
- provider configuration;
- no hidden provider fallback rule.
```

### Stage 6: GitHub integration

The agent can interact with GitHub issues or pull requests.

Missing documents/work:

```text
- GitHub issue reader;
- GitHub PR builder;
- token permission policy;
- comment-writing rules;
- branch/PR evidence;
- no automatic PR writes without approval.
```

### Stage 7: Interactive interface

The agent gets a richer user interface.

Missing documents/work:

```text
- TUI or CLI interaction design;
- approval prompts;
- diff viewer;
- session navigation;
- error display rules.
```

### Stage 8: Session history and memory

The agent remembers previous work safely.

Missing documents/work:

```text
- session storage policy;
- project memory policy;
- context compaction;
- privacy boundaries;
- retention and deletion rules.
```

### Stage 9: Plugin/tool system

The agent can use tools beyond the built-in package.

Missing documents/work:

```text
- tool registry;
- plugin validation;
- permission model;
- sandbox policy;
- audit logs;
- tool disable/rollback rules.
```

### Stage 10: Release-grade product

The agent becomes a packaged product.

Missing documents/work:

```text
- installer;
- release process;
- versioning;
- upgrade policy;
- integration tests;
- security tests;
- user documentation;
- release notes.
```

---

## 11. What “OpenCode-like” Means Here

In this repository, “OpenCode-like” means:

```text
A repo-aware coding assistant that can eventually inspect code, plan changes, propose diffs, run approved checks, and support Git/GitHub workflows.
```

It does not mean:

```text
copying OpenCode;
forking OpenCode;
claiming compatibility with OpenCode;
using OpenCode source code;
matching every OpenCode feature immediately.
```

Agent_X should become its own governed coding agent.

---

## 12. Recommended Current State

Recommended current interpretation:

```text
The documents are complete enough to ask a coding LLM to build the first plan-only MVP.
```

Recommended next action:

```text
Give the coding LLM the copy-paste prompt plus the other three documents as context.
Ask it to build only the plan-only MVP.
Require tests, smoke test, no-write proof, forbidden import scan, and package evidence.
```

Do not ask it to:

```text
make full OpenCode;
edit files automatically;
add model providers;
add GitHub integration;
add autonomous behavior;
create runtime under L2.
```

---

## 13. Simple Status Table

| Area | Current status | Plain-English meaning |
|---|---|---|
| Evolution direction | Ready | We know what kind of agent we want eventually. |
| Plan-only MVP guide | Ready | We know what the first safe working version should do. |
| Coding LLM TODO | Ready | We can give a coding model exact build instructions. |
| Copy-paste prompt | Ready | We have a short prompt to start the coding task. |
| Working agent code | Not built yet | The actual package still needs to be implemented. |
| File editing | Not allowed yet | The first agent must not edit source files. |
| Test running | Not allowed yet | Check runner comes later. |
| Model calls | Not allowed yet | LLM provider integration comes later. |
| GitHub integration | Not allowed yet | GitHub support comes later. |
| Full OpenCode-like product | Not yet | This requires many later stages. |

---

## 14. Final Plain-English Answer

If we complete the agent described by the current documents, we will have:

```text
A safe Agent_X coding planner that can inspect a repo and write a plan.
```

It will be able to tell the user:

```text
This looks like a documentation task.
These files are probably relevant.
This is the proposed plan.
This is the risk level.
Editing is not authorized yet.
Here is the evidence record.
```

It will not yet be able to say:

```text
I edited the file.
I ran the tests.
I opened a pull request.
I used an LLM to generate a patch.
I committed the code.
```

That is the correct first step.

The first agent is the foundation. The full OpenCode-like agent comes later, one governed capability at a time.
