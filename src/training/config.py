"""Configuration dataclasses for Codex-like model training."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


def _default_special_tokens() -> List[str]:
    return [
        "<pad>",
        "<eos>",
        "<bos>",
        "<nl>",
        "<code>",
        "</code>",
        "<python>",
        "</python>",
    ]


@dataclass
class DatasetConfig:
    """Configuration describing a single dataset split used for training.

    Attributes:
        name: Name passed to ``datasets.load_dataset``.
        subset: Optional subset or config name for the dataset.
        split: Dataset split to load (e.g. ``"train"``).
        text_column: Column containing natural language text.
        code_column: Optional column containing code snippets. When ``None``
            the ``text_column`` is assumed to contain all content.
        weight: Relative sampling weight for the dataset when mixing multiple
            sources together. The values do not need to add up to 1.0.
    """

    name: str
    subset: Optional[str] = None
    split: str = "train"
    text_column: str = "text"
    code_column: Optional[str] = None
    weight: float = 1.0


@dataclass
class TokenizerConfig:
    """Configuration for building a tokenizer tailored to source code."""

    pretrained: Optional[str] = None
    vocab_size: int = 51200
    model_max_length: int = 14336  # ~14 KB context window for UTF-8 code.
    byte_level: bool = True
    lowercase: bool = False
    min_frequency: int = 2
    special_tokens: List[str] = field(default_factory=_default_special_tokens)
    train_files: Optional[List[str]] = None
    serialization_dir: str = "tokenizer"
    use_custom: bool = False


@dataclass
class PreprocessorConfig:
    """Configuration options for the text/code preprocessor."""

    normalize_unicode: bool = True
    strip_comments: bool = False
    collapse_whitespace: bool = True
    dedent: bool = True
    ensure_trailing_newline: bool = True


@dataclass
class ChunkerConfig:
    """Configuration describing how to chunk long documents."""

    max_characters: int = 12000
    overlap: int = 512
    minimum_chunk_size: int = 256


@dataclass
class EncoderConfig:
    """High-level architecture knobs for the custom encoder."""

    hidden_size: int = 2048
    num_layers: int = 24
    num_attention_heads: int = 16
    intermediate_size: int = 8192
    dropout: float = 0.1
    max_position_embeddings: int = 16384


@dataclass
class DecoderConfig:
    """Configuration for the causal LM decoder head."""

    hidden_size: int = 2048
    tie_embeddings: bool = True


@dataclass
class ModelConfig:
    """Configuration for instantiating the base language model."""

    pretrained: Optional[str] = "bigcode/starcoderbase"
    torch_dtype: str = "bfloat16"
    gradient_checkpointing: bool = True
    use_flash_attention: bool = True
    use_custom_architecture: bool = False
    encoder: EncoderConfig = field(default_factory=EncoderConfig)
    decoder: DecoderConfig = field(default_factory=DecoderConfig)


@dataclass
class TrainingConfig:
    """High-level knobs for training the Codex-like model."""

    output_dir: str = "checkpoints/codex-like"
    total_batch_size: int = 1024
    micro_batch_size: int = 8
    learning_rate: float = 2.5e-4
    warmup_ratio: float = 0.05
    weight_decay: float = 0.1
    num_train_steps: int = 250000
    eval_interval: int = 1000
    log_interval: int = 50
    gradient_accumulation_steps: Optional[int] = None
    mixed_precision: str = "bf16"
    checkpoint_interval: int = 10000
    resume_from_checkpoint: Optional[str] = None
    datasets: List[DatasetConfig] = field(default_factory=list)
    tokenizer: TokenizerConfig = field(default_factory=TokenizerConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    preprocessor: PreprocessorConfig = field(default_factory=PreprocessorConfig)
    chunker: ChunkerConfig = field(default_factory=ChunkerConfig)


DEFAULT_DATASETS: List[DatasetConfig] = [
    DatasetConfig(
        name="codeparrot/github-code",
        split="train",
        text_column="content",
        code_column="content",
        weight=7.0,
    ),
    DatasetConfig(
        name="the_pile",
        subset="all",
        split="train",
        text_column="text",
        weight=3.0,
    ),
]


def default_training_config() -> TrainingConfig:
    """Return a ``TrainingConfig`` populated with curated defaults."""

    return TrainingConfig(datasets=list(DEFAULT_DATASETS))
