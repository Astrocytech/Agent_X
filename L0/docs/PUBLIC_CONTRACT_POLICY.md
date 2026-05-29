# Public Contract Policy

The L0 public contract consists of:

- `KernelService`
- `KernelService.run_turn`
- `KernelService.health`
- `KernelTurnRequest`
- `KernelTurnResponse`
- public seed ports
- evidence envelope
- seed package manifest
- capability manifest
- seed invariants

## Compatibility rule

Fields may be added only if optional or defaulted.

Fields may not be removed, renamed, or semantically inverted without creating a new versioned contract.

## Versioning rule

Breaking changes require a new contract file, for example:

- `kernel_turn_request_v2.py`
- `kernel_turn_response_v2.py`

The old version must remain supported until explicitly deprecated outside L0.

## Runtime rule

`KernelService.run_turn()` must remain the only stable public turn entrypoint.
