from __future__ import annotations

import dataclasses
import re as _re
import typing as _typing

from L1.controller.fic_generator import FicTemplate

__all__ = [
    "FicValidationResult",
    "FicValidator",
    "FicValidatorError",
    "validate_fics",
]


@dataclasses.dataclass(frozen=True)
class FicValidationResult:
    is_valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


class FicValidatorError(Exception):
    pass


_FIC_ID_RE = _re.compile(r"^FIC-L1-PLAN-\d{3}$")
_UNIT_ID_RE = _re.compile(r"^UNIT-L1-PLAN-\d{3}$")


class FicValidator:
    def validate(self, templates: object) -> FicValidationResult:
        errors: list[str] = []

        if not isinstance(templates, tuple):
            return FicValidationResult(
                is_valid=False,
                errors=("templates must be a tuple",),
                warnings=(),
            )

        if len(templates) == 0:
            return FicValidationResult(
                is_valid=False,
                errors=("no templates to validate",),
                warnings=(),
            )

        for i, t in enumerate(templates):
            if not isinstance(t, FicTemplate):
                errors.append(f"index {i}: must be a FicTemplate")
                continue
            self._validate_one(t, i, errors)

        seen_fic_ids: set[str] = set()
        seen_unit_ids: set[str] = set()
        for t in templates:
            if isinstance(t, FicTemplate):
                if t.fic_id in seen_fic_ids:
                    errors.append(f"duplicate fic_id: {t.fic_id}")
                seen_fic_ids.add(t.fic_id)
                if t.unit_id in seen_unit_ids:
                    errors.append(f"duplicate unit_id: {t.unit_id}")
                seen_unit_ids.add(t.unit_id)

        return FicValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
            warnings=(),
        )

    @staticmethod
    def _validate_one(t: FicTemplate, index: int, errors: list[str]) -> None:
        prefix = f"index {index}"
        if not _FIC_ID_RE.match(t.fic_id):
            errors.append(f"{prefix}: invalid fic_id: {t.fic_id!r}")
        if not _UNIT_ID_RE.match(t.unit_id):
            errors.append(f"{prefix}: invalid unit_id: {t.unit_id!r}")
        if not t.target_file:
            errors.append(f"{prefix}: target_file must not be empty")
        if t.target_file.startswith("/"):
            errors.append(f"{prefix}: target_file must not be absolute")
        if not t.description:
            errors.append(f"{prefix}: description must not be empty")
        if t.status != "draft":
            errors.append(f"{prefix}: status must be 'draft', got {t.status!r}")
        if t.version != "v0.1.0":
            errors.append(f"{prefix}: version must be 'v0.1.0', got {t.version!r}")


def validate_fics(
    templates: tuple[FicTemplate, ...],
) -> FicValidationResult:
    return FicValidator().validate(templates)
