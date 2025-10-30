# Schema Reference

The MWRC JSONL schema ensures consistent metadata across domains while allowing domain-specific enrichments.

Each JSONL line is a UTF-8 encoded JSON object. Top-level fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Deterministic UUID or hash representing the record. Typically derived from `hash` in `src.scraper.utils`. |
| `domain` | string | ✓ | Logical partition (`web`, `github`, `gitlab`, `vocabulary`). |
| `url` | string | ✓ | Canonical URL or repository identifier. |
| `language` | string | ✓ | ISO-639-1 or composite code (`ru`, `en`, `ru-en`). |
| `text` | string | ✓ | Cleaned textual content ready for model ingestion. |
| `tokens` | integer | ✓ | Token count computed using release-approved tokenizer. |
| `license` | string | ✓ | SPDX identifier or `custom:<slug>` when no SPDX equivalent exists. |
| `source_metadata` | object | ✓ | Provenance details (see below). |
| `quality` | object | ✓ | Quality metrics (per-domain). |
| `safety` | object | ✓ | Safety classifier outputs and redaction markers. |
| `embeddings` | object | ✗ | Optional vector references (e.g., path to embedding artefact). |
| `alignment` | object | ✗ | Bilingual alignment payload for vocabulary entries. |

## `source_metadata`

Common keys:

- `retrieved_at` (string, ISO-8601)
- `crawl_run_id` (string)
- `source` (string, e.g., hostname or repository slug)
- `commit_sha` (string, Git domains only)
- `branch` (string, Git domains only)
- `author` (string, when available)
- `attribution` (string, human-readable attribution statement)

## `quality`

Common keys:

- `readability` (float 0-1)
- `toxicity` (float 0-1, lower is safer)
- `domain_specific` (object) capturing classifier outputs, e.g., `security_relevance`
- `dedupe_rank` (integer) referencing dedupe cluster ordering

## `safety`

Common keys:

- `pii_flag` (boolean)
- `pii_detectors` (array of strings) listing triggered detectors (empty if `false`)
- `security_tier` (string: `public`, `sensitive`, `restricted`)
- `redactions` (array of objects with `pattern` and `replacement`)

## Domain-specific extensions

### Web (`domain = "web"`)

- `source_metadata.site_category` (e.g., `documentation`, `blog`, `forum`)
- `quality.page_depth` (integer)
- `quality.language_confidence` (float 0-1)

### GitHub/GitLab (`domain in {"github", "gitlab"}`)

- `source_metadata.repo_topics` (array of strings)
- `source_metadata.file_path` (string)
- `source_metadata.license_path` (string)
- `quality.code_language` (string, programming language detection)
- `quality.tests_present` (boolean)
- `safety.security_finding` (string, optional manual triage notes)

### Vocabulary (`domain = "vocabulary"`)

- `alignment.source_tokens` (array of strings, Russian)
- `alignment.target_tokens` (array of strings, English)
- `alignment.part_of_speech` (string, e.g., `noun`, `verb`)
- `quality.frequency_bucket` (string: `common`, `specialised`, `rare`)

## File layout

- Shards are stored as `jsonl/<domain>/<YYYY>/<MM>/<domain>-<YYYYMMDD>-<shard>.jsonl` and optionally `.jsonl.zst` if compression enabled.
- Each release includes `jsonl/<domain>/LATEST` symlink or pointer file referencing the newest shard set.
- Manifests live in `manifests/manifest-<timestamp>.json` referencing shards with relative paths.

## Schema management

- Schema changes follow semantic versioning. Store JSON Schema drafts in `schemas/mwrc-v<major>.<minor>.json` (not yet included by default).
- Provide migration scripts for downstream consumers when removing or renaming fields.
- Unit tests in CI validate sample shards against the JSON Schema to prevent regressions.
