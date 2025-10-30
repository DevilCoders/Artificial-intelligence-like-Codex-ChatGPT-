# Data Collection Pipeline

This guide details the end-to-end ingestion process for the Multilingual Web & Repository Corpus (MWRC). The pipeline is designed to crawl billions of records from websites, GitHub, GitLab, and bilingual vocabulary sources while enforcing governance controls and maintaining reproducibility.

## Architecture overview

1. **Source registry**: Central YAML registry enumerating approved domains, repositories, API endpoints, authentication scopes, and licensing status. Updated via pull requests with automated linting for ownership, contact email, and compliance tags.
2. **Distributed scheduler**: Kubernetes or Airflow orchestrates scrape jobs using the configuration exported by `src.scraper.config.PipelineConfig`. Jobs are sharded by domain and geographic region to respect data residency.
3. **Async crawlers**: Custom asyncio-based workers (`WebsiteCrawler`, `GitHubCrawler`, `GitLabCrawler`, `VocabularyCrawler`) execute HTTP requests with adaptive rate limits, rotating proxies, and per-source retry policies.
4. **Raw storage**: Unprocessed responses (HTML, Markdown, repository archives, vocabulary tables) are persisted in object storage using deterministic keys (`raw/<source>/<YYYY>/<MM>/<DD>/<uuid>.json`).
5. **Metadata broker**: Kafka topics capture crawl telemetry (request counts, HTTP status, bytes transferred, robots decisions) to power dashboards and anomaly detection.
6. **Checkpointing**: Every worker emits checkpoint files after configurable intervals (`PipelineConfig.checkpoint_interval`) to enable resumable crawls in case of failure.

## Key capabilities

- **Robots.txt and sitemap awareness**: Workers fetch robots.txt before scraping and ingest sitemaps when available. Non-compliant paths are skipped and logged to the compliance report.
- **Credential isolation**: GitHub/GitLab tokens are injected via `token_env_var` and rotated automatically using secret managers. Vocabulary sources requiring API keys are scoped to read-only privileges.
- **Adaptive throttling**: Rate limits are enforced using token-bucket semantics defined in `RateLimit`. Workers monitor latency and failure rates to back off proactively when encountering stress indicators.
- **Content negotiation**: Web crawlers negotiate HTML/JSON/Markdown based on domain preferences, while repo crawlers clone default branches and optionally fetch PR diffs for knowledge of active development.
- **Language prioritisation**: Seeds emphasise Russian and English entry points; heuristics expand to linked pages when language classifiers predict high confidence for target locales.
- **Attribution logging**: Every request stores headers, source license, and upstream attribution statements to satisfy open-source requirements during release.

## Scaling strategy

- Launch hundreds of concurrent pods across multiple regions, pinning web crawlers close to target domains to minimise latency and respect geopolitical constraints.
- Use queue-based load balancing to assign new crawl tasks only after previous shards emit checkpoints, preventing overload of smaller domains.
- Mirror high-volume repositories using git alternates and partial clones to reduce redundant bandwidth.

## Failure handling

- Automatic retries with exponential backoff for transient failures, capped at 5 attempts.
- Circuit breakers triggered by HTTP 429/5xx bursts pause scraping for that domain and alert operators.
- Persistent failures or legal blocks (HTTP 451) are escalated to compliance with full request/response logging.

## Reproducibility

- Pipeline configurations and source registries are versioned and tagged alongside each release.
- Crawl jobs emit deterministic JSON summaries describing commit hashes, dependency versions, and environment variables derived from `PipelineConfig.export_env()`.
- Raw artifacts are immutable; reprocessing uses snapshot pointers to guarantee repeatable normalization and training data builds.
