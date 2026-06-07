Status: ACTIVE
Owner: L1
Applies to: governance standards
Supersedes: EQC.md
Last reviewed: 2026-06-07

# EquationCode (EQC) v1.1

**EquationCode (EQC)** is a disciplined specification format where:

- **Mathematics is modularized into named, versioned operators**, and  
- **Algorithm control flow is explicit, minimal, and implementable**.

EQC removes “hidden semantics” that appear when math and pseudocode are split, which causes reproducibility issues, comparability failures, and implementation drift. EQC is designed so algorithms can be **refactored, simplified, optimized, and upgraded** by changing operators and manifests, while keeping behavior **traceable, testable, and comparable**.

---

## Why EQC exists

Traditional algorithm writeups often mix:
- loose pseudocode,
- inline equations,
- implied randomness,
- unspecified numerical handling,
- ambiguous tie-breaking,
- unclear constraint handling,
- untracked environment differences.

EQC makes these semantics explicit and modular.

---

## Core idea

- Put **math and stochastic behavior** into **operators** (named + versioned).
- Keep the **main procedure** as **control flow only**.
- Make reproducibility, comparability, and safe refactoring first-class requirements.

---

## EQC Structure (Blocks)

### Block 0 — Header, Provenance, and Global Semantics (mandatory)

#### 0.0 Identity
- **Algorithm:** `[Name]`
- **Purpose (1 sentence):** `[What it optimizes / searches / decides]`
- **Spec Version:** `EQC-v1.1` | `[YYYY-MM-DD]` | `[Authors]`
- **Domain / Problem Class:** `[Discrete search / Continuous optimization / Stochastic control / RL / etc.]`

#### 0.A Objective Semantics (mandatory)
Declare global meaning of “better”.

- **Optimization sense:** `MINIMIZE` or `MAXIMIZE`
- **Objective type:** `Scalar` or `Vector`
- **Primary comparison rule:** define a **total preorder** `≼` used everywhere (`best`, `argmin/argmax`, `ReduceBest`, termination thresholds):

  - Scalar: numeric comparison with `EPS_EQ` and the chosen optimization sense
  - Vector: choose one (must be total; if not inherently total, define deterministic fallback):
    - lexicographic order on named components
    - weighted sum with declared weights and stability rules
    - Pareto dominance + deterministic tie-break fallback

- **Invalid objective policy:** define how `NaN/Inf` objectives are ranked (must be total and deterministic)

#### 0.B Reproducibility Contract (mandatory)
- **Seed space:** `seed ∈ {0..2^64-1}`
- **PRNG family:** `[PCG64 / Philox / Threefry / etc.]`
- **Randomness locality:** all sampling occurs **only inside operators**
- **Replay guarantee:** replayable given (seed, PRNG family, numeric policy, ordering policy, parallel policy, environment policy)
- **Replay token:** required per-iteration fingerprint  
  - example: `rng_fingerprint_t = Hash64(rng_state_t)`

#### 0.C Numeric Policy (mandatory)
- **Floating-point format:** `[IEEE-754 binary64 unless stated otherwise]`
- **Rounding mode:** `[round-to-nearest ties-to-even unless stated otherwise]`
- **Fast-math policy:** `[forbidden]` or `[allowed with constraints]`
- **Named tolerances:** `EPS_EQ`, `EPS_PROB`, `EPS_TEMP`, `EPS_DENOM`, plus domain-specific tolerances
- **NaN/Inf policy:** `[abort-on-NaN/Inf]` or `[clamp-and-continue]`
- **Normalized exponentials:** stable log-sum-exp required
- **Overflow/underflow:** explicit clamp rules or explicit abort rules
- **Approx-equality:** define `a ≈ b` using `EPS_EQ`
- **Transcendental functions policy:** define allowed implementations and whether bitwise equality is required

