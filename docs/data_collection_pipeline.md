# Data Collection Pipeline

This guide documents the acquisition pipeline required to assemble a multi-billion record terminal command dataset from publicly available, ethically sourced materials.

## Source registry

Maintain a machine-readable registry (e.g., `sources.yaml`) describing every upstream location:

- **Repositories**: GitHub, GitLab, Bitbucket, and self-hosted mirrors.
- **Documentation portals**: Vendor docs, community wikis, security blogs, and cheat sheets.
- **Academic and training resources**: University courseware, CTF write-ups, and CERT advisories.

Each entry must include:

- Canonical URL and clone URL.
- License and redistribution terms.
- Content type (code, markdown, wiki, blog, dataset, etc.).
- Update cadence and last synced timestamp.
- Contact or issue tracker for takedown requests.

## Harvesting strategy

1. **Mirroring**: Use `git clone --mirror` for repositories, `wget --mirror`/`httrack` for static sites, and REST APIs for dynamic portals.
2. **Incremental updates**: Schedule daily or weekly sync jobs via Airflow or Prefect with checkpoints to minimise bandwidth.
3. **Change detection**: Compare commit hashes or HTTP `ETag` values to detect new content.
4. **Rate limiting**: Respect robots.txt, API rate limits, and courtesy delays.
5. **Audit logging**: Record job metadata (start time, duration, bytes transferred) for accountability.

## Content filtering

During ingestion, apply filters to reject unwanted material:

- Proprietary or incompatible license strings.
- Personally identifiable information (PII) using regex detectors and ML classifiers.
- Non-terminal assets (binary blobs, media files) unless explicitly required.
- Content flagged by security SMEs as harmful, unethical, or out of scope.

## Metadata capture

For every command candidate, capture:

- File path and repository commit.
- Surrounding textual context (±10 lines) for semantic understanding.
- Programming language or shell flavour inference.
- Execution environment hints (OS, architecture, dependencies).
- Security sensitivity level (green/yellow/red) with justification.

## Storage layout

Organise raw artefacts using a deterministic folder hierarchy:

```
raw/
  github/
    org__repo/
      commits/
      issues/
  docs/
    vendor__product/
      html/
      pdf/
```

Use object storage with versioned buckets and lifecycle policies to manage cost.

## Tooling recommendations

- **Downloader**: `aria2c`, `rclone`, or vendor-specific CLIs.
- **Queue management**: Kafka topics for newly discovered sources.
- **Infrastructure**: Kubernetes CronJobs or managed workflows (AWS Step Functions, GCP Cloud Composer).
- **Observability**: Prometheus metrics and Grafana dashboards for throughput, error rates, and backlog depth.

