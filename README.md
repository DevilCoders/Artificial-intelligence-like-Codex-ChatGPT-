# Artificial-intelligence-like-Codex-ChatGPT-

An advanced custom AI model template with enhanced capabilities inspired by OpenAI Codex. This repository provides configuration and training utilities for building a large language model capable of understanding both natural language and source code across numerous programming languages while pairing it with an enterprise-grade multilingual data factory.

## Features

- **Hybrid training corpora**: Mix billions of lines of open-source code (Python, JavaScript, Go, Perl, PHP, Ruby, Swift, TypeScript, Shell, and more) with curated natural-language corpora.
- **Large context window**: Configure tokenizers for ~14 KB Python code context to keep more of the active file in memory—over 3× GPT-3's 4 KB window.
- **Modern architecture**: Bootstraps from high-quality open checkpoints like `bigcode/starcoderbase` and enables flash attention and gradient checkpointing for efficiency.
- **Extensible pipeline**: Modular configuration objects let you adjust datasets, tokenizer, model, and training hyperparameters with ease.
- **First-class text/code processing**: Built-in preprocessor, chunker, tokenizer, encoder, and decoder components make it easy to experiment with custom data prep and model architectures without leaving the template.
- **Multilingual web and repository harvesting**: New scraping and normalization modules orchestrate web, GitHub, GitLab, and bilingual vocabulary pipelines to deliver professional-grade JSONL shards partitioned by domain.

## Repository structure

```
src/
  scraper/
    config.py      # Pipeline configuration covering rate limits, partitions, and storage
    crawlers.py    # Async crawlers for web domains, GitHub, GitLab, and vocabulary feeds
    pipeline.py    # End-to-end orchestration, export, and manifest creation helpers
    utils.py       # Hashing, redaction, and quality helpers shared across the pipeline
  training/
    config.py      # Declarative configuration dataclasses (datasets, tokenizer, encoder/decoder, etc.)
    data.py        # Dataset loading and weighting helpers
    preprocess.py  # Normalises NL/code pairs before tokenisation
    chunker.py     # Splits long documents into context-sized windows
    tokenizer.py   # Byte-level BPE training utilities
    encoder.py     # Lightweight Transformer encoder backbone
    decoder.py     # Causal LM head and weight tying logic
    modeling.py    # Tokenizer/model builders for pretrained + custom stacks
    train.py       # End-to-end training orchestration (preprocess → chunk → tokenise)
docs/
  *.md             # Dataset release playbooks, schema references, checklists, governance
data/
  jsonl/
    web/           # Sample shards of multilingual web content
    github/        # Sample shards of GitHub repositories
    gitlab/        # Sample shards of GitLab repositories
    vocabulary/    # Sample shards of bilingual vocabulary tables
  manifests/       # Example manifest produced by the scraper pipeline
```

## Quickstart

1. **Install dependencies**

   ```bash
   pip install -U "datasets>=2.17" "transformers[torch]>=4.38" accelerate tensorboard
   ```

2. **Review the default training configuration**

   ```python
   from src.training.config import default_training_config

   cfg = default_training_config()
   print(cfg)
   ```

   Adjust dataset weights, add additional public corpora, or point to organization-internal mirrors as needed.

3. **Launch training**

   ```bash
   python -m src.training.train
   ```

   The default configuration interleaves GitHub code (`codeparrot/github-code`) and high-quality natural language (`the_pile`). Customize the dataset list to include additional sources, such as StackOverflow dumps or curated documentation corpora.

4. **Harvest multilingual corpora**

   ```python
   import asyncio
   from pathlib import Path
   from datetime import timedelta

   from src.scraper import (
       GitCrawlerConfig,
       PipelineConfig,
       RateLimit,
       ScraperPipeline,
       ScraperTargets,
       VocabularySource,
       WebsiteCrawlerConfig,
   )

   config = PipelineConfig(
       website=WebsiteCrawlerConfig(
           allowed_domains=("infosec.example", "linux-handbook.example"),
           rate_limit=RateLimit(300, timedelta(minutes=1)),
       ),
       github=GitCrawlerConfig(
           organisations=("opensecurity", "cloud-hardening"),
           token_env_var="GITHUB_TOKEN",
       ),
       gitlab=GitCrawlerConfig(
           organisations=("redteam-labs",),
           token_env_var="GITLAB_TOKEN",
       ),
       vocabulary_sources=(
           VocabularySource(provider="wiktionary", url="https://example.org/dump"),
       ),
       storage=ScraperTargets(
           raw_root=Path("artifacts/raw"),
           staging_root=Path("artifacts/staging"),
           release_root=Path("artifacts/release"),
       ),
   )

   pipeline = ScraperPipeline(config)
   manifest_path = asyncio.run(pipeline.execute_and_export())
   print("Exported manifest", manifest_path)
   ```

5. **Monitoring**

   Training logs stream to TensorBoard. Start a dashboard with:

   ```bash
   tensorboard --logdir checkpoints/codex-like
   ```

## Customization tips

- **Tokenizer**: Provide a tokenizer checkpoint optimized for code (e.g., StarCoder or CodeLLaMA), or enable `tokenizer.use_custom=True` to train the repository's byte-level BPE tokenizer from scratch. The config automatically adds special tokens for natural-language/code demarcation and enforces a 14,336-token context length.
- **Preprocessing & chunking**: Tweak `preprocessor` and `chunker` sections of the config to normalise whitespace, strip comments, or change sliding-window sizes before tokenisation.
- **Model size**: Swap `bigcode/starcoderbase` for larger or smaller architectures that fit your compute budget, or set `model.use_custom_architecture=True` to instantiate the built-in encoder/decoder stack.
- **Scaling**: Integrate with [Hugging Face Accelerate](https://github.com/huggingface/accelerate) for distributed training on multi-GPU or TPU clusters. Adjust `total_batch_size` and `micro_batch_size` to saturate hardware.
- **Data governance**: Ensure that all included code repositories comply with your licensing and compliance requirements before use.

## Disclaimer

This project provides a reproducible template but does **not** ship the actual training datasets or trained checkpoints. You are responsible for sourcing data, validating licenses, and provisioning the large-scale compute necessary to train an AI coding assistant.

### Dataset release toolkit

The `/docs` directory now includes production-grade guidance for the Multilingual Web & Repository Corpus (MWRC)—a professional release comprising billions of multilingual website captures, GitHub/GitLab repositories, and bilingual Russian/English vocabularies. The playbooks walk through sourcing, distributed scraping, content cleaning, metadata enrichment, QA, and compliance workflows tailored for JSONL domain-partitioned shards. Sample JSONL shards under `/data/jsonl` demonstrate schema expectations, and a manifest in `/data/manifests` illustrates the delivery contract for downstream consumers.
