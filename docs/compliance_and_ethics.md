# Compliance, Licensing, and Ethics

This document enumerates the governance requirements to distribute the Terminal Command Intelligence dataset responsibly.

## Licensing

- Maintain an approved license list curated with legal counsel.
- Track license at source and record level; propagate SPDX identifiers in metadata.
- For copyleft licenses (GPL, AGPL), document redistribution obligations and provide source mirrors when required.
- Include attribution manifests summarising all third-party sources and their licenses.

## Redistribution rights

- Confirm that each source permits dataset redistribution for research and commercial use.
- Honour takedown requests promptly and maintain audit logs of removals.
- When redistribution is prohibited, store data in segregated buckets with restricted ACLs and exclude from public release.

## Ethics and responsible use

- Classify high-risk commands (e.g., exploit proof-of-concepts) and provide cautionary notes.
- Embed disclaimers emphasising lawful, ethical security testing on authorised systems.
- Provide guidelines for red teaming data usage aligned with industry frameworks (MITRE ATT&CK, NIST SP 800-115).

## Privacy & PII

- Run automated PII detection pipelines (regex, ML models) and manually review suspicious hits.
- Redact or tokenise any residual PII before release.
- Maintain incident response procedures for accidental disclosure.

## Security controls

- Store pre-release data in access-controlled environments with audit logging.
- Encrypt data at rest and in transit (TLS, KMS-managed keys).
- Apply data loss prevention (DLP) policies on collaboration platforms.

## Legal review

- Conduct formal release reviews with legal, compliance, and security stakeholders.
- Document sign-off in release checklist and store approvals in version control.

## Consumer terms of use

- Publish acceptable use policy prohibiting malicious deployment.
- Require downstream users to agree to terms before download (click-through or API token agreement).
- Provide contact information for reporting misuse.

