# Data Quality & Validation

A rigorous validation program ensures MWRC releases maintain accuracy, completeness, and safety across domains.

## Quality pillars

1. **Completeness**
   - Track crawl coverage vs. target seeds with dashboards showing % of allow-listed pages retrieved.
   - Monitor repository clone success rates, branch coverage, and documentation extraction ratios.
   - Ensure vocabulary feeds include all required lemma classes and part-of-speech tags.

2. **Correctness**
   - Run deterministic schema validation on every JSONL shard.
   - Perform language detection audits using stratified sampling (Russian-only, English-only, bilingual) with manual verification.
   - Compare repository hashes against upstream commit SHAs to catch truncated downloads.

3. **Consistency**
   - Validate domain-level quality scores remain within expected ranges across releases (e.g., readability, toxicity, vulnerability classifier output).
   - Ensure dedupe ratios remain stable; spikes trigger drift investigations.
   - Confirm manifests accurately reflect shard byte sizes and record counts by re-computing checksums.

4. **Timeliness**
   - Validate that >90% of records originate within freshness SLAs (web ≤90 days old, repositories synced weekly, vocabularies monthly).
   - Track pipeline latency from crawl to release; deviations >10% raise alerts.

5. **Safety & compliance**
   - Run sensitive-content classifiers (malware, exploit kits, PII) on every batch with automatic quarantining.
   - Manual review quotas for high-risk domains ensure policy enforcement and human oversight.

## Validation workflow

1. **Automated checks**
   - Great Expectations suites enforce schema, enumerations, and range constraints.
   - Embedding-based similarity checks flag potential duplicates or off-domain content for manual adjudication.
   - Language drift monitors compare distribution of tokens between releases.

2. **Human-in-the-loop review**
   - Curated stratified samples across domains, languages, and quality scores are assigned to bilingual reviewers.
   - Review outcomes feed into calibration dashboards measuring precision/recall of automated filters.

3. **Sign-off gates**
   - Data engineering signs off on infrastructure health and dedup metrics.
   - Linguists approve bilingual accuracy and vocabulary coverage.
   - Compliance validates policy adherence, licensing, and takedown log completeness.

## Monitoring & alerting

- Metrics exported to Prometheus/Grafana track crawl success, dedupe ratios, classifier drift, and validation SLA compliance.
- PagerDuty or Opsgenie alerts trigger when critical metrics breach thresholds (e.g., dedupe ratio >10%, toxicity classifier recall <0.85).
- Monthly postmortems review incidents, annotate root causes, and update playbooks.

## Reporting

- Publish release scorecards summarizing quality metrics, outstanding risks, and change highlights.
- Maintain historical dashboards to compare releases and support anomaly detection.
- Provide consumer-facing quality notes detailing known limitations, blocked domains, or schema changes.
