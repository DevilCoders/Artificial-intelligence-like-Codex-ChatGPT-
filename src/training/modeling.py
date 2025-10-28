"""Model construction helpers for the Codex-like system."""
from __future__ import annotations

from typing import Iterable, Optional

import torch
from torch import nn
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizerBase,
)
from transformers.modeling_outputs import CausalLMOutputWithCrossAttentions

from .config import ModelConfig, TokenizerConfig
from .decoder import CodeDecoder
from .encoder import CodeEncoder
from .tokenizer import build_custom_tokenizer


class CodexLikeCausalLM(nn.Module):
    """Minimal causal language model composed of custom encoder + decoder."""

    def __init__(self, config: ModelConfig, tokenizer: PreTrainedTokenizerBase) -> None:
        super().__init__()
        self.config = config
        vocab_size = len(tokenizer)
        if config.decoder.hidden_size != config.encoder.hidden_size:
            raise ValueError(
                "Decoder hidden size must match encoder hidden size for weight tying."
            )
        self.encoder = CodeEncoder(config.encoder, vocab_size=vocab_size)
        self.decoder = CodeDecoder(config.decoder, hidden_size=config.encoder.hidden_size, vocab_size=vocab_size)
        if config.decoder.tie_embeddings:
            self.decoder.lm_head.weight = self.encoder.embedding_weight
        self.loss_fn = nn.CrossEntropyLoss(ignore_index=-100)

    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: Optional[torch.LongTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        **_: dict,
    ) -> CausalLMOutputWithCrossAttentions:
        hidden_states = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        logits = self.decoder(hidden_states)

        loss = None
        if labels is not None:
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = labels[:, 1:].contiguous()
            loss = self.loss_fn(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
            )

        return CausalLMOutputWithCrossAttentions(loss=loss, logits=logits)


def build_tokenizer(
    config: TokenizerConfig,
    corpus: Optional[Iterable[str]] = None,
) -> PreTrainedTokenizerBase:
    """Load or train a tokenizer with sensible defaults for code."""

    if config.use_custom:
        if corpus is None:
            raise ValueError("A text corpus is required when ``use_custom`` tokenizer mode is enabled.")
        tokenizer = build_custom_tokenizer(config, corpus=corpus)
    elif config.pretrained:
        tokenizer = AutoTokenizer.from_pretrained(config.pretrained, use_fast=True)
    else:
        raise ValueError(
            "Provide either a pretrained tokenizer checkpoint or enable ``use_custom``"
            " with the paths necessary to train from scratch."
        )

    tokenizer.model_max_length = config.model_max_length
    tokenizer.add_special_tokens({"additional_special_tokens": config.special_tokens})
    if tokenizer.eos_token is None and "<eos>" in config.special_tokens:
        tokenizer.add_special_tokens({"eos_token": "<eos>"})
    if tokenizer.bos_token is None and "<bos>" in config.special_tokens:
        tokenizer.add_special_tokens({"bos_token": "<bos>"})
    if tokenizer.pad_token is None and "<pad>" in config.special_tokens:
        tokenizer.add_special_tokens({"pad_token": "<pad>"})
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    tokenizer.truncation_side = "left"
    return tokenizer


def build_model(config: ModelConfig, tokenizer: PreTrainedTokenizerBase) -> PreTrainedModel | nn.Module:
    """Instantiate the language model, supporting custom and pretrained variants."""

    if config.use_custom_architecture:
        return CodexLikeCausalLM(config=config, tokenizer=tokenizer)

    if not config.pretrained:
        raise ValueError("A pretrained checkpoint is required when ``use_custom_architecture`` is False.")

    torch_dtype: Optional[torch.dtype]
    if config.torch_dtype == "bfloat16":
        torch_dtype = torch.bfloat16
    elif config.torch_dtype == "float16":
        torch_dtype = torch.float16
    else:
        torch_dtype = None

    model = AutoModelForCausalLM.from_pretrained(
        config.pretrained,
        torch_dtype=torch_dtype,
        trust_remote_code=True,
    )
    model.resize_token_embeddings(len(tokenizer))

    if config.gradient_checkpointing and hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()
    if config.use_flash_attention and hasattr(model, "enable_flash_attention"):
        model.enable_flash_attention()

    return model
