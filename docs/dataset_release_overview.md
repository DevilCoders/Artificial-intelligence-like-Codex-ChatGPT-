# Multilingual Web & Repository Corpus (MWRC) Overview

The Multilingual Web & Repository Corpus (MWRC) delivers a professional-grade release of web, GitHub, GitLab, and bilingual vocabulary content aligned to Russian and English AI training scenarios. It is engineered to scale to billions of high-quality records through automated sourcing, rigorous normalization, and comprehensive governance, enabling enterprise AI teams to build domain-specialized assistants for security operations, infrastructure engineering, and cross-lingual collaboration.

## Objectives

- **Massive multilingual reach**: Capture Russian and English materials across websites, wikis, blogs, developer portals, and open-source repositories to balance cultural nuance with global engineering best practices.
- **Domain coverage**: Track security (red/blue teaming), operations, networking, DevSecOps, and penetration-testing playbooks while incorporating neutral vocabulary corpora to ground translation models.
- **Operational resilience**: Support continuous refreshes, automated anomaly detection, and reproducible manifests required for downstream compliance certification and auditability.
- **Ethical governance**: Respect robots.txt, licensing, takedown requests, and sensitive-content policies while providing transparent provenance metadata.

## Deliverables

1. **Domain-partitioned JSONL shards** with deterministic naming (`<domain>/<domain>-<shard>.jsonl[.zst]`) including hash digests and per-record metadata such as license, language, quality scores, and crawl timestamps.
2. **Manifest and lineage artifacts** providing checksums, record counts, generation parameters, and upstream mirrors for every release cut.
3. **Scraper orchestration assets** (configuration dataclasses, async crawlers, pipeline runner) capable of reproducing the corpus across distributed workers and cloud regions.
4. **Cleaning and enrichment playbooks** detailing HTML parsing, code extraction, bilingual alignment, translation heuristics, deduplication, and safety filters.
5. **Quality, compliance, and release documentation** summarizing validation metrics, policy waivers, incident responses, and launch readiness decisions.

## Release milestones

| Milestone | Description | Exit criteria |
|-----------|-------------|---------------|
| Source discovery | Curate allow-listed domains, organizations, mirrors, and vocabulary datasets with licensing clearance. | Source registry published with license classification, contact routes, and automated freshness checks. |
| Crawl orchestration | Execute distributed scrapers with adaptive rate limiting, rotating proxies, and failure recovery. | 99.5% job success, SLA-compliant response times, and automated retry exhaustion reporting. |
| Normalisation & enrichment | Convert raw artifacts to canonical JSONL records with language tags, dedup hashes, embeddings, and quality scores. | Schema validation passes; >98% records with language detection confidence ≥0.9; dedup ratio <5%. |
| Compliance review | Run privacy, security, and legal reviews including manual sampling of high-risk segments. | Compliance sign-off stored in release dossier; takedown workflow rehearsed. |
| Packaging & distribution | Produce signed manifests, publish shards to artefact registry, and notify downstream teams. | Integrity checks succeed; release notes and checksums available via catalog; rollback plan tested. |
| Documentation & enablement | Finalize `/docs` playbooks, consumer onboarding guides, and dataset change log. | Documentation approved by data governance; enablement session delivered to ML platform teams. |

## Stakeholders

- **Data engineering**: Own orchestrator implementation, cloud infrastructure, and pipeline observability.
- **ML engineering**: Provide schema feedback, evaluate dataset quality, and integrate with pretraining/finetuning workflows.
- **Localization linguists**: Review bilingual alignment quality, lexicon coverage, and cultural nuance for Russian ↔ English content.
- **Security & trust**: Operate sensitive-content classifiers, manage exploit/zero-day policies, and steward takedown responses.
- **Legal & compliance**: Validate licensing, export controls, and regional data-residency requirements.

## Versioning strategy

- Tag public releases as `mwrc-YYYY.MM.iteration` (e.g., `mwrc-2024.07.0`).
- Maintain semantic change logs capturing new domains, schema migrations, policy updates, and major quality deltas.
- Offer delta manifests for hotfix builds and maintain `LATEST` pointers for automated consumers.

## Distribution channels

- Primary: internal object storage (S3/GCS/Azure Blob) with immutability, signed URLs, and inventory exports.
- Secondary: curated research mirrors (e.g., academic partnerships) with scoped subsets and rate-limit controls.
- Optional: sanitized subsets for public evaluation hosted via Hugging Face Datasets or Open Data portals.

## Support & maintenance

- Run continuous monitoring on crawl throughput, dedup ratios, translation accuracy, and safety classifier drift.
- Provide on-call coverage for ingestion failures and data-quality regressions with documented runbooks.
- Publish quarterly health reports, consumer satisfaction surveys, and roadmap updates.
