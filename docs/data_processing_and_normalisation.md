# Data Processing & Normalisation

This playbook outlines the processing stages that transform raw MWRC crawls into clean, domain-partitioned JSONL shards suitable for large-scale AI training.

## Pipeline stages

1. **Ingestion staging**
   - Raw artifacts flow into `/staging/<domain>/<timestamp>/<uuid>.json`.
   - Metadata includes request headers, crawl run identifier, HTTP status, byte counts, and robots decisions.
   - Staging validations confirm UTF-8 encoding, gzip integrity, and schema compatibility before processing.

2. **Parsing & extraction**
   - HTML documents are parsed with Readability-style boilerplate removal and CSS/JS stripping.
   - Repository assets are processed using tree parsers that extract readme files, code snippets, commit metadata, and security advisories as separate payloads.
   - Vocabulary dumps are normalised to two-column CSV internally before JSONL conversion to simplify deduplication.

3. **Language identification**
   - FastText or CLD3-based detectors classify text. Records with probability <0.8 for Russian or English are quarantined for manual review.
   - Bilingual vocabulary records store both `ru` and `en` tokens; longer sentences undergo translation consistency checks using bilingual embeddings.

4. **Cleaning & enrichment**
   - Whitespace normalisation, Unicode NFC enforcement, and punctuation smoothing.
   - Redaction of secrets, credentials, or PII using regex patterns from `PipelineConfig.redact_patterns` and `PipelineConfig.pii_detectors`.
   - Token counts, readability scores, and domain-specific quality scores (e.g., security playbook classifier) are appended to metadata.
   - License classifiers predict SPDX IDs when missing, cross-checked against source registry hints.

5. **Deduplication**
   - SHA-256 hashes computed over URL + text pairs (`compute_record_hash`) underpin near-exact dedupe windows.
   - MinHash + locality-sensitive hashing run across embeddings to flag semantic near-duplicates, with heuristics to retain the highest-quality exemplar per cluster.
   - Dedup decisions (retain/drop + reason) are logged for traceability.

6. **Alignment & structuring**
   - Content is mapped into canonical schema fields (see `schema_reference.md`).
   - Domain partition keys follow `<domain>/<YYYY>/<MM>/<DD>/<shard>.jsonl[.zst]` to facilitate incremental refreshes.
   - Vocabulary lines include explicit alignment arrays for bilingual data when available.

7. **Validation**
   - JSON schema validation ensures field presence, type correctness, and allowed enumerations.
   - Language-specific validators verify Cyrillic-to-Latin ratio thresholds to avoid mislabelled entries.
   - Size checks enforce minimum character length per domain (web ≥256 chars, repos ≥80 chars per file snippet).

8. **Export & manifesting**
   - Clean records stream into JSONL writers grouped by domain and date, optionally compressed with Zstandard.
   - Manifest builder captures shard paths, record counts, byte sizes, dedupe ratios, and processing parameters.
   - Release candidate metadata and quality metrics are signed and uploaded to the artefact registry alongside shards.

## Tooling

- Python-based processors in `src.scraper.pipeline` orchestrate post-processing, leveraging asynchronous IO for throughput.
- Spark or Ray jobs can be attached during enrichment to compute embeddings or domain-specific classifiers at scale.
- Great Expectations suites enforce schema constraints, while Marquez/OpenLineage captures data lineage.

## Operational notes

- Maintain replay logs enabling deterministic reprocessing from any checkpoint.
- Quarantine buckets hold rejected or policy-blocked items for remediation.
- End-to-end latency target: <12 hours from crawl completion to release-candidate packaging for standard refresh cycles.