#### 0.D Ordering and Tie-Break Policy (mandatory)
- **Index base:** `[1-based]` or `[0-based]`
- **Tie-breaking:** deterministic (“lowest index wins” or “stable sort then lowest index”)
- **Iteration order:** explicitly defined (ascending index or stable insertion order)
- **Sorting stability:** stable sort required
- **Argmin/argmax ties:** resolved deterministically
- **Categorical boundary rule:** define residual rounding behavior

#### 0.E Parallel, Concurrency, and Reduction Policy (mandatory if parallel)
- **Parallel scope:** what is parallelized
- **Reduction semantics:** deterministic reduction operator and ordering
- **Float reduction rule:** fixed tree/chunk order, plus Kahan/pairwise requirement if needed
- **Concurrency restrictions:** no async updates, or define deterministic resolution + logging
- **Device policy:** CPU/GPU deterministic kernels required or not

#### 0.F Environment and Dependency Policy (mandatory)
- **Reference runtime class:** `[CPU-only]`, `[GPU-enabled]`, `[distributed]`
- **Compiler/flags:** fast-math, FMA, vector intrinsics allowed/forbidden
- **Dependency manifest:** key libraries + versions
- **Determinism level:** `BITWISE` / `TOLERANCE` / `DISTRIBUTIONAL`

#### 0.G Operator Manifest (mandatory)
List exact operator versions used (and namespaces).

Must include:
- Initialization: `InitializePRNG_v#`, `GenerateInitialState_v#`, `InitializeMemory_v#`
- Core: `Fitness_v#`, `Schedule*_v#`, `Select*/Sample*_v#`, `Propose*_v#`, `Accept*_v#`, `Update*_v#`
- Constraints: `Feasible_v#`, `Violation_v#`, `Repair/Project_v#`, `Penalty_v#` (as applicable)
- Termination + logging: `Terminated_v#`, `LogIteration_v#`
- Parallel helpers: `ParallelMap_v#`, `ReduceBest_v#`, `ReduceSum_v#` (as applicable)
- Optional diagnostics: `Error.Emit_v#`, `StateFingerprint_v#`

#### 0.H Namespacing and Packaging (mandatory)
- Fully-qualified operators: `Namespace.OperatorName_v#`
- Imports: `IMPORT Namespace` or `IMPORT Namespace AS Alias`
- No version collisions in manifest
- Sidecar maps each operator to file/module

#### 0.I Outputs and Metric Schema (mandatory)
- **Declared outputs:** `(best_x, best_f, trace)` or equivalent
- **Metric schema:** metric names, types, units, computation rules
- **Completion status:** success/terminated/failed + reason codes

#### 0.J Spec Lifecycle Governance (mandatory)
- Compatibility level: backward compatible / breaking change
- Deprecations + replacements
- Migration notes
- Equivalence target (Block VIII)

#### 0.K Failure and Error Semantics (mandatory)
EQC must make failure modes deterministic and comparable.

- Choose one global error model:
  1. **Structured errors:** `ERROR(code, details)` may be returned by operators  
  2. **Abort-only:** errors trigger termination, but must emit a final trace record

- **Error trace rule:** on error emit final trace record containing:
  - `t`, `failure_code`, `failure_operator`, replay token, minimal diagnostics

- **Recovery policy:** none, or deterministic retry budget rules

#### 0.L Input/Data Provenance (mandatory if data-driven)
If external data is used, declare:
- dataset identifiers + hashes
- preprocessing operators + versions
- caching policy
- parsing strictness rules

---

### Block I — System Model: State, Inputs, Domains (mandatory)

#### I.A Persistent State
Declare all persistent variables with type/shape/constraints, e.g.:
- `x_t ∈ X`
- `M_t ∈ ℳ`
- `t ∈ ℕ`
- `best_x_t`, `best_f_t`
- `stall_count_t`
- `rng_state_t ∈ Ω`

Recommended:
- `state_fp_t = StateFingerprint_v#(persistent_state_t)`

