"""Decoder head for converting hidden states into token logits."""
from __future__ import annotations

import torch
from torch import nn

from .config import DecoderConfig


class CodeDecoder(nn.Module):
    """Simple linear language modelling head."""

    def __init__(self, config: DecoderConfig, hidden_size: int, vocab_size: int) -> None:
        super().__init__()
        self.config = config
        self.lm_head = nn.Linear(hidden_size, vocab_size, bias=False)

    def forward(self, hidden_states: torch.FloatTensor) -> torch.FloatTensor:
        return self.lm_head(hidden_states)
