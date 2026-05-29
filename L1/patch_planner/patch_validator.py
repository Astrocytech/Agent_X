"""Validates that a patch plan respects L0 invariants."""


class PatchValidator:
    def validate(self, plan) -> bool:
        raise NotImplementedError("Patch validator scaffold")
