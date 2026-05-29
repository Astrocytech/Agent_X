from __future__ import annotations

import dataclasses
import enum
import pathlib as _pathlib
import re as _re
import typing as _typing

__all__ = [
    "GoalType",
    "GoalPriority",
    "GoalScope",
    "GoalRecord",
    "GoalClassifier",
    "GoalClassifierError",
    "classify_goal_text",
    "classify_goal_file",
]


class GoalType(enum.Enum):
    FEATURE = "feature"
    BUG_FIX = "bug_fix"
    REFACTOR = "refactor"
    RESEARCH = "research"
    DOCUMENTATION = "documentation"
    INFRASTRUCTURE = "infrastructure"


class GoalPriority(enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GoalScope(enum.Enum):
    COMPONENT = "component"
    CROSS_COMPONENT = "cross_component"
    SYSTEM = "system"


@dataclasses.dataclass(frozen=True)
class GoalRecord:
    goal_type: GoalType
    priority: GoalPriority
    scope: GoalScope
    summary: str
    constraints: tuple[str, ...]
    raw_text: str


class GoalClassifierError(Exception):
    pass


_TYPE_KEYWORDS: list[tuple[list[str], GoalType]] = [
    (["feature", "new capability", "add ability", "implement"], GoalType.FEATURE),
    (["bug", "fix", "error", "crash", "defect", "incorrect"], GoalType.BUG_FIX),
    (["refactor", "clean", "restructure", "reorganize", "simplify"], GoalType.REFACTOR),
    (["research", "investigate", "explore", "study", "analysis"], GoalType.RESEARCH),
    (["doc", "readme", "comment", "documentation", "annotate"], GoalType.DOCUMENTATION),
    (
        ["infra", "ci", "cd", "pipeline", "deploy", "build system"],
        GoalType.INFRASTRUCTURE,
    ),
]

_PRIORITY_KEYWORDS: list[tuple[list[str], GoalPriority]] = [
    (["critical", "urgent", "p0", "blocker"], GoalPriority.CRITICAL),
    (["high", "p1", "important"], GoalPriority.HIGH),
    (["medium", "p2", "moderate"], GoalPriority.MEDIUM),
    (["low", "p3", "nice to have", "minor"], GoalPriority.LOW),
]

_SCOPE_KEYWORDS: list[tuple[list[str], GoalScope]] = [
    (["system", "cross-layer", "global", "portfolio"], GoalScope.SYSTEM),
    (["cross-component", "inter-module", "multi-module"], GoalScope.CROSS_COMPONENT),
    (["component", "module", "single", "local"], GoalScope.COMPONENT),
]

_CONSTRAINT_KEYWORDS: list[str] = [
    "must", "must not", "shall", "cannot", "require", "only",
    "no ", "without", "within", "after", "before", "until",
    "except", "unless",
]


class GoalClassifier:
    def classify(self, text: str) -> GoalRecord:
        if not isinstance(text, str):
            raise GoalClassifierError("text must be a string")
        lower = text.lower()
        goal_type = self._classify_type(lower)
        priority = self._classify_priority(lower)
        scope = self._classify_scope(lower)
        summary = self._extract_summary(text)
        constraints = self._extract_constraints(text)
        return GoalRecord(
            goal_type=goal_type,
            priority=priority,
            scope=scope,
            summary=summary,
            constraints=constraints,
            raw_text=text,
        )

    def classify_file(self, path: str, *, root: _StrOrPath = ".") -> GoalRecord:
        root_p = _resolve_root(root)
        p = _pathlib.Path(path)
        if p.is_absolute():
            raise GoalClassifierError("path must be relative")
        target = (root_p / p).resolve(strict=False)
        if not target.exists():
            raise GoalClassifierError("file not found")
        if not target.is_file():
            raise GoalClassifierError("path is not a file")
        try:
            text = target.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            raise GoalClassifierError("file is not valid UTF-8")
        return self.classify(text)

    @staticmethod
    def _classify_type(lower: str) -> GoalType:
        for keywords, gtype in _TYPE_KEYWORDS:
            for kw in keywords:
                if _word_in(kw, lower):
                    return gtype
        return GoalType.FEATURE

    @staticmethod
    def _classify_priority(lower: str) -> GoalPriority:
        for keywords, gprio in _PRIORITY_KEYWORDS:
            for kw in keywords:
                if _word_in(kw, lower):
                    return gprio
        return GoalPriority.MEDIUM

    @staticmethod
    def _classify_scope(lower: str) -> GoalScope:
        for keywords, gscope in _SCOPE_KEYWORDS:
            for kw in keywords:
                if _word_in(kw, lower):
                    return gscope
        return GoalScope.COMPONENT

    @staticmethod
    def _extract_summary(text: str) -> str:
        stripped = text.strip()
        if not stripped:
            return ""
        lines = stripped.splitlines()
        for line in lines:
            cleaned = line.strip().strip("#*-").strip()
            if cleaned:
                return cleaned
        return ""

    @staticmethod
    def _extract_constraints(text: str) -> tuple[str, ...]:
        lower = text.lower()
        found: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            line_lower = stripped.lower()
            for kw in _CONSTRAINT_KEYWORDS:
                if _word_in(kw, line_lower):
                    found.append(stripped)
                    break
        return tuple(found)


_StrOrPath = _typing.Union[str, _pathlib.Path]


def _resolve_root(root: _StrOrPath) -> _pathlib.Path:
    if isinstance(root, _pathlib.Path):
        r = root
    elif isinstance(root, str):
        r = _pathlib.Path(root)
    else:
        raise GoalClassifierError("root must be str or pathlib.Path")
    if not r.exists():
        raise GoalClassifierError("root does not exist")
    if not r.is_dir():
        raise GoalClassifierError("root is not a directory")
    return r


def _word_in(keyword: str, lower_text: str) -> bool:
    pattern = _re.compile(_re.escape(keyword), _re.IGNORECASE)
    return bool(pattern.search(lower_text))


def classify_goal_text(text: str) -> GoalRecord:
    return GoalClassifier().classify(text)


def classify_goal_file(path: str, *, root: _StrOrPath = ".") -> GoalRecord:
    return GoalClassifier().classify_file(path, root=root)
