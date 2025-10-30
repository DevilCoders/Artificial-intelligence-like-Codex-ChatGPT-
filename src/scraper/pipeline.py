"""End-to-end pipeline orchestrating scraping, cleaning, and exporting."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from collections import defaultdict
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

from .config import PipelineConfig, VocabularySource
from .crawlers import (
    GitHubCrawler,
    GitLabCrawler,
    VocabularyCrawler,
    WebsiteCrawler,
    normalise_results,
)
from .utils import NormalisedRecord, is_pii_free

logger = logging.getLogger(__name__)


class ScraperPipeline:
    """Coordinates crawling, cleaning, deduplication, and export."""

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        self.config.storage.ensure_directories()

    async def crawl_web(self) -> list[NormalisedRecord]:
        crawler = WebsiteCrawler(self.config.website)
        async with crawler:
            results = [result async for result in crawler.iter_records()]
        normalised = await normalise_results(results, self.config, domain="web")
        return self._post_process(normalised)

    async def crawl_github(self) -> list[NormalisedRecord]:
        crawler = GitHubCrawler(self.config.github)
        async with crawler:
            results = [result async for result in crawler.iter_records()]
        normalised = await normalise_results(results, self.config, domain="github")
        return self._post_process(normalised)

    async def crawl_gitlab(self) -> list[NormalisedRecord]:
        crawler = GitLabCrawler(self.config.gitlab)
        async with crawler:
            results = [result async for result in crawler.iter_records()]
        normalised = await normalise_results(results, self.config, domain="gitlab")
        return self._post_process(normalised)

    async def crawl_vocabularies(
        self, sources: Sequence[VocabularySource]
    ) -> list[NormalisedRecord]:
        collected: list[NormalisedRecord] = []
        for source in sources:
            crawler = VocabularyCrawler(source)
            async with crawler:
                results = [result async for result in crawler.iter_records()]
            normalised = await normalise_results(results, self.config, domain="vocabulary")
            collected.extend(self._post_process(normalised))
        return collected

    def _post_process(self, records: Iterable[NormalisedRecord]) -> list[NormalisedRecord]:
        processed: list[NormalisedRecord] = []
        for record in records:
            cleaned_text, redactions = self._apply_redactions(record.text)
            if not is_pii_free(cleaned_text, self.config.pii_detectors):
                continue
            safety = dict(record.safety)
            safety.setdefault("redactions", [])
            if redactions:
                safety["redactions"] = safety.get("redactions", []) + redactions
            updated = replace(
                record,
                text=cleaned_text,
                tokens=_count_tokens(cleaned_text),
                safety=safety,
            )
            processed.append(updated)
        return processed

    async def run(self) -> dict[str, list[NormalisedRecord]]:
        """Run the full scraping workflow concurrently."""

        tasks = {
            "web": asyncio.create_task(self.crawl_web()),
            "github": asyncio.create_task(self.crawl_github()),
            "gitlab": asyncio.create_task(self.crawl_gitlab()),
            "vocabulary": asyncio.create_task(
                self.crawl_vocabularies(self.config.vocabulary_sources)
            ),
        }
        results: dict[str, list[NormalisedRecord]] = {}
        for key, task in tasks.items():
            results[key] = await task
            logger.info("Collected records", extra={"source": key, "count": len(results[key])})
        return results

    def export_jsonl(self, records: dict[str, list[NormalisedRecord]]) -> list[Path]:
        """Export records into release-ready JSONL shards partitioned by domain."""

        output_paths: list[Path] = []
        current_date = datetime.utcnow().strftime("%Y%m%d")
        for domain, domain_records in records.items():
            if not domain_records:
                continue
            shard_dir = self.config.storage.release_root / domain
            shard_dir.mkdir(parents=True, exist_ok=True)
            shard_path = shard_dir / f"{domain}-{current_date}-000001.jsonl"
            with shard_path.open("w", encoding="utf-8") as fp:
                for record in domain_records:
                    fp.write(record.to_json())
                    fp.write("\n")
            output_paths.append(shard_path)
            logger.info(
                "Exported shard", extra={"domain": domain, "path": str(shard_path), "count": len(domain_records)}
            )
        return output_paths

    def build_manifest(self, shard_paths: Iterable[Path]) -> Path:
        manifest_dir = self.config.storage.release_root / "manifests"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / f"manifest-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
        entries = []
        for path in shard_paths:
            entries.append(
                {
                    "path": str(path.relative_to(self.config.storage.release_root)),
                    "bytes": path.stat().st_size,
                    "records": sum(1 for _ in path.open(encoding="utf-8")),
                }
            )
        manifest = {
            "generated_at": datetime.utcnow().isoformat(),
            "shards": entries,
            "config": self.config.export_env(),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest_path

    async def execute_and_export(self) -> Path:
        results = await self.run()
        shard_paths = self.export_jsonl(results)
        manifest_path = self.build_manifest(shard_paths)
        return manifest_path

    @staticmethod
    def group_by_language(records: Iterable[NormalisedRecord]) -> dict[str, list[NormalisedRecord]]:
        grouped: dict[str, list[NormalisedRecord]] = defaultdict(list)
        for record in records:
            grouped[record.language].append(record)
        return grouped

    def _apply_redactions(self, text: str) -> tuple[str, list[dict[str, str]]]:
        redactions: list[dict[str, str]] = []
        cleaned = text
        for pattern in self.config.redact_patterns:
            if re.search(pattern, cleaned):
                cleaned = re.sub(pattern, "<REDACTED>", cleaned)
                redactions.append({"pattern": pattern, "replacement": "<REDACTED>"})
        return cleaned, redactions


def _count_tokens(text: str) -> int:
    return max(1, len(text.split()))
