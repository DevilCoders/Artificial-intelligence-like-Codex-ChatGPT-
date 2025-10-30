# Open Source Code Corpus Release Overview

This overview summarises the structure, scope, and release strategy for the Open Source Code Corpus (OSCC). The corpus targets
billions of high-quality code examples sourced from public GitHub, GitLab, and other permissively licensed repositories so that
data and ML engineers can train professional-grade foundation and instruction-tuned models.

## Objectives

- **Diverse coverage**: Capture popular and long-tail programming languages, frameworks, build systems, and scripting
  environments relevant to application, infrastructure, data, and security engineering work.
- **Production readiness**: Pair every snippet with rich metadata covering provenance, licensing, execution requirements,
  documentation signals, and QA checkpoints required by enterprise consumers.
- **Ethical governance**: Respect original authorship, adhere to licensing obligations, and gate potentially sensitive content
  (e.g., secrets, malware, or exploit kits) through policy filters.
- **Scalable refreshes**: Provide a repeatable pipeline capable of refreshing billions of records on a quarterly cadence without
  manual intervention.

## Deliverables

1. **Dataset shards** produced in CSV and JSONL formats, split into deterministic multi-gigabyte files (e.g.,
   `code-000001.jsonl.zst`) with manifest and checksum files.
2. **Schema definitions** describing the canonical field contract, enumerations, and optional enrichments used across formats.
3. **Ingestion & processing pipeline** assets (jobs, configs, notebooks) to reproduce the corpus from raw mirrors and new
   candidate repositories.
4. **Quality, evaluation, and compliance reports** demonstrating license validation, deduplication, static analysis results,
   and release gating decisions.
5. **Release documentation** (this directory) that enables downstream teams to operate, audit, and extend the corpus.

## Release milestones

| Milestone | Description | Exit criteria |
|-----------|-------------|---------------|
| Source registry | Curate allow-listed organisations, repositories, and mirrors; snapshot commit ranges. | Registry stored in configuration repo with licensing metadata and sync automation. |
| Normalisation | Convert raw files into canonical records with consistent metadata, formatting, and snippet extraction. | Validation suite passes, schema contracts satisfied, canonical hashes produced. |
| Enrichment | Add embeddings, tests, language/tool tags, dependency manifests, and code intelligence signals. | Coverage thresholds met (>95% records with language, license, and quality metrics). |
| Compliance | Execute legal, privacy, and security reviews; log waivers. | No blocking issues; approved distribution scope stored in release dossier. |
| Packaging | Publish release candidate shards, manifests, and checksums to artefact registry. | Release candidate signed, integrity verified, and immutably stored. |
| Documentation | Finalise `/docs` playbooks, public release notes, and landing page. | Documentation review sign-off completed and archived. |

## Stakeholders

- **Data engineering**: Own ingestion, transformation, storage, and refresh automation.
- **ML engineering**: Define downstream consumption requirements, provide schema feedback, and benchmark releases.
- **Developer relations**: Coordinate with upstream communities and communicate attribution requirements.
- **Legal & compliance**: Approve licensing, distribution rights, and data retention policies.
- **Security & trust**: Operate sensitive-content classifiers, monitor misuse, and respond to takedown requests.

## Versioning strategy

- Tag public releases using year.month.sequence semantics (e.g., `v2024.07.0`).
- Maintain a change log enumerating new sources, schema changes, and quality improvements.
- Provide patch releases for urgent fixes and delta manifests describing added/removed shards.

## Distribution channels

- Primary: internal artefact registry (S3, GCS, Azure Blob, or self-hosted object storage) with signed manifests.
- Secondary: optional mirrors on academic or industry dataset hubs; always include attribution and usage guidelines.
- Ensure network egress budgets and API quota considerations for downstream continuous-training consumers.

## Support & maintenance

- Establish quarterly refresh cadence with automated anomaly detection for licensing drift, quality regressions, and duplicate
  rates.
- Maintain on-call rotations and runbooks for ingestion failures, security escalations, and takedown requests.
- Track consumer issues through ticketing system with defined SLAs and publish quarterly health reviews.
