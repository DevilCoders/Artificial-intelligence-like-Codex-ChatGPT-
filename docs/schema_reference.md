# Schema Reference

This document defines the canonical record schema for the Terminal Command Intelligence dataset. Maintain versioned copies of this schema and update semantic version when breaking changes occur.

## Core fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `record_id` | `string`/`int64` | Globally unique identifier (UUIDv7 recommended). | Yes |
| `command` | `string` | Canonical terminal command string. | Yes |
| `category` | `string` | Primary task classification (e.g., `recon`, `blue_team`). | Yes |
| `subcategories` | `array[string]` | Additional hierarchical tags. | No |
| `platform` | `string` | Supported OS or environment (`linux`, `windows`, `macos`, `cloud/aws`, etc.). | Yes |
| `execution_context` | `string` | Context required to run command (shell, interpreter, container). | No |
| `description` | `string` | Human-readable explanation of command purpose. | Yes |
| `prerequisites` | `array[string]` | Required packages, permissions, or network conditions. | No |
| `impact_level` | `string` | Risk tier: `low`, `medium`, `high`, `critical`. | Yes |
| `safety_notes` | `string` | Mitigations or warnings for ethical usage. | No |
| `source_url` | `string` | Canonical upstream reference. | Yes |
| `source_commit` | `string` | Commit hash or version identifier for reproducibility. | No |
| `license` | `string` | SPDX identifier for licensing. | Yes |
| `license_notes` | `string` | Additional obligations or attribution instructions. | No |
| `collection_date` | `date` | ISO-8601 date when record was ingested. | Yes |
| `last_verified` | `date` | Date the command was last executed/validated. | No |
| `validation_status` | `string` | Enum: `passed`, `failed`, `waived`. | Yes |
| `validation_report` | `string` | Link to detailed QA findings. | No |
| `dedupe_hash` | `string` | SHA-256 hash of canonical command + context. | Yes |
| `embedding_vector` | `array[float32]` | Optional vector for semantic retrieval (stored externally). | No |

## File formats

### CSV

- Use UTF-8 encoding with Unix line endings.
- Represent arrays as pipe-delimited strings (`tag1|tag2`).
- Provide header row and quote fields containing commas.
- Compress shards with `gzip` or `zstd` and include `.sha256` checksum files.

### JSONL

- One JSON object per line, encoded in UTF-8.
- Use camelCase or snake_case consistently per schema version (recommended: snake_case).
- Omit null fields to reduce file size; consumers must handle missing keys.

## Manifest specification

Each release must ship a manifest file (JSON or YAML) containing:

```json
{
  "dataset_name": "terminal-command-intelligence",
  "schema_version": "1.0.0",
  "release": "v2024.06.0",
  "record_count": 1000000000,
  "file_format": ["csv", "jsonl"],
  "files": [
    {
      "path": "csv/commands-000001.csv.zst",
      "records": 20000000,
      "checksum": "sha256:...",
      "size_bytes": 123456789
    }
  ],
  "validation_report": "reports/validation-v2024.06.0.html"
}
```

## Schema change management

- Document proposed changes in architecture decision records (ADRs).
- Provide migration guides for downstream consumers.
- Support at least one previous schema version for two release cycles.

