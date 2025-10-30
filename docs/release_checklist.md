# Release Checklist

Use this checklist to validate readiness before shipping an MWRC release.

## Preparation

- [ ] Release scope approved, including domain additions/removals and schema changes.
- [ ] Pipeline configuration (`PipelineConfig` export) committed with version tag.
- [ ] Source registry diff reviewed by data engineering, linguists, and compliance.
- [ ] Resource plan confirmed (compute budget, proxy capacity, storage quotas).

## Collection phase

- [ ] All crawl jobs completed successfully with retry budgets within limits.
- [ ] Robots.txt logs reviewed; exceptions documented and approved.
- [ ] GitHub/GitLab API usage within quota; tokens rotated post-run.
- [ ] Vocabulary dumps verified against upstream checksums.

## Processing & QA

- [ ] Normalisation jobs completed; staging buckets empty except for quarantined items.
- [ ] Deduplication metrics within thresholds (<5% duplicates remaining).
- [ ] Language distribution validated (≥40% Russian, ≥40% English, ≤20% other).
- [ ] Sensitive-content filters executed; manual reviews signed off.
- [ ] Schema validation reports archived; no blocking errors outstanding.

## Packaging

- [ ] JSONL shards generated with deterministic naming and optional Zstandard compression.
- [ ] Manifest created with path, record counts, byte sizes, and config snapshot.
- [ ] Checksums (SHA-256) generated per shard and stored in release directory.
- [ ] Sample records exported for documentation (per domain, per language).

## Compliance & documentation

- [ ] Licensing attestations compiled; attribution text verified.
- [ ] Takedown queue reviewed; outstanding requests resolved or deferred with approval.
- [ ] Transparency report drafted (quality metrics, known limitations, bias remediation).
- [ ] `/docs` updates merged; change log entry drafted.

## Launch

- [ ] Artefacts uploaded to distribution channels; permissions validated.
- [ ] Consumers notified via mailing list/slack with summary + breaking changes.
- [ ] Rollback plan rehearsed; previous stable release accessible.
- [ ] Post-launch monitoring enabled (metrics dashboards, alerting rules).
