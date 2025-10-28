"""Chunking utilities to slice long documents into manageable windows."""
from __future__ import annotations

from typing import Iterable, Iterator, Sequence

from .config import ChunkerConfig


class CodeChunker:
    """Chunk text into overlapping windows to respect model context limits."""

    def __init__(self, config: ChunkerConfig | None = None) -> None:
        self.config = config or ChunkerConfig()
        if self.config.max_characters <= 0:
            raise ValueError("max_characters must be positive")
        if self.config.overlap >= self.config.max_characters:
            raise ValueError("overlap must be smaller than max_characters")

    def _sliding_windows(self, text: str) -> Iterator[str]:
        step = self.config.max_characters - self.config.overlap
        if step <= 0:
            step = self.config.max_characters
        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(text_len, start + self.config.max_characters)
            chunk = text[start:end]
            if len(chunk) >= self.config.minimum_chunk_size or end == text_len:
                yield chunk
            start += step

    def __call__(self, text: str | Sequence[str]) -> Iterable[str]:
        if isinstance(text, str):
            yield from self._sliding_windows(text)
        else:
            for segment in text:
                yield from self._sliding_windows(segment)
