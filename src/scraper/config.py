"""Configuration structures for scraper pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Optional


@dataclass(frozen=True)
class RateLimit:
    """Represents a basic token-bucket style rate limit."""

    requests: int
    per: timedelta

    def __post_init__(self) -> None:
        if self.requests <= 0:
            raise ValueError("requests must be positive")
        if self.per.total_seconds() <= 0:
            raise ValueError("per must be a positive duration")


@dataclass(frozen=True)
class WebsiteCrawlerConfig:
    """Configuration for generic website crawling."""

    allowed_domains: tuple[str, ...]
    blocked_paths: tuple[str, ...] = ()
    rate_limit: RateLimit = RateLimit(600, timedelta(minutes=1))
    max_concurrency: int = 32
    max_depth: int = 4
    user_agent: str = (
        "MWRC-Scraper/1.0 (+https://datasets.example.org/policies#crawler)"
    )
    obey_robots_txt: bool = True
    min_content_length: int = 256


@dataclass(frozen=True)
class GitCrawlerConfig:
    """Shared configuration for GitHub and GitLab crawling."""

    organisations: tuple[str, ...]
    languages: tuple[str, ...] = ("Python", "JavaScript", "Go", "Rust", "C#")
    rate_limit: RateLimit = RateLimit(30, timedelta(seconds=10))
    max_open_prs: int = 200
    include_wiki: bool = False
    include_security_advisories: bool = False
    default_branch_only: bool = True
    token_env_var: Optional[str] = None


@dataclass(frozen=True)
class VocabularySource:
    """Details for bilingual vocabulary sourcing."""

    provider: str
    language_pair: tuple[str, str] = ("ru", "en")
    url: Optional[str] = None
    license_name: str = "CC-BY-4.0"


@dataclass(frozen=True)
class ScraperTargets:
    """Mapping of source type to output directories."""

    raw_root: Path
    staging_root: Path
    release_root: Path

    def ensure_directories(self) -> None:
        for directory in (self.raw_root, self.staging_root, self.release_root):
            directory.mkdir(parents=True, exist_ok=True)


@dataclass
class PipelineConfig:
    """Aggregated configuration for the end-to-end pipeline."""

    website: WebsiteCrawlerConfig
    github: GitCrawlerConfig
    gitlab: GitCrawlerConfig
    vocabulary_sources: tuple[VocabularySource, ...]
    storage: ScraperTargets
    desired_languages: tuple[str, ...] = ("en", "ru")
    batch_size: int = 5000
    normalize_whitespace: bool = True
    redact_patterns: tuple[str, ...] = (r"(?i)api_key=[0-9a-z-_]+",)
    pii_detectors: tuple[str, ...] = (
        r"(?i)ssn\b[ -]?(\d{3})[ -]?(\d{2})[ -]?(\d{4})",
        r"\b\d{16}\b",  # potential card numbers
    )
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    metrics_sinks: tuple[str, ...] = ("prometheus", "datahub")
    checkpoint_interval: int = 10_000
    max_pending_tasks: int = 50_000
    metadata_enrichers: tuple[str, ...] = (
        "license_classifier",
        "language_detector",
        "domain_quality_scorer",
    )
    compress_output: bool = True
    compression_format: str = "zstd"
    dedupe_window_days: int = 90
    incremental_refresh: bool = True
    partition_strategy: str = "domain-date-shard"
    additional_settings: MutableMapping[str, str] = field(default_factory=dict)

    def export_env(self) -> Mapping[str, str]:
        """Convert selected settings into environment variables for workers."""

        env: dict[str, str] = {
            "MWRC_BATCH_SIZE": str(self.batch_size),
            "MWRC_EMBEDDING_MODEL": self.embedding_model,
            "MWRC_PARTITION_STRATEGY": self.partition_strategy,
            "MWRC_COMPRESS_OUTPUT": "1" if self.compress_output else "0",
        }
        if self.website.user_agent:
            env["MWRC_USER_AGENT"] = self.website.user_agent
        if self.github.token_env_var:
            env["MWRC_GITHUB_TOKEN_ENV"] = self.github.token_env_var
        if self.gitlab.token_env_var:
            env["MWRC_GITLAB_TOKEN_ENV"] = self.gitlab.token_env_var
        env.update(self.additional_settings)
        return env

    def iter_sources(self) -> Iterable[str]:
        """Iterate over configured source identifiers."""

        yield "website"
        yield "github"
        yield "gitlab"
        for vocab in self.vocabulary_sources:
            yield f"vocabulary:{vocab.provider}"
