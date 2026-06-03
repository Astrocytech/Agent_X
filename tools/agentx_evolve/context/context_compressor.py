from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


class ContextCompressor:
    MAX_SNIPPET_LINES = 50

    def compress_snippet(self, content: str, max_lines: int = 0) -> str:
        if not max_lines:
            max_lines = self.MAX_SNIPPET_LINES
        lines = content.split("\n")
        if len(lines) <= max_lines:
            return content
        head = lines[:max_lines // 2]
        tail = lines[-(max_lines // 2):]
        return "\n".join(head) + f"\n... ({len(lines) - max_lines} lines omitted) ...\n" + "\n".join(tail)

    def summarize(self, text: str, max_chars: int = 500) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "..."

    def strip_comments(self, code: str, comment_chars: str = "#") -> str:
        lines = code.split("\n")
        result = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(comment_chars):
                continue
            result.append(line)
        return "\n".join(result)

    def extract_signatures(self, code: str) -> list[str]:
        lines = code.split("\n")
        sigs: list[str] = []
        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(kw) for kw in ("def ", "class ", "async def ")):
                sigs.append(stripped)
        return sigs
