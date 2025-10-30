# Data Processing & Normalisation

This guide outlines how to transform mirrored repositories into high-quality records aligned with the Open Source Code Corpus
(OSCC) schema. The processing pipeline scales to billions of snippets by leveraging distributed compute, deterministic
normalisation, and rigorous tracking.

## 1. Preparation

1. **Input manifest**: Consume the source registry produced during data collection. Each entry must include repository host,
   commit SHA or tag, license, and ingestion priority.
2. **Processing configuration**: Parameterise jobs with language-specific extractors, maximum snippet lengths, comment handling
   policies, and build/test execution toggles.
3. **Environment isolation**: Run transformations inside sandboxed containers with pinned dependencies to ensure reproducibility.

## 2. Parsing & extraction

1. **Language detection**: Use tree-sitter or linguist-derived heuristics to confirm declared languages and override ambiguous
   file types.
2. **AST-based chunking**: Traverse abstract syntax trees to extract functions, classes, and relevant blocks. Capture the
   minimal context required for readability (imports, docstrings, type hints).
3. **Docstring & comment capture**: Preserve docstrings, comments, and README references that explain the snippet's purpose or
   usage.
4. **Context linking**: Attach surrounding metadata such as dependency files, tests, or configuration snippets that reference the
   code block.

## 3. Normalisation

1. **Whitespace & formatting**: Normalise indentation, line endings, and trailing whitespace while respecting language-specific
   conventions.
2. **Encoding**: Enforce UTF-8 encoding and replace non-printable characters with escapes.
3. **Secret scrubbing**: Redact detected secrets with placeholder tokens and attach remediation notes in metadata.
4. **License propagation**: Resolve repository- and file-level licenses; inherit or override according to SPDX metadata.
5. **Attribution fields**: Populate repository owner, project name, commit hash, and source URLs for each record.
6. **Hashing**: Generate canonical `dedupe_hash` values on the cleaned snippet plus key metadata.

## 4. Enrichment

1. **Static analysis**: Run linters, formatters, and security scanners (Bandit, Semgrep, ESLint, gosec) to generate quality and
   risk signals.
2. **Execution metadata**: For repositories with tests/examples, execute targeted test suites or notebook cells inside secure
   sandboxes; record success/failure and logs.
3. **Embedding generation**: Produce language model embeddings for semantic search and curriculum design; store vectors in
   separate feature stores referenced via IDs.
4. **Taxonomy tagging**: Map snippets to task ontologies (e.g., `web.backend`, `ml.training`, `iac.terraform`, `sec.exploit`) and
   cross-reference with framework/library tags.

## 5. Validation & checks

1. **Schema validation**: Enforce schema contracts using tools like Great Expectations or pydantic models.
2. **Deduplication**: Identify and collapse duplicates within and across repositories using canonical hashes, fuzzy matching, and
   similarity search.
3. **Quality scoring**: Combine static analysis, test pass rates, documentation coverage, and code review heuristics into a
   composite quality score per record.
4. **Manual review**: Sample high-risk categories (security, cryptography, low-quality) for subject-matter expert review and
   capture adjudication outcomes.

## 6. Output formatting

1. **Partitioning**: Write records into deterministic shards (e.g., 5–10M records per file) with balanced language distribution.
2. **Compression & checksums**: Compress outputs with `zstd` or `gzip`, generate SHA-256 checksums, and sign manifests.
3. **Metadata sidecars**: Produce auxiliary files containing statistics (language breakdown, license mix, quality distributions)
   and processing lineage.

## 7. Observability & lineage

- Emit structured logs for every record, capturing pipeline stage, duration, success/failure, and error messages.
- Populate a central lineage catalogue linking source commits to output shards and validation artefacts.
- Store pipeline configurations and container images with content-addressable identifiers for reproducibility audits.
