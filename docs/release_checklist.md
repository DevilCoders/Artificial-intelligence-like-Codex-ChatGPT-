# Release Checklist

Use this checklist to certify that a dataset build is production-ready. Track completion via issue tracker or release management tool.

## Pre-release

- [ ] Source registry refreshed and mirrors up to date.
- [ ] New or deprecated sources reviewed by security and legal stakeholders.
- [ ] Processing pipeline executed with reproducible configuration hash recorded.
- [ ] Validation suite completed with zero `P0`/`P1` issues.
- [ ] Manual review sample signed off by security SMEs.
- [ ] Compliance review sign-off captured (legal, privacy, security).
- [ ] Release notes drafted with summary of changes and known limitations.

## Packaging

- [ ] CSV and JSONL shards generated with deterministic filenames and compression.
- [ ] `MANIFEST.json` includes row counts, schema version, SHA-256 checksums, and compression metadata.
- [ ] Attribution bundle (`ATTRIBUTION.md`, license manifests) assembled.
- [ ] Documentation in `/docs` updated (schema, pipeline, QA, compliance).
- [ ] Checksums verified in staging environment.

## Publication

- [ ] Artefacts uploaded to primary distribution bucket with immutable retention policy.
- [ ] Optional mirrors (Hugging Face, academic repos) synced.
- [ ] Access controls and API tokens validated.
- [ ] Release announcement communicated to stakeholders (email, Slack, changelog).
- [ ] Support rotation briefed on new release contents.

## Post-release

- [ ] Monitoring dashboards updated with new release metrics.
- [ ] Feedback intake (issue template, form) ready for consumer reports.
- [ ] Schedule post-mortem or retrospective within two weeks.
- [ ] Archive raw processing logs and validation reports.

