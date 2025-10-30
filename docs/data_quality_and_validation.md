# Data Quality & Validation Strategy

This guide defines the validation framework used to ensure the Open Source Code Corpus (OSCC) meets enterprise-grade standards
before release. The strategy combines automated checks, sampling, and governance workflows to manage billions of records.

## 1. Quality principles

- **Accuracy**: Snippets reflect actual source content at a specific commit and include faithful metadata.
- **Completeness**: Required schema fields are populated; optional enrichments have target coverage thresholds.
- **Consistency**: Formatting, encoding, and taxonomy assignments are uniform across shards and releases.
- **Safety**: Harmful or sensitive content is filtered or flagged with appropriate risk labels.
- **Traceability**: Every record links back to source commits, processing jobs, and validation artefacts.

## 2. Automated validation pipeline

1. **Schema conformance**: Validate each record with strict schema contracts (e.g., Great Expectations, `pandera`, custom Rust
   validators). Reject or quarantine non-compliant rows.
2. **License verification**: Confirm SPDX identifiers against allow-lists, cross-check with repository license files, and flag
   conflicts for manual review.
3. **Deduplication metrics**: Calculate intra- and inter-release duplicate ratios using canonical hashes and MinHash-based
   similarity search. Set alert thresholds (<1% duplicates per release).
4. **Static analysis scores**: Ingest linter and security scanner outputs; enforce minimum quality thresholds by language and
   framework.
5. **Execution validation**: Where feasible, run tests or notebooks associated with snippets; capture exit codes, runtime, and
   logs. Require >90% pass rate for curated gold subsets.
6. **Content safety**: Apply classifiers for PII, secrets, malware, extremism, and hate speech. Block or redact flagged content
   and log remediation.

## 3. Sampling & human review

1. **Stratified sampling**: Sample by language, license, repository host, and quality score decile. Adjust sample rates based on
   risk appetite and historical incident patterns.
2. **Expert review**: Assign samples to domain experts (language specialists, security analysts). Provide review forms capturing
   accuracy, safety, documentation quality, and suggested actions.
3. **Escalation workflow**: Route disputed records to governance board meetings for final decision, documenting outcomes in the
   release dossier.

## 4. Metrics & dashboards

- **Coverage metrics**: Language coverage, license mix, attribution completeness, enrichment coverage.
- **Quality indices**: Mean quality score, static analysis pass rate, test pass rate, documentation density.
- **Operational metrics**: Processing throughput, validation runtime, error counts, backlog age.
- **Safety metrics**: Sensitive-content hit rate, false-positive rate, remediation turnaround time.

Publish dashboards in analytics tooling (e.g., Looker, Metabase, Superset) and include snapshots in release notes.

## 5. Release gating

1. **Go/no-go checklist**: Ensure critical metrics exceed thresholds defined in release playbooks (see `release_checklist.md`).
2. **Sign-offs**: Require approvals from data engineering, ML engineering, legal/compliance, and security leads.
3. **Issue tracking**: Capture all release-blocking issues in the tracker; document waivers with expiration dates and owners.
4. **Post-release monitoring**: Instrument telemetry to detect downstream issues (API error rates, consumer feedback) and trigger
   remediation workflows.

## 6. Continuous improvement

- Conduct quarterly retrospectives on validation incidents and update heuristics accordingly.
- Maintain a backlog of validation rules to automate based on human-review findings.
- Share learnings with upstream open-source communities and incorporate feedback into sourcing policies.
