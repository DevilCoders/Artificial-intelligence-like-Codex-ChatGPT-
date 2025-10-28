"""Custom Transformer encoder stack used for the Codex-like model."""
from __future__ import annotations

import torch
from torch import nn

from .config import EncoderConfig


class CodeEncoder(nn.Module):
    """Lightweight Transformer encoder tailored for causal language modelling."""

    def __init__(self, config: EncoderConfig, vocab_size: int) -> None:
        super().__init__()
        self.config = config
        self.token_embeddings = nn.Embedding(vocab_size, config.hidden_size)
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        self.layernorm = nn.LayerNorm(config.hidden_size)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.hidden_size,
            nhead=config.num_attention_heads,
            dim_feedforward=config.intermediate_size,
            dropout=config.dropout,
            activation="gelu",
            batch_first=True,
        )
        self.layers = nn.TransformerEncoder(encoder_layer, num_layers=config.num_layers)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, input_ids: torch.LongTensor, attention_mask: torch.LongTensor | None = None) -> torch.FloatTensor:
        device = input_ids.device
        batch_size, seq_len = input_ids.size()
        positions = torch.arange(seq_len, device=device).unsqueeze(0).expand(batch_size, seq_len)
        token_embeds = self.token_embeddings(input_ids)
        position_embeds = self.position_embeddings(positions)
        hidden_states = token_embeds + position_embeds
        hidden_states = self.layernorm(self.dropout(hidden_states))

        if attention_mask is not None:
            src_key_padding_mask = attention_mask == 0
        else:
            src_key_padding_mask = None

        encoded = self.layers(hidden_states, src_key_padding_mask=src_key_padding_mask)
        return encoded

    @property
    def embedding_weight(self) -> torch.nn.Parameter:
        return self.token_embeddings.weight
