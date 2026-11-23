"""
AI Ecosystem Intelligence Pipeline - Crawler Subsystem
======================================================
Module: src.crawler
Description: Production-ready asynchronous crawler and data acquisition engine.
Implements:
- High-throughput asynchronous crawling (asyncio + httpx)
- Anti-bot navigation and browser header rotation
- 24-hour rolling freshness ingestion for news feeds and career portals
- Research paper harvesting with GitHub repository and metric correlation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from core.engine import CrawlerEngine
from core.models import StartupProductRecord, SourceAssessment
from core.registry import SourceRegistry
from core.deduplicator import Deduplicator
from core.storage import StorageManager

logger = logging.getLogger("src.crawler")


class ProductionCrawler:
    """
    Unified crawler facade providing access to:
    1. Massive bulk entity harvesting (Startups & Products)
    2. Real-time 24-hour fresh signal ingestion (News & Jobs)
    3. Research paper correlation with GitHub telemetry
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.bulk_engine = CrawlerEngine(data_dir=data_dir)
        self.deduplicator = Deduplicator()
        self._daily_pipeline = None
        self._paper_pipeline = None

    @property
    def daily_pipeline(self):
        if self._daily_pipeline is None:
            from core.daily_pipeline import DailyCollectionPipeline
            self._daily_pipeline = DailyCollectionPipeline()
        return self._daily_pipeline

    @property
    def paper_pipeline(self):
        if self._paper_pipeline is None:
            from core.paper_github_pipeline import PaperGithubPipeline
            self._paper_pipeline = PaperGithubPipeline()
        return self._paper_pipeline

    async def run_bulk_harvest(self, source_id: Optional[str] = None, limit: int = 1000) -> Dict[str, Any]:
        """Executes concurrent bulk extraction for directory sources."""
        if source_id:
            logger.info(f"Running bulk harvest on source {source_id} (Limit: {limit})...")
            return await self.bulk_engine.ingest_source(source_id, limit=limit)
        else:
            logger.info("Assessing and harvesting all available directory sources...")
            assessments = await self.bulk_engine.test_all_sources()
            return {"status": "completed", "sources_assessed": len(assessments)}

    def run_daily_freshness_ingestion(self) -> Dict[str, Any]:
        """Ingests 24-hour fresh news and job vacancy signals."""
        logger.info("Executing 24-hour freshness cycle across 5 news feeds and 5 job boards...")
        return self.daily_pipeline.run_collection()

    def run_paper_github_correlation(self) -> Dict[str, Any]:
        """Harvests research papers and links associated GitHub repositories and stars."""
        logger.info("Executing research paper discovery and GitHub telemetry extraction...")
        return self.paper_pipeline.run()


__all__ = [
    "ProductionCrawler",
    "CrawlerEngine",
    "SourceRegistry",
    "Deduplicator",
    "StorageManager",
]
