"""Checks whether a proposed change respects L0 boundaries."""


class BoundaryChecker:
    def check(self, proposed_change: dict) -> dict:
        raise NotImplementedError("Boundary checker scaffold")
