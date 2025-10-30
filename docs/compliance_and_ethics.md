# Compliance, Licensing & Ethics

This handbook captures the governance requirements for releasing the Open Source Code Corpus (OSCC). The corpus aggregates
billions of code examples from public repositories; adherence to legal, ethical, and community standards is non-negotiable.

## 1. Licensing & attribution

1. **License inventory**: Maintain a living catalogue of SPDX identifiers permitted for inclusion. Default allow-list: `Apache-2.0`,
   `MIT`, `BSD-2-Clause`, `BSD-3-Clause`, `CC-BY-4.0`, `ISC`, `Unlicense`. Log exceptions with legal sign-off.
2. **Per-file resolution**: Parse license headers, `LICENSE` files, and `.reuse/dep5` metadata to determine the effective license
   per snippet. Record provenance in metadata.
3. **Attribution packages**: Ship machine-readable attribution manifests (JSON, SPDX SBOM) and human-readable NOTICE files with
   every release. Include repository URLs, authors, and license obligations.
4. **Distribution scope**: Document where the corpus will be hosted (internal, partner network, public) and confirm distribution
   rights for each license class.

## 2. Intellectual property & takedowns

1. **Ownership verification**: Exclude repositories with ambiguous ownership or DMCA history. Monitor takedown feeds and update
   allow-list accordingly.
2. **Takedown protocol**: Provide public contact channels and service-level objectives (e.g., acknowledge within 24h, resolve
   within 5 business days). Remove affected shards and publish delta manifests.
3. **Trademark & branding**: Strip logos, proprietary trademarks, and confidential branding materials from metadata and
   documentation.

## 3. Privacy & sensitive data

1. **PII & secrets scanning**: Run specialised detectors (trufflehog, detect-secrets, Presidio) during ingestion. Quarantine hits
   pending review and redact before release.
2. **Security-sensitive content**: Classify exploit code, malware, and red-team tooling. Apply policy-based gating (e.g., release
   to restricted audience, include warnings) and record rationale.
3. **User-generated data**: Avoid personal project repositories containing identifiable information unless explicit permission and
   licensing allow redistribution.

## 4. Ethical usage guidelines

1. **Purpose statement**: Clearly articulate intended uses (AI training, code intelligence research) and prohibited uses
   (malware generation, credential stuffing). Publish alongside dataset landing page.
2. **Safety controls**: Provide downstream consumers with filtering heuristics, metadata flags, and suggested guardrails for
   high-risk categories.
3. **Community stewardship**: Engage with upstream maintainers, honour attribution, and respond to concerns transparently.

## 5. Audit & compliance operations

1. **Documentation**: Store legal reviews, policy decisions, takedown records, and compliance attestations in a secured knowledge
   base.
2. **Access control**: Restrict release candidate access to authorised personnel; enforce MFA and least-privilege IAM policies.
3. **Retention & deletion**: Define retention periods for raw mirrors, intermediate artefacts, and final releases. Ensure secure
   deletion workflows are auditable.
4. **Regulatory awareness**: Monitor evolving regulations (EU AI Act, privacy laws, export controls) and update policies when
   scope changes.

## 6. Governance cadence

- Quarterly compliance review with legal, security, and data leadership.
- Annual external audit or third-party assessment for high-assurance releases.
- Continuous policy updates captured in change logs and communicated to stakeholders.
