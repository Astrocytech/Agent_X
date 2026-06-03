from __future__ import annotations


class ContextBudgeter:
    TOKENS_PER_CHAR = 0.25

    def __init__(self, max_tokens: int = 8192):
        self._max_tokens = max_tokens
        self._used = 0

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    @max_tokens.setter
    def max_tokens(self, value: int) -> None:
        self._max_tokens = value

    @property
    def used(self) -> int:
        return self._used

    def reset(self) -> None:
        self._used = 0

    def consume(self, text: str) -> int:
        tokens = self._estimate(text)
        self._used += tokens
        return tokens

    def headroom(self) -> int:
        return max(0, self._max_tokens - self._used)

    def is_over_budget(self) -> bool:
        return self._used > self._max_tokens

    def fraction_used(self) -> float:
        if self._max_tokens == 0:
            return 1.0
        return self._used / self._max_tokens

    def _estimate(self, text: str) -> int:
        return int(len(text) * self.TOKENS_PER_CHAR) + 1
