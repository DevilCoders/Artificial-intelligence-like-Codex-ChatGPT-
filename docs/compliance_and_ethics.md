# Compliance & Ethics

Responsible sourcing and distribution underpin every MWRC release. This document defines the governance measures required to maintain ethical, legal, and trustworthy datasets.

## Legal considerations

- **Licensing**: Catalog SPDX identifiers for every source. Git repositories inherit licenses from `LICENSE` files or repository metadata; websites require explicit terms-of-use review. Vocabulary datasets often follow Creative Commons variants—record attribution text verbatim.
- **Robots.txt adherence**: Respect disallow directives. For ambiguous cases, default to non-collection and escalate to legal counsel.
- **Takedown process**: Maintain a documented workflow with response SLAs (e.g., initial acknowledgement within 24 hours, resolution within 5 business days). Store all requests and actions in the compliance dossier.
- **Export controls**: Assess whether security-sensitive content (e.g., exploit kits) triggers jurisdictional restrictions. Implement geofencing for distribution if required.

## Privacy & safety

- **PII detection**: Apply regex and ML-based detectors. Records flagged as containing PII are removed or heavily redacted before release.
- **Security-sensitive materials**: Classify red/blue team content by sensitivity tier. Tier 3 (actively exploitable zero-day material) is blocked from public releases and held in restricted internal sets.
- **Abuse monitoring**: Instrument download portals with rate-limits, captcha, and abuse detection. Provide reporting channels for responsible disclosure.

## Ethical sourcing

- **Community engagement**: Notify maintainers of large-scale scraping activities where feasible, providing opt-out mechanisms.
- **Attribution**: Include source URLs, repository names, authors, and license notices in metadata and release documentation.
- **Bias mitigation**: Track representation of Russian vs. English content, gendered terms, and geographic focus. Trigger remediation if imbalances exceed policy thresholds.

## Governance workflow

1. **Policy alignment**: Annual review of legal, security, and ethical policies with stakeholders. Update playbooks accordingly.
2. **Control testing**: Quarterly audits of crawler compliance (robots adherence, token usage) and redaction efficacy.
3. **Incident response**: Maintain a severity matrix defining response actions for policy breaches. Conduct post-incident reviews and publish corrective actions.
4. **Documentation**: Store sign-offs, waivers, takedown logs, and bias assessments with each release tag. Ensure artifacts are immutable and access-controlled.

## Consumer guidance

- Provide acceptable-use policies highlighting restrictions (e.g., weaponization, disallowed jurisdictions).
- Offer contact channels for ethics questions or data-subject requests.
- Publish transparency reports summarizing takedown volume, bias remediation, and policy changes.