#### I.B Inputs and Hyperparameters
Declare immutable inputs and hyperparameters with ranges/units.

#### I.C Constraints and Feasible Set (mandatory if constrained)
- `X_feas ⊆ X`
- Must define at least one:
  - `Constraints.Feasible_v#(x, inputs) → {0,1}`
  - `Constraints.Violation_v#(x, inputs) → ℝ_{\ge0}` (or vector)
- If none: explicitly “Unconstrained problem.”

#### I.D Transient Variables
Declare transient variables and forbid cross-iteration reference unless promoted.

#### I.E Invariants and Assertions
- Invariants mandatory
- Assertions recommended

---

### Block II — Initialization (mandatory; versioned and testable)

Initialization procedure skeleton:
1. `t ← 0`
2. `rng_state ← Random.InitializePRNG_v#(seed)`
3. `(x_0, rng_state) ← Init.GenerateInitialState_v#(inputs, rng_state)`
4. `M_0 ← Init.InitializeMemory_v#(inputs)`
5. `f_0 ← Objective.Fitness_v#(x_0, inputs)`
6. `best_x ← x_0`, `best_f ← f_0`
7. `stall_count ← 0` (if used)
8. Optional: initialize constraint trackers/penalty states

Rule: changes here are spec changes and must appear in migration notes.  
Failures follow Block 0.K.

---

### Block III — Operator Library (mandatory)

#### III.A Operator template (required)
For each operator:
- **Operator:** `Namespace.Name_v#`
- **Category:** `Init / Objective / Schedule / Propose / Select / Accept / Update / Constraints / Logging / Parallel / Termination / IO / Error`
- **Signature:** typed domains and shapes
- **Purity class:** `PURE / STATEFUL / IO / EXTERNAL_NONDETERMINISTIC`
- **Determinism:** deterministic or stochastic
- **Definition:** math + precise steps
- **Preconditions / Postconditions**
- **Edge cases**
- **Numerical considerations**
- **Ordering/tie handling**
- **Complexity note**
- **Resource considerations (optional)**
- **Failure behavior** (Block 0.K)
- **Dependencies**
- **Test vectors** (Block VII)

#### III.B Strict randomness rule (mandatory)
- `SAMPLE` only inside operators
- Stochastic operators must thread `rng_state` or equivalent replay mechanism

#### III.C No hidden globals (mandatory)
Operators may reference only:
- signature inputs
- declared constants/hyperparameters
- listed dependencies

#### III.D Constraint-handling policy (mandatory if constrained)
Declare one:
- Repair/Project
- Penalty
- Lexicographic feasibility dominance

Must make comparisons total and deterministic.

---

### Block IV — Algorithm Procedure (control-flow only) (mandatory)

#### IV.A Allowed constructs
- `WHILE / FOR / IF / BREAK / RETURN`
- `←` assignment
- operator calls
- scalar arithmetic, comparisons, min/max/clamp, record construction

Everything else belongs in operators.

#### IV.B Total state update rule
Every persistent variable has an explicit update each iteration.

#### IV.C No implicit side effects rule
All effects must be through `IO` or `EXTERNAL_NONDETERMINISTIC` operators in the manifest.

#### IV.D Procedure skeleton
1. Perform Block II  
2. `WHILE NOT Termination.Terminated_v#(persistent_state, inputs):`
   - schedules via operators
   - selection via operators
   - proposal via operators
   - objective eval via operators
   - constraints policy via operators (if needed)
   - accept/reject via operators
   - explicit state updates
   - explicit best update (global preorder)
   - `Logging.LogIteration_v#(trace_record)`
   - `t ← t + 1`
3. Return outputs

Errors handled per Block 0.K with final trace entry.

---

### Block V — Observability, Trace, Comparability (mandatory)

#### V.A Logging rule
Each iteration must call `Logging.LogIteration_v#(trace_record)`.

