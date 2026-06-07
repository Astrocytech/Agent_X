# Repository Ownership

## `L0/`

Owner: L0 seed kernel core.

Allowed:
- kernel code
- kernel contracts
- governance policies
- tool gateway code
- profiles
- kernel tests
- kernel docs
- evidence records

Not allowed:
- L1 governance standards
- runtime integration code
- tool-specific implementation

## `L1/`

Owner: L1 governance and evolution control.

Allowed:
- FIC units
- standards
- SIB bindings
- validators
- evolution controller code
- evidence
- generated manifests
- layer tests

Not allowed:
- L0 kernel code
- L2 profiles
- runtime implementation

## `L2/`

Owner: L2 specialization profiles and blueprints.

Allowed:
- profile definitions
- blueprints
- evaluation specs
- integration specs
- SIB bindings
- layer tests
- evidence

Not allowed:
- L0 kernel code
- L1 governance implementation
- runtime code

## `tools/agentx_initiator/`

Owner: project inspection and initiation tool.

Allowed:
- CLI commands
- core analysis logic
- schemas
- templates
- tests
- fixtures
- tool docs
- evidence

Not allowed:
- L1 governance standards
- runtime integration code

## `tools/agentx_evolve/`

Owner: runtime integration layer.

Allowed:
- runtime code
- model adapters
- patch execution code
- orchestrator code
- schemas
- fixtures
- tool-specific docs
- tool-specific tests

Not allowed:
- L1 governance standards
- project-wide roadmap docs
- unrelated experiments
- generated `.agentx-init` runtime runs

## `docs/`

Owner: project-wide documentation.

Allowed:
- architecture docs
- governance docs
- runtime integration plans
- acceptance criteria
- archived superseded docs

Not allowed:
- layer-specific source code
- test files
- runtime artifacts

## `tests/`

Owner: cross-component and system tests.

Allowed:
- integration tests
- system tests
- regression tests
- smoke tests

Not allowed:
- component-specific unit tests (belong in layer/tool)

## `examples/`

Owner: user-facing examples.

Allowed:
- concept examples
- agent examples
- patch examples
- example fixtures

Not allowed:
- production code
- test suites

## `requirements/`

Owner: dependency management.

Allowed:
- dependency list files

Not allowed:
- source code
- scripts
