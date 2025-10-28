"""Utilities for mixing natural language and source code datasets."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional

from datasets import Dataset, DatasetDict, concatenate_datasets, load_dataset

from .config import DatasetConfig


@dataclass
class MixedDataset:
    """A dataset that samples examples proportionally from several sources."""

    dataset: Dataset
    name: str
    weight: float


def _load_single_dataset(config: DatasetConfig) -> Dataset:
    """Load a dataset split according to the provided ``DatasetConfig``."""

    data = load_dataset(config.name, config.subset, split=config.split)
    if isinstance(data, DatasetDict):  # Defensive; ``split`` usually prevents this.
        data = data[config.split]
    columns_to_keep: List[str] = [config.text_column]
    if config.code_column and config.code_column not in columns_to_keep:
        columns_to_keep.append(config.code_column)
    data = data.remove_columns([col for col in data.column_names if col not in columns_to_keep])

    rename_mapping = {config.text_column: "text"}
    if config.code_column:
        rename_mapping[config.code_column] = "code"
    data = data.rename_columns(rename_mapping)
    if "code" not in data.column_names:
        data = data.add_column("code", [""] * len(data))
    return data


def load_mixed_datasets(configs: Iterable[DatasetConfig]) -> List[MixedDataset]:
    """Load and wrap each dataset with its respective sampling weight."""

    mixed: List[MixedDataset] = []
    for cfg in configs:
        dataset = _load_single_dataset(cfg)
        mixed.append(MixedDataset(dataset=dataset, name=cfg.name, weight=cfg.weight))
    return mixed


def interleave_weighted(datasets: List[MixedDataset]) -> Dataset:
    """Return a dataset that interleaves multiple sources by weight.

    ``datasets`` is expected to be small; the operation loads each dataset fully
    into memory. For large-scale training you should rely on streaming mode from
    ``datasets`` by setting ``streaming=True`` in the configs, which would
    require a slightly different implementation.
    """

    total_weight = sum(ds.weight for ds in datasets)
    if total_weight <= 0:
        raise ValueError("At least one dataset must have a positive weight.")

    # Compute the proportion of each dataset and repeat rows accordingly.
    proportions = [ds.weight / total_weight for ds in datasets]
    max_len = max(len(ds.dataset) for ds in datasets)
    repeated = []
    for ds, proportion in zip(datasets, proportions):
        repeat_count = max(1, math.ceil(proportion * len(datasets) * max_len / len(ds.dataset)))
        repeated.append(concatenate_datasets([ds.dataset] * repeat_count))
    combined = concatenate_datasets(repeated)
    return combined.shuffle(seed=42)


def iter_dataset_text(dataset: Iterable[dict], text_column: str = "text", code_column: Optional[str] = "code") -> Iterator[str]:
    """Yield concatenated text/code strings ready for tokenization."""

    for item in dataset:
        text = item.get(text_column, "")
        code = item.get(code_column or "", "") if code_column else ""
        if text and code:
            yield f"<nl>{text}\n<code>\n{code}"
        elif code:
            yield code
        else:
            yield text
