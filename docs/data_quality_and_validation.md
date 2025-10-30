# Data Quality and Validation Playbook

Ensuring dataset reliability is critical for downstream model performance. This playbook defines the validation strategy for the Terminal Command Intelligence dataset.

## Quality pillars

1. **Accuracy**: Commands perform the described action and metadata fields are correct.
2. **Completeness**: Required fields populated; optional enrichments available at target coverage.
3. **Consistency**: Standardised formatting, taxonomy, and casing across shards.
4. **Timeliness**: Dataset reflects recent tooling changes and patch levels.
5. **Safety**: Potentially destructive commands are flagged with appropriate warnings.

## Automated validation suite

| Check | Description | Tooling |
|-------|-------------|---------|
| Schema validation | Verify CSV/JSONL records conform to schema. | `great_expectations`, `pandera` |
| Deduplication | Detect near-duplicate commands via MinHash/LSH. | Spark UDFs, `datasketch` |
| License compliance | Ensure only approved licenses present. | Custom whitelist validator |
| Metadata completeness | Enforce coverage thresholds for `platform`, `category`, `impact_level`. | SQL dashboards |
| Safety classifier | Score commands for destructive potential. | Transformer-based classifier |
| Language detection | Confirm command belongs to supported shell/OS. | FastText, heuristics |

## Manual review workflow

1. Sample commands by risk tier (`red`, `yellow`, `green`).
2. Assign reviewers with relevant OS/security expertise.
3. Collect feedback in issue tracker (Jira, Linear, or GitHub Projects).
4. Track acceptance metrics (pass rate, turnaround time) each release.

## Regression testing

- Maintain historical baselines for deduplication ratio, failure counts, and classifier distributions.
- Block releases if metrics deviate beyond agreed thresholds (e.g., >5% drop in metadata completeness).

## Data observability

- Stream validation results to a central warehouse (e.g., BigQuery) for reporting.
- Build Looker/Grafana dashboards covering:
  - Records ingested per source.
  - Validation failures by category.
  - Top flagged licenses requiring legal review.
  - Safety classifier trend lines.

## Issue management

- Severity levels: `P0` (blocker), `P1` (major), `P2` (minor).
- Document mitigation steps for each severity level and assign owners.
- Publish weekly QA status updates summarising open defects and release impact.