#### V.B Trace schema (minimum required)
- `t`
- replay token / RNG fingerprint
- control parameters
- discrete choices
- objective values (+ penalty-adjusted if used)
- acceptance decision (+ probability if applicable)
- feasibility/violation metrics (if constrained)
- best summary + stall counters
- invariant/assertion status
- failure fields if failed

#### V.C Metric comparability rule
Metrics must be computed only via the declared metric schema.

#### V.D Comparability guarantee
Two implementations are comparable if they share:
- identical trace schema keys/types
- identical metric schema
- identical replay-token definition + determinism level
- identical objective preorder and constraint policy

---

### Block VI — Parallelism and Nondeterminism Semantics (mandatory if parallel)

Must define:
- parallel boundaries
- deterministic reductions + ordering
- batch aggregation order
- async policy and resolution + logging

---

### Block VII — Validation, Test Vectors, Tooling (enabled end-to-end)

#### VII.A Lint rules (mandatory)
Spec must pass:
1. symbol completeness
2. no hidden globals
3. total state updates
4. stochastic explicitness
5. edge-case totality
6. ordering/tie adherence
7. trace compliance
8. manifest completeness
9. initialization versioned
10. parallel policy declared if used
11. objective preorder total
12. constraint policy total if constrained
13. purity class for all operators
14. failure/error semantics declared and traceable
15. data provenance declared if data-driven

#### VII.B Operator test vectors (mandatory)
- deterministic: input → expected output (tolerance if needed)
- stochastic: (seed, inputs) → expected replay token sequence or invariant property

#### VII.C Golden traces (recommended)
- at least one golden run trace for reference seed/environment
- regression criteria: exact, tolerance, or distributional

#### VII.D Machine-readable sidecar (recommended)
JSON/YAML defining:
- header/provenance
- objective preorder
- manifest + namespaces
- numeric/ordering/parallel policies
- trace + metric schemas
- test vectors + golden trace refs
- checkpoint format version
- equivalence test parameters

---

### Block VIII — Refactoring, Optimization, Semantic Equivalence (mandatory)

#### VIII.A Equivalence levels
- **E0 Trace-equivalent**
- **E1 Metric-equivalent**
- **E2 Distribution-equivalent**
- **E3 Invariant-equivalent**

Spec must declare required level for any operator/parallel change.

#### VIII.B Allowed refactor categories
- algebraic simplification
- numerical stabilization
- vectorization/batching (preserve ordering/reduction semantics)
- memoization/caching (no observable change except declared perf counters)
- parallelization (re-declare policies)
- operator replacement via version bump + manifest update

Breaking observables require trace schema update + migration notes, or breaking-change classification.

#### VIII.C Equivalence test procedure (mandatory)
Define:
- seed sets
- metrics tested
- thresholds/tolerances
- statistical tests for E2 (and multiple-test correction if applicable)

---

### Block IX — Checkpoint, Restore, Long-Run Replay (mandatory for scalable runs)

#### IX.A Checkpoint contents (mandatory if checkpointing exists)
Must include:
- all persistent state
- `rng_state`
- operator manifest bindings
- policy hashes (numeric/ordering/parallel/environment)
- trace schema version
- termination status + reason code
- recommended: `state_fp` + manifest/policy digest

#### IX.B Serialization rules (mandatory)
- format: `[binary/JSON]` with float encoding + endianness rules
- forward/backward compatibility rules + version tag
- restore guarantee: replay class preserved (E0/E1/E2 as declared)

---

## What EQC enables beyond old pseudocode

