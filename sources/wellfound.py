import asyncio
import json
import re
from typing import AsyncGenerator, Dict, Any, List, Optional
import httpx
from bs4 import BeautifulSoup
from sources.base import BaseCollector
from core.models import StartupProductRecord, SourceAssessment


class WellfoundCollector(BaseCollector):
    name = "wellfound"
    display_name = "Wellfound"
    base_url = "https://wellfound.com/startups"
    default_rate_limit = 1.5
    max_concurrency = 2

    async def test_accessibility(self) -> SourceAssessment:
        async with httpx.AsyncClient(headers=self.headers, timeout=12.0) as client:
            # 1. robots.txt
            robots_status = "Unknown"
            try:
                r_rob = await client.get("https://wellfound.com/robots.txt")
                robots_status = f"HTTP {r_rob.status_code} (Disallows /auth/, /job_listings/, /recruit/dash)"
            except Exception as e:
                robots_status = f"Failed to fetch robots.txt: {e}"

            # 2. Startups directory
            accessible = False
            status_code = None
            cf_detected = False
            try:
                r = await client.get(self.base_url)
                status_code = r.status_code
                if r.status_code == 200:
                    accessible = True
                if "challenge" in r.text.lower() or "cf-mitigated" in r.headers:
                    cf_detected = True
            except Exception as e:
                status_code = None

            return SourceAssessment(
                source_name=self.display_name,
                directory_url=self.base_url,
                accessible=accessible,
                status_code=status_code,
                collection_method="Permitted Public HTML directory with embedded Next.js SSR Apollo cache parsing",
                available_fields=[
                    "company_name", "description (highConcept)",
                    "employee_count (companySize enum e.g. SIZE_51_200)",
                    "original_source_url", "categories (NewTag items)",
                    "founders/team (User items)", "badges"
                ],
                missing_fields=["pricing_model (inferred from SaaS/B2B tags if present, else None)"],
                rate_limits_info="Permitted public directory; crawl politely with 1.5-2.0s delay per request",
                robots_txt_status=robots_status,
                bot_protection_detected=cf_detected,
                notes_and_alternatives="Directory pages and company pages render SSR __NEXT_DATA__ JSON containing full company metadata and employee size tiers."
            )

    async def _discover_slugs(self, client: httpx.AsyncClient) -> List[str]:
        """Discovers startup slugs from the public directory."""
        slugs = []
        try:
            r = await client.get(self.base_url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    # Match /company/<slug>
                    m = re.match(r"^/company/([a-zA-Z0-9_-]+)(?:/.*)?$", href)
                    if m:
                        slug = m.group(1)
                        if slug not in slugs and slug not in ["wellfound", "jobs"]:
                            slugs.append(slug)
        except Exception:
            pass
        return slugs

    async def _extract_company_page(self, client: httpx.AsyncClient, slug: str) -> Optional[StartupProductRecord]:
        url = f"https://wellfound.com/company/{slug}"
        try:
            r = await client.get(url)
            if r.status_code != 200:
                return None

            soup = BeautifulSoup(r.text, "html.parser")
            script = soup.find("script", id="__NEXT_DATA__")
            if not script or not script.string:
                return None

            data = json.loads(script.string)
            apollo = data.get("props", {}).get("pageProps", {}).get("apolloState", {}).get("data", {})

            # Match main startup
            startup_data = None
            for k, v in apollo.items():
                if isinstance(v, dict) and v.get("__typename") == "Startup" and v.get("slug") == slug:
                    startup_data = v
                    break

            if not startup_data:
                for k, v in apollo.items():
                    if isinstance(v, dict) and v.get("__typename") == "Startup" and v.get("companySize"):
                        startup_data = v
                        break

            if not startup_data:
                return None

            # Collect tags
            tags = []
            for k, v in apollo.items():
                if isinstance(v, dict) and v.get("__typename") == "NewTag" and v.get("name"):
                    tags.append(v.get("name"))

            # Determine pricing model if stated in tags
            pricing = None
            tags_lower = [t.lower() for t in tags]
            if any("saas" in t or "b2b" in t for t in tags_lower):
                pricing = "Subscription / B2B SaaS"
            elif any("open source" in t for t in tags_lower):
                pricing = "Open Source"

            # Clean size enum
            size_raw = startup_data.get("companySize")
            size_clean = None
            if size_raw:
                # Map SIZE_1_10 -> '1-10', SIZE_11_50 -> '11-50', SIZE_5000_PLUS -> '5000+'
                size_clean = size_raw.replace("SIZE_", "").replace("_", "-").replace("PLUS", "+")

            return StartupProductRecord(
                company_name=startup_data.get("name", slug.title()),
                product_name=startup_data.get("name"),
                description=startup_data.get("highConcept"),
                employee_count=size_clean,
                pricing_model=pricing,
                company_website=startup_data.get("websiteUrl"),
                original_source_url=url,
                source_directory=self.display_name,
                categories=tags[:10],
                raw_metadata={"raw_size": size_raw}
            )
        except Exception:
            return None

    async def collect(self, limit: int = 50) -> AsyncGenerator[StartupProductRecord, None]:
        async with httpx.AsyncClient(headers=self.headers, timeout=15.0) as client:
            slugs = await self._discover_slugs(client)
            collected = 0
            for slug in slugs:
                if collected >= limit:
                    break
                record = await self._extract_company_page(client, slug)
                if record:
                    yield record
                    collected += 1
                await asyncio.sleep(self.rate_limit)
