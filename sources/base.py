from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional
import httpx
from core.models import StartupProductRecord, SourceAssessment


class BaseCollector(ABC):
    """
    Abstract Base Collector for all directory and API sources.
    Every source implements accessibility testing and asynchronous data ingestion.
    """
    name: str = "base"
    display_name: str = "Base Source"
    base_url: str = ""
    default_rate_limit: float = 1.0  # seconds between requests
    max_concurrency: int = 3

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rate_limit = self.config.get("rate_limit_delay", self.default_rate_limit)
        self.headers = self.config.get("headers", {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml,application/json;q=0.9,*/*;q=0.8"
        })

    @abstractmethod
    async def test_accessibility(self) -> SourceAssessment:
        """
        Tests whether the source is accessible, checks robots.txt,
        anti-bot protections, and reports available data fields.
        """
        pass

    @abstractmethod
    async def collect(self, limit: int = 50) -> AsyncGenerator[StartupProductRecord, None]:
        """
        Asynchronously discovers and yields startup and product records
        with automatic pagination and rate limit compliance.
        """
        pass