- Swap math modules without rewriting control flow (only operator wiring changes).
- Make objective meaning explicit and total (global preorder for scalar or vector objectives).
- Make constraints first-class and comparable (feasibility, violation, repair, penalty rules).
- Force explicit semantics for distributions, schedules, acceptance rules, and edge cases.
- Localize and expose all randomness (seeded sampling only inside operators, explicit rng_state).
- Enable deterministic replay with explicit PRNG, numeric, ordering, parallel, and environment policies.
- Make numerical stability a requirement (stable normalization, clamping, overflow/underflow rules).
- Make floating behavior explicit (precision, rounding, equality tolerances, NaN/Inf ranking).
- Enforce deterministic tie-breaking and iteration ordering everywhere.
- Make parallel and distributed execution reproducible (fixed reduction semantics and aggregation order).
- Prevent hidden side effects via operator purity classes (`PURE`, `STATEFUL`, `IO`, `EXTERNAL_NONDETERMINISTIC`).
- Make large specs maintainable through namespacing, imports, and manifest bindings.
- Encode invariants and assertions as specification elements, not informal comments.
- Enable systematic ablation, regression, and safe replacement (versioned operators, test vectors, golden traces).
- Guarantee cross-implementation comparability (standard trace schema, metric schema, replay tokens).
- Enable static validation through lint rules that check completeness, totality, and determinism contracts.
- Support durable evolution through explicit equivalence levels and explicit equivalence test procedures.
- Support long-run and distributed workflows through checkpoint-restore semantics with replay guarantees.
- Improve auditability by making the chain explicit: operators → procedure wiring → traces → outputs.


### Example 1 — Old style (pseudocode + math “below”)

**Pseudocode**

```
Input: x0, T0, α, MAX_ITERS
x ← x0
S ← ones(d)
for t = 0..MAX_ITERS-1:
    T ← T0 / sqrt(t+1)
    p ← softmax(S / T)
    i ← sample_categorical(p)
    x' ← mutate(x, i)
    if accept(x, x', T):
        x ← x'
    S[i] ← (1-α) S[i] + α ( f(x') - f(x) )
return x
```

**Math (informal, “below the code”)**

* Temperature schedule:
  [
  T_t = \frac{T_0}{\sqrt{t+1}}
  ]
* Boltzmann / softmax:
  [
  p_{t,i} = \frac{\exp(S_{t,i}/T_t)}{\sum_{j=1}^{d}\exp(S_{t,j}/T_t)}
  ]
