# Schema Reference

This document defines the canonical record schema for the Open Source Code Corpus (OSCC). Maintain versioned copies of this
schema and increment semantic version numbers when breaking changes occur.

## Core fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `record_id` | `string` | Globally unique identifier (UUIDv7 recommended). | Yes |
| `repository_host` | `string` | Hosting provider (`github`, `gitlab`, `bitbucket`, `mirror`). | Yes |
| `repository` | `string` | Canonical `<owner>/<name>` identifier. | Yes |
| `source_url` | `string` | Permanent URL to the file or snippet (commit permalink). | Yes |
| `commit_sha` | `string` | 40-character Git commit SHA representing the snapshot. | Yes |
| `file_path` | `string` | Relative path to file within repository. | Yes |
| `programming_language` | `string` | Primary language of the snippet (ISO 639-2 or GitHub Linguist names). | Yes |
| `license_spdx` | `string` | SPDX identifier resolved for this snippet. | Yes |
| `license_status` | `string` | Enum: `approved`, `restricted`, `waived`. | Yes |
| `snippet` | `string` | Canonical code block used for training. | Yes |
| `start_line` | `int32` | Starting line number of the snippet within the file. | No |
| `end_line` | `int32` | Ending line number of the snippet within the file. | No |
| `docstring` | `string` | Associated docstring or comment providing natural-language context. | No |
| `documentation_urls` | `array[string]` | Links to documentation, READMEs, or blog posts referencing the snippet. | No |
| `tags` | `array[string]` | Taxonomy tags (language features, frameworks, domains). | No |
| `task_type` | `string` | High-level task classification (`web.backend`, `ml.training`, etc.). | Yes |
| `quality_score` | `float32` | Composite quality score (0–1) derived from validation pipeline. | Yes |
| `tests_passed` | `boolean` | Indicates whether associated tests/notebooks executed successfully. | No |
| `test_status_notes` | `string` | Additional detail for `tests_passed=false` cases. | No |
| `risk_classification` | `string` | Enum: `standard`, `security_sensitive`, `restricted`. | Yes |
| `safety_tags` | `array[string]` | Flags for safety filtering (e.g., `contains_exploit`, `pii_redacted`). | No |
| `collection_date` | `date` | ISO-8601 date when snippet was ingested. | Yes |
| `last_reviewed` | `date` | Date of latest human or automated review. | No |
| `validation_status` | `string` | Enum: `passed`, `failed`, `waived`. | Yes |
| `validation_report` | `string` | Link to detailed QA findings. | No |
| `dedupe_hash` | `string` | SHA-256 hash of normalised snippet + provenance fields. | Yes |
| `embedding_vector` | `array[float32]` | Optional vector ID or inline embedding; store externally where possible. | No |
| `ingestion_pipeline` | `string` | Identifier for pipeline configuration/version used during processing. | Yes |

## File formats

### CSV

- Use UTF-8 encoding with Unix line endings.
- Represent arrays as pipe-delimited strings (`tag1|tag2`).
- Escape embedded quotes by doubling them. Provide header row.
- Compress shards with `gzip` or `zstd`; include `.sha256` checksum files and optional `.sig` signatures.

### JSONL

- One JSON object per line, encoded in UTF-8.
- Use snake_case for field names (`documentation_urls`, `tests_passed`).
- Omit null fields to reduce file size; consumers must handle missing keys.
- Ensure numbers maintain appropriate precision (use `float32` for quality scores, `int32` for line numbers).

## Manifest specification

Each release must ship a manifest file (JSON or YAML) describing shard contents, integrity, and governance metadata. Example:

```json
{
  "dataset_name": "open-source-code-corpus",
  "schema_version": "1.1.0",
  "release": "v2024.07.0",
  "record_count": 1250000000,
  "file_formats": ["csv", "jsonl"],
  "shards": [
    {
      "path": "csv/code-000001.csv.zst",
      "records": 7500000,
      "size_bytes": 268435456,
      "checksum": "sha256:..."
    },
    {
      "path": "jsonl/code-000001.jsonl.zst",
      "records": 7500000,
      "size_bytes": 335544320,
      "checksum": "sha256:..."
    }
  ],
  "quality_report": "reports/quality-v2024.07.0.html",
  "compliance_report": "reports/compliance-v2024.07.0.pdf"
}
```

## Schema change management

- Propose changes through architecture decision records (ADRs) with downstream impact analysis.
- Provide migration guides and backward-compatible views (e.g., SQL views, transformation scripts) for at least two release
  cycles.
- Version schema definitions in source control and publish change logs alongside release notes.
