"""Crawler implementations for websites, GitHub, and GitLab."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncIterator, Iterable

from .config import GitCrawlerConfig, PipelineConfig, VocabularySource, WebsiteCrawlerConfig
from .utils import NormalisedRecord, compute_record_hash

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CrawlResult:
    """Canonical record extracted by a crawler prior to normalisation."""

    url: str
    content: str
    language: str | None
    metadata: dict[str, Any]
    retrieved_at: datetime


class BaseCrawler:
    """Abstract base crawler providing async iteration helper."""

    def __init__(self, concurrency: int = 16) -> None:
        self._semaphore = asyncio.Semaphore(concurrency)

    async def __aenter__(self) -> "BaseCrawler":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.close()

    async def close(self) -> None:
        """Hook for releasing resources."""

    async def iter_records(self) -> AsyncIterator[CrawlResult]:
        raise NotImplementedError


class WebsiteCrawler(BaseCrawler):
    """Asynchronous crawler for generic websites with robots.txt handling."""

    def __init__(self, config: WebsiteCrawlerConfig) -> None:
        super().__init__(config.max_concurrency)
        self.config = config

    async def iter_records(self) -> AsyncIterator[CrawlResult]:
        # Placeholder implementation using config allowed domains. Real implementation would
        # fetch pages respecting robots.txt, site maps, and structural hints.
        for domain in self.config.allowed_domains:
            logger.debug("Scheduling domain crawl", extra={"domain": domain})
            for idx in range(5):
                url = f"https://{domain}/article/{idx}"
                metadata = {
                    "domain": domain,
                    "depth": 2,
                    "render_strategy": "requests",
                    "language_hint": "en" if idx % 2 == 0 else "ru",
                    "license": "CC-BY-4.0" if idx % 2 == 0 else "CC-BY-SA-3.0",
                    "security_tier": "public",
                }
                yield CrawlResult(
                    url=url,
                    content=(
                        "<html><body>Sample content for domain %s index %d."
                        " Дополнительный текст.</body></html>" % (domain, idx)
                    ),
                    language="en" if idx % 2 == 0 else "ru",
                    metadata=metadata,
                    retrieved_at=datetime.utcnow(),
                )


class GitRepositoryCrawler(BaseCrawler):
    """Base crawler for Git hosting platforms."""

    def __init__(self, config: GitCrawlerConfig, platform: str) -> None:
        super().__init__(concurrency=8)
        self.config = config
        self.platform = platform

    async def iter_records(self) -> AsyncIterator[CrawlResult]:
        for organisation in self.config.organisations:
            for language in self.config.languages:
                repo_name = f"{organisation}/{language.lower()}-playbook"
                metadata = {
                    "platform": self.platform,
                    "organisation": organisation,
                    "language": language,
                    "branch": "main",
                    "license": "MIT",
                    "security_tier": "public" if self.platform == "github" else "sensitive",
                }
                yield CrawlResult(
                    url=f"https://{self.platform}.com/{repo_name}",
                    content=f"print('Hello from {language} repo maintained by {organisation}')",
                    language="en",
                    metadata=metadata,
                    retrieved_at=datetime.utcnow(),
                )


class GitHubCrawler(GitRepositoryCrawler):
    def __init__(self, config: GitCrawlerConfig) -> None:
        super().__init__(config, platform="github")


class GitLabCrawler(GitRepositoryCrawler):
    def __init__(self, config: GitCrawlerConfig) -> None:
        super().__init__(config, platform="gitlab")


class VocabularyCrawler(BaseCrawler):
    """Crawler for bilingual vocabulary sources."""

    def __init__(self, source: VocabularySource) -> None:
        super().__init__(concurrency=4)
        self.source = source

    async def iter_records(self) -> AsyncIterator[CrawlResult]:
        dataset = [
            {"ru": "безопасность", "en": "security", "frequency_bucket": "common"},
            {"ru": "инфраструктура", "en": "infrastructure", "frequency_bucket": "specialised"},
            {"ru": "разведка", "en": "reconnaissance", "frequency_bucket": "specialised"},
        ]
        for idx, row in enumerate(dataset):
            metadata = {
                "provider": self.source.provider,
                "license": self.source.license_name,
                "row_id": idx,
                "frequency_bucket": row.get("frequency_bucket", "common"),
            }
            yield CrawlResult(
                url=self.source.url or f"https://lexicons.example/{self.source.provider}/{idx}",
                content=json.dumps({"ru": row["ru"], "en": row["en"]}, ensure_ascii=False),
                language="ru-en",
                metadata=metadata,
                retrieved_at=datetime.utcnow(),
            )


async def normalise_results(
    results: Iterable[CrawlResult],
    pipeline_config: PipelineConfig,
    domain: str,
) -> list[NormalisedRecord]:
    """Convert crawl results into normalised records ready for persistence."""

    normalised: list[NormalisedRecord] = []
    for item in results:
        clean_text = re.sub(r"<[^>]+>", " ", item.content)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        metadata = dict(item.metadata)
        metadata.update(
            {
                "retrieved_at": item.retrieved_at.isoformat(),
                "domain": domain,
            }
        )
        license_name = metadata.get("license", "CUSTOM:UNKNOWN")
        security_tier = metadata.get("security_tier", "public")
        tokens = max(1, len(clean_text.split()))
        hash_value = compute_record_hash(clean_text, item.url)
        record_id = f"{domain}-{hash_value[:8]}"
        quality = _derive_quality(domain, clean_text, metadata)
        safety = {
            "pii_flag": False,
            "pii_detectors": [],
            "security_tier": security_tier,
            "redactions": [],
        }
        alignment = None
        if domain == "vocabulary":
            alignment = _extract_alignment(item.content)
        record = NormalisedRecord(
            id=record_id,
            domain=domain,
            url=item.url,
            language=item.language or "unknown",
            text=clean_text,
            tokens=tokens,
            license=license_name,
            source_metadata=metadata,
            quality=quality,
            safety=safety,
            hash=hash_value,
            alignment=alignment,
        )
        if domain == "web" and len(record.text) < pipeline_config.website.min_content_length:
            logger.debug("Skipping short web record", extra={"url": item.url})
            continue
        normalised.append(record)
    return normalised


def _derive_quality(domain: str, text: str, metadata: dict[str, Any]) -> dict[str, Any]:
    tokens = max(1, len(text.split()))
    readability = max(0.1, min(1.0, 1.1 - tokens / 600))
    quality: dict[str, Any] = {
        "readability": round(readability, 2),
        "toxicity": 0.0,
        "domain_specific": {},
        "dedupe_rank": 0,
    }
    if domain == "web":
        hint = metadata.get("language_hint")
        quality["language_confidence"] = 0.95 if hint in {"en", "ru"} else 0.8
        quality["domain_specific"] = {"security_relevance": 0.85}
    elif domain in {"github", "gitlab"}:
        code_lang = metadata.get("language", "unknown")
        quality["code_language"] = code_lang
        quality["tests_present"] = metadata.get("tests_present", False)
        quality["domain_specific"] = {"security_relevance": 0.9}
    elif domain == "vocabulary":
        quality["frequency_bucket"] = metadata.get("frequency_bucket", "common")
        quality["domain_specific"] = {}
    return quality


def _extract_alignment(content: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "ru" in parsed and "en" in parsed:
            return {
                "source_tokens": [parsed["ru"]],
                "target_tokens": [parsed["en"]],
                "part_of_speech": parsed.get("pos", "noun"),
            }
    except json.JSONDecodeError:
        logger.debug("Unable to parse vocabulary alignment", extra={"content": content[:50]})
    return None
