# Model Policy

## Purpose
Define how external model integration works with L0.

## Rules
- Models are external to L0 runtime
- Model access is governed by extension ABI boundary
- Request/response contracts must be versioned
- Model outputs must be validated before use in governance decisions

## Enforcement
- Extension boundary checks in L1 controller
- Model contracts registered in extension_specs