* Acceptance probability (Metropolis-like):
  [
  \Pr(\text{accept}) = \min\left(1, \exp\left(\frac{f(x'_t)-f(x_t)}{T_t}\right)\right)
  ]
* Sensitivity update (EMA):
  [
  S_{t+1,i} = (1-\alpha)S_{t,i} + \alpha,(f(x'_t)-f(x_t))
  ]

**What is missing / ambiguous here (typical old-style issues)**

* Is `f` minimized or maximized?
* What happens when (T \to 0)?
* How is softmax stabilized (overflow)?
* What if (f(x)) is NaN/Inf?
* Does `f(x)` in the EMA use the pre-accept or post-accept state?
* Are indices 0-based or 1-based?
* Does `sample_categorical` have deterministic rounding/tie behavior?
* Is randomness reproducible (PRNG specified, seed threading, ordering policy)?

---

### Example 2 — Same idea using EQC (operators + implementable skeleton)

#### Block 0 (excerpt): Global semantics (minimal)

* Optimization sense: `MAXIMIZE`
* Index base: `0-based`
* Randomness locality: sampling only inside operators
* Numeric policy: stable softmax (log-sum-exp), `EPS_TEMP > 0`, NaN policy declared
* Tie-break: lowest index

#### Block III: Operator library (short, only the key operators)

**Operator:** `Schedule.CoolTemperature`
**Signature:** ((t\in\mathbb{N}, T0\in\mathbb{R}*{>0}) \to (T\in\mathbb{R}*{>0}))
**Definition:**
[
T \leftarrow \max(EPS_TEMP,; T0/\sqrt{t+1})
]

**Operator:** `Prob.BoltzmannPMF`
**Signature:** ((S\in\mathbb{R}^d, T\in\mathbb{R}_{>0}) \to (p\in\Delta^{d-1}))
**Numerical considerations:** stable normalization via max-subtraction
**Definition:**
[
m \leftarrow \max_j S_j,\quad
w_i \leftarrow \exp((S_i-m)/T),\quad
p_i \leftarrow \frac{w_i}{\sum_j w_j}
]

**Operator:** `Rand.SampleCategorical`
**Signature:** ((p\in\Delta^{d-1}, rng_state\in\Omega)\to(i\in{0..d-1}, rng_state'\in\Omega))
**Definition:** SAMPLE (i\sim \text{Categorical}(p)) and return updated RNG state.

**Operator:** `Move.ProposeMutation`
**Signature:** ((x\in X, i\in{0..d-1}, rng_state\in\Omega)\to(x'\in X, rng_state'\in\Omega))
**Definition:** deterministic mutation given `(x,i)` or stochastic but then must thread RNG explicitly.

**Operator:** `Accept.Metropolis`
**Signature:** ((f\in\mathbb{R}, f'\in\mathbb{R}, T\in\mathbb{R}_{>0}, rng_state\in\Omega)\to(accept\in{0,1}, a\in[0,1], rng_state'\in\Omega))
**Definition:**
[
a \leftarrow \min(1,\exp((f'-f)/T)),\quad \text{SAMPLE }u\sim U(0,1),\quad accept \leftarrow [u<a]
]

**Operator:** `Update.SensitivityEMA`
**Signature:** ((S\in\mathbb{R}*{>0}^d, i\in{0..d-1}, f\in\mathbb{R}, f'\in\mathbb{R}, \alpha\in(0,1))\to(S'\in\mathbb{R}*{>0}^d))
**Edge cases:** ensure positivity
**Definition:**
[
signal \leftarrow \max(0, f'-f),\quad
S'_i \leftarrow \max(\varepsilon,\ (1-\alpha)S_i + \alpha\cdot signal),\quad
S'_k \leftarrow S_k\ \forall k\neq i
]

**Operator:** `Logging.LogIteration`
**Signature:** ((trace, record)\to(trace'))
**Definition:** append record with required fields including replay token.

#### Block IV: Procedure skeleton (control flow only)

```
Procedure Execute(seed):

  # Block II: Initialization
  (rng_state) ← Random.InitializePRNG(seed)
  (x, rng_state) ← Init.GenerateInitialState(inputs, rng_state)
  S ← Init.InitializeSensitivity(d)
  f ← Objective.Fitness(x, inputs)
  best_x ← x
  best_f ← f
  t ← 0

  WHILE NOT Termination.Terminated(state, inputs):

      T ← Schedule.CoolTemperature(t, T0)

      p ← Prob.BoltzmannPMF(S, T)
      (i, rng_state) ← Rand.SampleCategorical(p, rng_state)

      (x', rng_state) ← Move.ProposeMutation(x, i, rng_state)
      f' ← Objective.Fitness(x', inputs)

      (accept, acc_prob, rng_state) ← Accept.Metropolis(f, f', T, rng_state)

      IF accept == 1:
          x ← x'
          f ← f'

      S ← Update.SensitivityEMA(S, i, f, f', α)

      (best_x, best_f) ← ReduceBest(best_x, best_f, x, f)   # uses global preorder

      trace ← Logging.LogIteration(trace, {
          t, T, i, f, f', accept, acc_prob, rng_fingerprint_t
      })

      t ← t + 1

  RETURN (best_x, best_f, trace)
```

**What EQC adds here that the old style did not**

* The skeleton is implementable and stable, but the “meaning” lives in operators.
* Softmax stability, (T\to0) handling, NaN policy, tie-breaking, RNG threading, and acceptance semantics are all explicit and testable.
* You can replace `Prob.BoltzmannPMF` with `Prob.BoltzmannPMF` (or a totally different selection policy) without rewriting the loop.
* Refactors have declared equivalence targets (E0/E1/E2/E3) and can be regression-tested via trace/metrics.


**As a single block**

Although not recommended, it is possible to write EQC as a **single merged document** (no explicit “Block 0/1/2…” headings). The tradeoff is that you still need **section boundaries** of some kind, otherwise the spec becomes hard to lint, diff, or tool. In other words, without blocks, it becomes a mess that is hard to maintain.

The practical way to “remove blocks” while keeping EQC’s guarantees is to switch from **block-based layout** to a **schema-first layout**:

* A **single top-level artifact** (one file)
* With **named sections** (or a strict key/value schema) that appear in a fixed order
* So tooling can still find: global semantics, state, init, operators, procedure, trace, tests, equivalence, checkpointing.

Below are three workable “no-block” formats.

---

## Option A — Single-file “Merged Spec” with mandatory section headers

One file, no block numbering, but **required headings**:

1. **Header & Global Semantics** (objective, ordering, numeric, environment, determinism level)
2. **System Model** (persistent state, transient variables, invariants, constraints)
3. **Initialization** (explicit, versioned)
4. **Operator Manifest** (wiring table)
5. **Operator Definitions** (the library)
6. **Procedure** (control flow only, calls operators)
7. **Trace & Metrics** (schema + comparability)
8. **Validation** (lint rules, test vectors, golden traces)
9. **Equivalence & Refactors** (E0–E3 rules, allowed changes)
10. **Checkpoint/Restore** (format + replay guarantees)

This “merges everything” into one narrative document, but keeps machine-detectable anchors.

---

## Option B — Schema layout (YAML/JSON-first) + embedded operator math

Single artifact with a strict schema (good for tooling):

* Top-level keys: `identity`, `objective`, `numeric_policy`, `ordering_policy`, `parallel_policy`, `environment_policy`, `state`, `constraints`, `init`, `manifest`, `operators`, `procedure`, `trace_schema`, `tests`, `equivalence`, `checkpointing`.
* Each operator holds:

  * signature
  * determinism
  * edge cases
  * numerical notes
  * definition (LaTeX or structured steps)

This is the cleanest “merged” form for code generation and validation.

---

## Option C — Literate spec (Markdown) with inline schema tags

One Markdown file that reads like a paper, but contains tagged anchors like:

* `@objective`, `@numeric_policy`, `@ordering_policy`, `@operator`, `@procedure`, `@trace_schema`

Tooling can parse tags without needing “blocks.”

---

# If you merge, you must keep these rules (otherwise it stops being EQC)

Even without blocks, EQC only works if you keep these structural invariants:

* **Global semantics must be declared before anything uses them**
  (objective preorder, numeric policy, ordering/ties, determinism level)
* **All randomness must still live inside operators**
* **Persistent vs transient state must still be explicit**
* **Initialization must still be a first-class spec component**
* **Procedure must remain control-flow only**
* **Trace schema must be declared and enforced**
* **Operators must remain versioned and replaceable via manifest**
* **Equivalence + refactor rules must remain explicit**

So: you can remove “Block” labels, but you cannot remove the **semantic partitions**.

---

## A good merged EQC skeleton (example outline)

```text
EQC Spec: <Name>  Version: EQC-v1.x

1) Header & Global Semantics
   - objective sense + total preorder
   - numeric policy
   - ordering/ties policy
   - reproducibility contract
   - environment/dependency determinism

2) System Model
   - persistent state
   - transient variables
   - constraints + feasible semantics
   - invariants/assertions

3) Initialization
   - explicit init procedure + operator versions

4) Operator Manifest
   - list operator bindings

5) Operator Library
   - operator definitions (versioned, typed, edge cases, numerical notes)

6) Procedure
   - control flow only; operator calls only; total state updates

7) Observability
   - trace schema + metric schema + comparability rule

8) Validation
   - lint rules + test vectors + golden traces

9) Refactor & Equivalence
   - E0–E3 + permitted changes

10) Checkpoint/Restore
   - required fields + serialization + replay class
```

This is “merged” (one file, one flow), but still EQC-complete.




