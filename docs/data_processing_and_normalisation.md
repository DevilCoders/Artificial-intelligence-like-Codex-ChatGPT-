# Data Processing and Normalisation

This document outlines the end-to-end transformations applied after raw harvesting to convert mixed-source materials into a uniform terminal command dataset.

## Processing stages

1. **Parsing**
   - Identify command blocks via syntax-aware parsers (Markdown code fences, shell script detectors, XML/HTML selectors).
   - Extract adjacent descriptive text to populate `description`, `usage_notes`, and `prerequisites` fields.
   - Capture code-language hints (Bash, PowerShell, CMD, Zsh, Python snippet executed from terminal).

2. **Canonicalisation**
   - Trim trailing whitespace, normalise quotes, and collapse redundant spaces.
   - Resolve environment variables to placeholder tokens (e.g., `$TARGET_HOST`), avoiding exposure of sensitive hostnames.
   - Deduplicate commands by hashing `command + normalized_context` using SHA-256.

3. **Metadata enrichment**
   - Map command to taxonomy categories (e.g., `recon`, `lateral_movement`, `incident_response`).
   - Add OS/platform compatibility using heuristics and curated pattern lists.
   - Attach required privileges (user/root/system) and estimated impact level.
   - Generate embeddings or vector fingerprints for semantic retrieval.

4. **Safety review**
   - Run classifiers to detect destructive payloads (wipers, ransomware) and label accordingly.
   - Apply redaction policies to secrets, API keys, or company-specific identifiers.
   - Route ambiguous cases to security SMEs for manual approval.

5. **Schema validation**
   - Validate each record against JSON Schema and CSV schema definitions.
   - Enforce required fields (`record_id`, `command`, `category`, `platform`, `license`, `source_url`).
   - Ensure enumerated fields (e.g., `impact_level`) contain only allowed values.

6. **Sharding**
   - Partition into deterministic shards (10–20M rows each) with stable file names.
   - Generate `MANIFEST.json` summarising row counts, byte size, compression format, and checksums.

## Tooling stack

- **Parsing**: Tree-sitter, Pygments, custom regex heuristics.
- **Processing orchestration**: Apache Spark, Ray, or Dask for large-scale workloads.
- **Metadata store**: PostgreSQL or BigQuery to hold enriched metadata and track audit status.
- **Schema enforcement**: `pandera`, `great_expectations`, or `cerberus` for data contracts.

## Data contracts

Define versioned schemas (e.g., `schemas/terminal-command-v1.json`) and publish alongside dataset releases. Consumers must pin to specific versions and acknowledge breaking changes.

## Performance considerations

- Optimise CPU by batching regex and parser operations.
- Use columnar intermediate storage (Parquet) to enable vectorised transformations.
- Compress final shards with `zstd` or `gzip` depending on downstream ecosystem compatibility.

## Observability

- Emit metrics for records processed per minute, deduplication ratio, validation failure counts, and classifier confidence distributions.
- Integrate with data quality dashboards to alert when anomalies exceed thresholds.

