"""Custom tokenizer utilities for the Codex-like system."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from tokenizers import ByteLevelBPETokenizer
from transformers import PreTrainedTokenizerFast

from .config import TokenizerConfig


@dataclass
class CodeTokenizerState:
    """Serializable state describing the tokenizer training artefacts."""

    vocab_path: Path
    merges_path: Path
    special_tokens: List[str]
    tokenizer_file: Path


class CodeTokenizer:
    """Train and serve a byte-level BPE tokenizer specialised for code."""

    def __init__(self, config: TokenizerConfig) -> None:
        self.config = config
        self._tokenizer = ByteLevelBPETokenizer(lowercase=config.lowercase)
        self._hf_tokenizer: Optional[PreTrainedTokenizerFast] = None
        self._state: Optional[CodeTokenizerState] = None

    def train_from_iterator(self, iterator: Iterable[str]) -> None:
        """Train the tokenizer using an iterator of strings."""

        self._tokenizer.train_from_iterator(
            iterator,
            vocab_size=self.config.vocab_size,
            min_frequency=self.config.min_frequency,
            show_progress=False,
            special_tokens=self.config.special_tokens or [],
        )

    def train_from_files(self, files: Iterable[str]) -> None:
        """Train the tokenizer using files on disk."""

        self._tokenizer.train(
            files,
            vocab_size=self.config.vocab_size,
            min_frequency=self.config.min_frequency,
            special_tokens=self.config.special_tokens or [],
        )

    def save(self, directory: str | Path) -> CodeTokenizerState:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        vocab_path_str, merges_path_str = self._tokenizer.save_model(str(directory))
        tokenizer_file = directory / "tokenizer.json"
        self._tokenizer.save(str(tokenizer_file))
        vocab_path = Path(vocab_path_str)
        merges_path = Path(merges_path_str)
        self._state = CodeTokenizerState(
            vocab_path=vocab_path,
            merges_path=merges_path,
            special_tokens=self.config.special_tokens or [],
            tokenizer_file=tokenizer_file,
        )
        return self._state

    def to_hf(self) -> PreTrainedTokenizerFast:
        """Convert the underlying tokenizer to a ``PreTrainedTokenizerFast``."""

        if self._hf_tokenizer is not None:
            return self._hf_tokenizer

        if self._state is None:
            raise RuntimeError("Tokenizer must be trained and saved before conversion.")

        tokenizer = PreTrainedTokenizerFast(
            tokenizer_file=str(self._state.tokenizer_file),
            model_max_length=self.config.model_max_length,
        )
        tokenizer.add_special_tokens({"additional_special_tokens": self._state.special_tokens})
        tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
        tokenizer.truncation_side = "left"
        self._hf_tokenizer = tokenizer
        return tokenizer


def build_custom_tokenizer(config: TokenizerConfig, corpus: Optional[Iterable[str]] = None) -> PreTrainedTokenizerFast:
    """Utility function to train a custom tokenizer when no checkpoint is provided."""

    tokenizer_builder = CodeTokenizer(config)
    if config.train_files:
        tokenizer_builder.train_from_files(config.train_files)
    elif corpus is not None:
        tokenizer_builder.train_from_iterator(corpus)
    else:
        raise ValueError("Either ``train_files`` or an in-memory corpus must be provided.")

    tokenizer_builder.save(Path(config.serialization_dir))
    return tokenizer_builder.to_hf()
