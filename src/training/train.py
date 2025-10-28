"""End-to-end training entrypoint for the Codex-like model."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List, Optional

from datasets import Dataset
from transformers import DataCollatorForLanguageModeling, Trainer, TrainingArguments

from .config import DatasetConfig, TrainingConfig, default_training_config
from .chunker import CodeChunker
from .data import MixedDataset, interleave_weighted, load_mixed_datasets
from .modeling import build_model, build_tokenizer
from .preprocess import CodePreprocessor

LOGGER = logging.getLogger(__name__)


def _prepare_corpus(
    dataset: Dataset,
    preprocessor: CodePreprocessor,
    chunker: CodeChunker,
    text_column: str = "text",
    code_column: Optional[str] = "code",
) -> List[str]:
    """Produce a list of normalized + chunked samples ready for tokenization."""

    prepared: List[str] = []
    for item in dataset:
        text = item.get(text_column, "")
        code = item.get(code_column, "") if code_column else ""
        normalized = preprocessor(text, code)
        for chunk in chunker(normalized):
            prepared.append(chunk)
    return prepared


def _tokenize_dataset(dataset: Dataset, tokenizer, text_column: str = "text") -> Dataset:
    """Tokenize the dataset into causal LM inputs."""

    def _map_batch(batch: dict) -> dict:
        return tokenizer(
            batch[text_column],
            truncation=True,
            max_length=tokenizer.model_max_length,
            return_attention_mask=True,
        )

    return dataset.map(
        _map_batch,
        batched=True,
        remove_columns=dataset.column_names,
        desc="Tokenizing",
    )


def build_training_arguments(config: TrainingConfig) -> TrainingArguments:
    gradient_accumulation_steps = config.gradient_accumulation_steps or (
        config.total_batch_size // config.micro_batch_size
    )
    return TrainingArguments(
        output_dir=config.output_dir,
        per_device_train_batch_size=config.micro_batch_size,
        per_device_eval_batch_size=config.micro_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        weight_decay=config.weight_decay,
        logging_steps=config.log_interval,
        evaluation_strategy="steps",
        eval_steps=config.eval_interval,
        save_steps=config.checkpoint_interval,
        save_total_limit=5,
        bf16=config.mixed_precision == "bf16",
        fp16=config.mixed_precision == "fp16",
        max_steps=config.num_train_steps,
        gradient_checkpointing=True,
        report_to=["tensorboard"],
        resume_from_checkpoint=config.resume_from_checkpoint,
    )


def train(config: TrainingConfig | None = None) -> None:
    """Main training orchestration function."""

    config = config or default_training_config()
    Path(config.output_dir).mkdir(parents=True, exist_ok=True)

    LOGGER.info("Preparing preprocessing pipeline…")
    preprocessor = CodePreprocessor(config.preprocessor)
    chunker = CodeChunker(config.chunker)

    LOGGER.info("Preparing datasets…")
    mixed_configs: Iterable[DatasetConfig] = config.datasets
    datasets: Iterable[MixedDataset] = load_mixed_datasets(mixed_configs)
    combined_dataset = interleave_weighted(list(datasets))

    LOGGER.info("Normalizing and chunking corpus…")
    corpus = _prepare_corpus(
        combined_dataset,
        preprocessor=preprocessor,
        chunker=chunker,
    )

    LOGGER.info("Loading tokenizer…")
    tokenizer = build_tokenizer(config.tokenizer, corpus=corpus)

    prepared_dataset = Dataset.from_dict({"text": corpus})

    tokenized = _tokenize_dataset(prepared_dataset, tokenizer=tokenizer)

    LOGGER.info("Instantiating model…")
    model = build_model(config.model, tokenizer)

    LOGGER.info("Starting trainer…")
    training_args = build_training_arguments(config)
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=data_collator,
    )

    trainer.train(resume_from_checkpoint=config.resume_from_checkpoint)
    trainer.save_model(config.output_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train()
