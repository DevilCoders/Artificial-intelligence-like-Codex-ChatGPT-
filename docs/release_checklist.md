# Release Checklist

Use this checklist to certify each Open Source Code Corpus (OSCC) release candidate. All items must be completed or waived with
executive approval before public or internal distribution.

## 1. Planning & scope

- [ ] Release scope agreed upon (languages, new repositories, enrichment features).
- [ ] Release version assigned following `vYYYY.MM.X` pattern and recorded in change log.
- [ ] Rollback strategy defined, including previous release restore point and communication plan.

## 2. Data readiness

- [ ] Source registry updated, reviewed, and tagged for this release.
- [ ] All ingestion pipelines completed successfully with logs archived.
- [ ] Snapshot manifest generated with commit SHAs, timestamps, and storage URIs.

## 3. Processing & enrichment

- [ ] Normalisation jobs passed automated validation (schema, hashing, formatting).
- [ ] Static analysis and security scanners executed; results triaged and documented.
- [ ] Embeddings/features generated and linked via feature-store IDs (if applicable).

## 4. Quality assurance

- [ ] Quality dashboard reviewed; key metrics meet thresholds (duplicate rate, quality score, language coverage).
- [ ] Human review samples completed with no blocking issues.
- [ ] Regression comparison against prior release (quality deltas, new incident types) completed.

## 5. Compliance & legal

- [ ] License inventory reconciled; attribution packages generated and reviewed by legal.
- [ ] Sensitive-content review completed; restricted assets labelled or removed.
- [ ] Takedown inbox checked; outstanding requests resolved.

## 6. Packaging & distribution

- [ ] CSV and JSONL shards generated with deterministic naming and partitioning.
- [ ] Checksums (`.sha256`) and signatures produced for all artefacts.
- [ ] Release manifest validated against schema and uploaded to artefact registry.
- [ ] Landing page/README updates prepared with new release notes.

## 7. Approvals

- [ ] Data engineering sign-off
- [ ] ML engineering sign-off
- [ ] Legal/compliance sign-off
- [ ] Security/trust sign-off
- [ ] Executive sponsor sign-off (required for public releases)

## 8. Post-release

- [ ] Monitoring alerts configured for consumer pipelines.
- [ ] Support rota updated for launch window.
- [ ] Retro meeting scheduled within two weeks of release.
