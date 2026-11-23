import os
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
import httpx
from sources.base import BaseCollector
from core.models import StartupProductRecord, SourceAssessment


class CrunchbaseCollector(BaseCollector):
    name = "crunchbase"
    display_name = "Crunchbase"
    base_url = "https://www.crunchbase.com/"
    default_rate_limit = 2.0
    max_concurrency = 1

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key") or os.environ.get("CRUNCHBASE_API_KEY")

    async def test_accessibility(self) -> SourceAssessment:
        async with httpx.AsyncClient(headers=self.headers, timeout=12.0) as client:
            robots_status = "Unknown"
            try:
                r_rob = await client.get("https://www.crunchbase.com/robots.txt")
                robots_status = f"HTTP {r_rob.status_code} (Disallows /search, /discover, /v4, /admin)"
            except Exception as e:
                robots_status = f"Failed to fetch robots.txt: {e}"

            # Test web directory access
            cf_detected = False
            status_code = None
            try:
                r = await client.get("https://www.crunchbase.com/organization/openai")
                status_code = r.status_code
                if r.status_code == 403 or "challenge" in r.text.lower() or "cf-mitigated" in r.headers:
                    cf_detected = True
            except Exception as e:
                cf_detected = True

            accessible = False
            collection_method = ""
            if self.api_key:
                collection_method = "Official Crunchbase Basic/Enterprise REST API (v4)"
                accessible = True
            else:
                collection_method = "BLOCKED: Web scraper restricted by Cloudflare Turnstile challenge and ToS"

            return SourceAssessment(
                source_name=self.display_name,
                directory_url=self.base_url,
                accessible=accessible,
                status_code=status_code,
                collection_method=collection_method,
                available_fields=[
                    "company_name (via API)", "description (via API)",
                    "employee_count (num_employees_enum via API)",
                    "company_website (via API)", "original_source_url (via API)",
                    "funding_total (via API)", "categories (via API)"
                ] if self.api_key else [],
                missing_fields=["pricing_model"] if self.api_key else ["All fields blocked without API key"],
                rate_limits_info="Commercial API tier (e.g. 200 requests/minute with valid key). Web UI enforces immediate Cloudflare 403 challenge.",
                robots_txt_status=robots_status,
                bot_protection_detected=cf_detected,
                notes_and_alternatives=(
                    "Crunchbase prohibits automated scraping in robots.txt and deploys Cloudflare Turnstile bot challenges. "
                    "Automated crawling without bypassing security requires an official Crunchbase API key (CRUNCHBASE_API_KEY). "
                    "Alternative legitimate open sources recommended: Wikidata SPARQL/Entity API (CC0 public domain data including "
                    "employee counts, founding dates, and websites), Y Combinator directory, and Hugging Face Hub."
                )
            )

    async def collect(self, limit: int = 50) -> AsyncGenerator[StartupProductRecord, None]:
        if not self.api_key:
            # Yield nothing or raise informative log - no bypass allowed
            return

        url = "https://api.crunchbase.com/api/v4/searches/organizations"
        headers = {
            "X-cb-user-key": self.api_key,
            "Content-Type": "application/json"
        }
        query_payload = {
            "field_ids": [
                "name", "short_description", "num_employees_enum",
                "website_url", "permalink", "categories"
            ],
            "limit": min(limit, 50)
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, headers=headers, json=query_payload)
            if r.status_code == 200:
                entities = r.json().get("entities", [])
                for ent in entities:
                    props = ent.get("properties", {})
                    permalink = props.get("permalink", "")
                    record = StartupProductRecord(
                        company_name=props.get("name", "Unknown"),
                        product_name=props.get("name"),
                        description=props.get("short_description"),
                        employee_count=props.get("num_employees_enum"),
                        company_website=props.get("website_url"),
                        original_source_url=f"https://www.crunchbase.com/organization/{permalink}",
                        source_directory=self.display_name,
                        categories=[c.get("value") for c in props.get("categories", []) if isinstance(c, dict)]
                    )
                    yield record
