"""Preprocessing utilities tailored for code + natural language mixtures."""
from __future__ import annotations

import re
import textwrap
import unicodedata
from typing import Iterable

from .config import PreprocessorConfig


_CODE_BLOCK_RE = re.compile(r"```(?P<lang>\w+)?\n(?P<body>.*?)(```|$)", re.DOTALL)


class CodePreprocessor:
    """Normalize, clean, and combine natural language + code segments."""

    def __init__(self, config: PreprocessorConfig | None = None) -> None:
        self.config = config or PreprocessorConfig()

    def _normalize_unicode(self, text: str) -> str:
        if not self.config.normalize_unicode:
            return text
        return unicodedata.normalize("NFKC", text)

    def _strip_comments(self, code: str) -> str:
        if not self.config.strip_comments:
            return code
        # Remove common single-line comments; keeps docstrings intentionally.
        code = re.sub(r"(?m)#.*$", "", code)
        code = re.sub(r"(?m)//.*$", "", code)
        return code

    def _collapse_whitespace(self, text: str) -> str:
        if not self.config.collapse_whitespace:
            return text
        return re.sub(r"\s+", " ", text).strip()

    def _dedent(self, text: str) -> str:
        if not self.config.dedent:
            return text
        return textwrap.dedent(text)

    def _ensure_trailing_newline(self, text: str) -> str:
        if not self.config.ensure_trailing_newline:
            return text
        return text if text.endswith("\n") else text + "\n"

    def _extract_inline_code(self, text: str) -> Iterable[str]:
        for match in _CODE_BLOCK_RE.finditer(text):
            yield match.group("body").strip("\n")

    def __call__(self, text: str, code: str | None = None) -> str:
        text = text or ""
        code = code or ""

        text = self._normalize_unicode(text)
        code = self._normalize_unicode(code)

        inline_blocks = [self._dedent(block) for block in self._extract_inline_code(text)]
        if inline_blocks and not code:
            code = "\n\n".join(inline_blocks)

        text = self._collapse_whitespace(text)
        code = self._strip_comments(code)
        code = self._dedent(code)

        combined = []
        if text:
            combined.append(f"<nl>{text}")
        if code:
            combined.append("<code>\n" + code)
        normalized = "\n".join(filter(None, combined))
        normalized = self._ensure_trailing_newline(normalized)
        return normalized
