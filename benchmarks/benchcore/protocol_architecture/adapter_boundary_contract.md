# Adapter Boundary Contract

## Purpose
Define the responsibilities and boundaries of adapters in the BenchCore benchmark pack's protocol architecture. Adapters translate between internal representation and external protocol formats (REST, MOS).

## Source
BENCHCORE-DOC-030

## Adapter Responsibilities
1. **REST Adapter**: Converts internal command objects into mock REST request objects (validated against `mock_rest_input.schema.json`) and converts mock REST response objects into internal result objects.
2. **MOS Adapter**: Converts internal command objects into mock MOS XML payloads and converts mock MOS response objects (validated against `mock_mos_output.schema.json`) into internal result objects.
3. **Translation Adapter**: Bidirectional mapping between REST and MOS representations as defined in `rest_mos_mapping_contract.md`.

## Boundary Rules
1. **No live I/O**: Adapters must never open TCP connections, make HTTP requests, or interact with live systems. All operations are pure transformations.
2. **Schema validation boundary**: All adapter outputs must pass schema validation before being consumed by the next stage.
3. **Error boundary**: Adapters must catch and wrap all transformation errors into a standard `AdapterError` type with fields: `adapter_name`, `input_snapshot`, `error_message`, `error_category` (parse, transform, validation).
4. **Isolation**: Adapters must have no knowledge of stages beyond their immediate consumer. They receive typed inputs and produce typed outputs.
5. **Statelessness**: Adapters must be stateless. All configuration must be passed as parameters.

## Failure Handling
| Error Category | Handling | Output |
|----------------|----------|--------|
| Parse error | Catch, wrap, propagate | `AdapterError(category: "parse")` |
| Transform error | Catch, wrap, propagate | `AdapterError(category: "transform")` |
| Validation error | Catch, wrap, propagate | `AdapterError(category: "validation")` |
| Unknown error | Catch, wrap, propagate | `AdapterError(category: "unknown")` |

## No-Live-Dependency Requirement
- **No** real HTTP clients, TCP sockets, SSH clients, or database drivers.
- **No** real credentials, tokens, or secrets.
- **No** file system writes beyond benchmark output directories.
- **No** environment-specific configuration (hostnames, ports, paths).

## Testing
- Adapters must be unit-testable with no mocking framework required (pure functions).
- Test fixtures live in `protocol_architecture/fixtures/`.
