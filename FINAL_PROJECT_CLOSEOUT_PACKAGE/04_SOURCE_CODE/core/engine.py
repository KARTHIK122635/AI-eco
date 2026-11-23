import asyncio
import logging
from typing import List, Dict, Optional, Any
from core.registry import SourceRegistry
from core.models import StartupProductRecord, SourceAssessment
from core.deduplicator import Deduplicator
from core.storage import StorageManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CrawlerEngine")


class CrawlerEngine:
    """
    Central Asynchronous Crawling & Data Ingestion Engine.
    Handles source orchestration, deduplication, rate limiting, and persistence.
    """
    def __init__(self, registry: Optional[SourceRegistry] = None, data_dir: str = "data"):
        self.registry = registry or SourceRegistry()
        self.deduplicator = Deduplicator()
        self.storage = StorageManager(data_dir=data_dir)

    async def test_all_sources(self) -> List[SourceAssessment]:
        """Tests accessibility and data fields for all registered sources."""
        sources = self.registry.list_available_sources()
        assessments = []
        for s in sources:
            src_id = s["id"]
            collector = self.registry.get_collector(src_id)
            if not collector:
                continue
            logger.info(f"Testing accessibility for {collector.display_name} ({src_id})...")
            try:
                assessment = await collector.test_accessibility()
                assessments.append(assessment)
            except Exception as e:
                logger.error(f"Error testing {src_id}: {e}")
                assessments.append(SourceAssessment(
                    source_name=collector.display_name,
                    directory_url=collector.base_url,
                    accessible=False,
                    status_code=None,
                    collection_method="Error encountered",
                    available_fields=[],
                    missing_fields=[],
                    rate_limits_info="Unknown",
                    robots_txt_status="Error",
                    bot_protection_detected=False,
                    notes_and_alternatives=f"Test failed with exception: {e}"
                ))
        return assessments

    async def ingest_source(self, source_id: str, limit: int = 50) -> Dict[str, int]:
        """Runs ingestion for a single source with deduplication and persistence."""
        collector = self.registry.get_collector(source_id)
        if not collector:
            logger.warning(f"Source {source_id} not found in registry.")
            return {"discovered": 0, "added": 0, "duplicates": 0}

        logger.info(f"Starting ingestion from {collector.display_name} (Limit: {limit})...")
        discovered_count = 0
        added_count = 0
        duplicate_count = 0

        try:
            async for record in collector.collect(limit=limit):
                discovered_count += 1
                if self.deduplicator.add(record):
                    self.storage.append_record(record)
                    added_count += 1
                else:
                    duplicate_count += 1
        except Exception as e:
            logger.error(f"Error during collection from {source_id}: {e}", exc_info=True)

        logger.info(f"Finished {collector.display_name}: Discovered {discovered_count}, Added {added_count}, Duplicates {duplicate_count}")
        return {
            "discovered": discovered_count,
            "added": added_count,
            "duplicates": duplicate_count
        }

    async def ingest_all(self, limit_per_source: int = 30) -> Dict[str, Any]:
        """Runs ingestion across all enabled sources in parallel/staggered tasks."""
        sources = self.registry.list_available_sources()
        summary = {}
        for s in sources:
            src_id = s["id"]
            if not s.get("enabled", True):
                logger.info(f"Skipping disabled source: {src_id}")
                continue
            res = await self.ingest_source(src_id, limit=limit_per_source)
            summary[src_id] = res

        # Export full dataset to CSV
        all_records = self.deduplicator.get_all()
        self.storage.export_csv(all_records)
        return {
            "source_summaries": summary,
            "total_unique_records": len(all_records),
            "csv_path": self.storage.csv_path,
            "jsonl_path": self.storage.jsonl_path,
            "sqlite_path": self.storage.db_path
        }
