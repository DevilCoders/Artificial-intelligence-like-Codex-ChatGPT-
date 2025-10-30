"""Utility helpers for scraping pipeline."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Iterable, Optional

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class NormalisedRecord:
    """Structured representation ready for serialization."""

    id: str
    domain: str
    url: str
    language: str
    text: str
    tokens: int
    license: str
    source_metadata: dict[str, Any]
    quality: dict[str, Any]
    safety: dict[str, Any]
    hash: str
    alignment: Optional[dict[str, Any]] = None
    embeddings: Optional[dict[str, Any]] = None

    def to_json(self) -> str:
        payload = {
            "id": self.id,
            "domain": self.domain,
            "url": self.url,
            "language": self.language,
            "text": self.text,
            "tokens": self.tokens,
            "license": self.license,
            "source_metadata": self.source_metadata,
            "quality": self.quality,
            "safety": self.safety,
            "hash": self.hash,
        }
        if self.alignment:
            payload["alignment"] = self.alignment
        if self.embeddings:
            payload["embeddings"] = self.embeddings
        return json.dumps(payload, ensure_ascii=False)


def compute_record_hash(text: str, url: str) -> str:
    """Compute a stable hash for deduplication using SHA256."""

    digest = hashlib.sha256()
    digest.update(url.encode("utf-8"))
    digest.update(b"\0")
    digest.update(text.encode("utf-8"))
    return digest.hexdigest()


def redact_patterns(text: str, patterns: Iterable[str]) -> str:
    """Redact sensitive patterns from text."""

    redacted = text
    for pattern in patterns:
        redacted = re.sub(pattern, "<REDACTED>", redacted)
    return redacted


def is_pii_free(text: str, detectors: Iterable[str]) -> bool:
    """Return True if none of the detectors match the text."""

    for detector in detectors:
        if re.search(detector, text):
            logger.debug("PII detector triggered", extra={"detector": detector})
            return False
    return True
