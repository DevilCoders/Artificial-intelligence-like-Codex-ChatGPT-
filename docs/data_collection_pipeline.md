# Data Collection Pipeline

This playbook documents how to source and maintain the Open Source Code Corpus (OSCC), targeting billions of code examples across
GitHub, GitLab, community mirrors, and documentation portals. The pipeline emphasises reproducibility, compliance, and scale.

## 1. Source discovery & registry

1. **Seed allow-list**: Start with permissively licensed organisations (Apache, MIT, BSD, CC-BY) and high-signal repositories
   (official SDKs, security tooling, infrastructure-as-code, research implementations).
2. **Metadata harvesting**: Use platform APIs (GitHub, GitLab), BigQuery GH Archive, and curated lists to collect repository
   metadata: stars, primary language, topics, forks, license, archival status.
3. **Risk scoring**: Apply heuristics to exclude repositories with malware, leaked secrets, personal data, or restrictive
   licenses. Maintain risk justification logs for each decision.
4. **Registry store**: Persist the allow-list in version-controlled configuration (YAML/JSON) with the following fields:
   repository URL, host, default branch, release tags to mirror, license status, refresh cadence, and attribution contacts.

## 2. Mirroring & snapshotting

1. **Bulk cloning**: Use distributed workers with git partial clone or sparse checkout to mirror repositories respecting API
   limits. Schedule jobs via orchestration (Airflow, Dagster, Prefect).
2. **Immutable storage**: Store bare mirrors in object storage with versioned folders `mirror/<host>/<owner>/<repo>/<commit>/`.
3. **Snapshot selection**: Choose release tags or commit ranges per repository. Record commit SHAs, snapshot timestamps, and
   manifest entries for reproducibility.
4. **Event hooks**: Subscribe to webhooks or release feeds for high-priority repositories to trigger incremental syncs.

## 3. Candidate extraction

1. **File selection**: Filter mirrored content using language detection, file extensions, and maximum file size thresholds.
2. **Sensitive content filtering**: Run scanners for credentials, secrets, personally identifiable information, and regulated
   data. Flag and quarantine hits for manual review.
3. **Security posture**: Detect and classify offensive security artifacts (exploits, malware). Route to security review for
   policy gating before inclusion.

## 4. Snippet generation

1. **Chunking**: Segment files into function-level or logical code blocks using tree-sitter, AST parsers, or heuristic
   delimiters. Capture surrounding context (imports, class definitions) where relevant.
2. **Documentation pairing**: Link code with inline comments, README excerpts, and official documentation to provide context for
   training tasks.
3. **Metadata capture**: Record language, repository path, line ranges, commit SHA, dependency manifests, and build/test status
   when available.
4. **Canonical hashing**: Generate SHA-256 hashes on normalised snippets (whitespace-trimmed, comment-normalised) to deduplicate
   across repositories and releases.

## 5. Ingestion orchestration

1. **Workflow engine**: Orchestrate the above steps via DAGs with idempotent tasks and checkpointing.
2. **Observability**: Emit metrics (throughput, errors, dedupe rates), structured logs, and lineage metadata to a central
   catalogue (e.g., OpenLineage, Marquez).
3. **Failure handling**: Implement retries with exponential backoff, dead-letter queues for problematic repositories, and
   automated issue creation for manual remediation.

## 6. Refresh cadence

- **Quarterly full refresh**: Rebuild the corpus from the latest allow-listed snapshots, tracking drift in license or repository
  status.
- **Monthly deltas**: Process incremental commits for high-signal repositories and publish delta shards with compatibility
  manifests.
- **Urgent patches**: Provide out-of-band updates for takedown requests, security incidents, or schema adjustments.

## 7. Documentation & audit

- Maintain diagrams of ingestion architecture, data lineage, and dependency graphs.
- Store audit evidence (API request logs, license approvals, takedown responses) for at least two years.
- Publish postmortems for major incidents and capture follow-up actions in the runbook backlog.
