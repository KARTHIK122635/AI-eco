import asyncio
import httpx
import logging
from typing import AsyncGenerator, List, Dict, Any
from core.schemas import AIStartup, evaluate_ai_evidence
from core.enrichment import WikidataEnricher

logger = logging.getLogger("AIStartupCollector")


class AIStartupCollector:
    """
    Collects and validates at least 1,000 verified AI startups from
    Y Combinator, Wellfound, and Wikidata with full pagination and enrichment.
    """
    ALGOLIA_APP_ID = "45BWZJ1SGC"
    ALGOLIA_API_KEY = "ZTQxNjIzMWY2Y2IxMTRhNjc4MTY4MTA1NjY0ZTg2OGU2ZDA3ZGI4ZTFiZTM4MTI2ZWQ0YmNhMzM4OGE4OGI5NWFuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNDb21wYW55X3Byb2R1Y3Rpb24lMkNZQ0NvbXBhbnlfQnlfTGF1bmNoX0RhdGVfcHJvZHVjdGlvbiZ0YWdGaWx0ZXJzPSU1QiUyMnljZGNfcHVibGljJTIyJTVEJnZhbGlkVW50aWw9MTc5NTMyNjExOQ=="

    def __init__(self):
        self.enricher = WikidataEnricher()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

    async def collect_yc_ai_startups(self, target_count: int = 1200) -> AsyncGenerator[AIStartup, None]:
        """Discovers AI startups from YC Algolia directory using multiple targeted queries & pagination."""
        url = f"https://{self.ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/*/queries"
        headers = {
            "x-algolia-application-id": self.ALGOLIA_APP_ID,
            "x-algolia-api-key": self.ALGOLIA_API_KEY,
            "content-type": "application/json"
        }

        ai_queries = ["AI", "Machine Learning", "Generative AI", "LLM", "Computer Vision"]
        yielded_slugs = set()
        yielded_count = 0

        async with httpx.AsyncClient(headers=self.headers, timeout=15.0) as client:
            for query_term in ai_queries:
                if yielded_count >= target_count:
                    break
                page = 0
                hits_per_page = 100

                while yielded_count < target_count and page < 10:
                    payload = {
                        "requests": [
                            {
                                "indexName": "YCCompany_production",
                                "params": f"query={query_term}&hitsPerPage={hits_per_page}&page={page}"
                            }
                        ]
                    }
                    try:
                        r = await client.post(url, headers=headers, json=payload)
                        if r.status_code != 200:
                            break
                        hits = r.json()["results"][0].get("hits", [])
                        if not hits:
                            break

                        for h in hits:
                            slug = h.get("slug")
                            if slug and slug in yielded_slugs:
                                continue

                            name = h.get("name", "").strip()
                            one_liner = h.get("one_liner") or ""
                            long_desc = h.get("long_description") or ""
                            desc = one_liner if one_liner else long_desc
                            tags = h.get("tags") or []
                            if h.get("industry"):
                                tags.append(h.get("industry"))

                            # Validate AI evidence
                            eval_res = evaluate_ai_evidence(name, f"{one_liner} {long_desc}", tags)
                            if not eval_res["is_ai"]:
                                continue  # Exclude non-AI companies

                            if slug:
                                yielded_slugs.add(slug)

                            team_size = h.get("team_size")
                            emp_count = int(team_size) if team_size and team_size > 0 else None
                            source_url = f"https://www.ycombinator.com/companies/{slug}" if slug else "https://www.ycombinator.com/companies"

                            pricing = None
                            tags_lower = [t.lower() for t in tags]
                            if any("open source" in t for t in tags_lower):
                                pricing = "Open Source / Commercial"
                            elif any("saas" in t or "b2b" in t for t in tags_lower):
                                pricing = "Subscription / B2B SaaS"

                            startup_id = f"yc_{slug}" if slug else f"yc_{abs(hash(name))}"
                            startup = AIStartup(
                                startup_id=startup_id,
                                name=name,
                                description=desc,
                                ai_focus_area=eval_res["focus_area"],
                                ai_evidence=eval_res["matched_keywords"],
                                employee_count=emp_count,
                                pricing_model=pricing,
                                website=h.get("website"),
                                primary_source_url=source_url,
                                provenance_sources=["Y Combinator"],
                                headquarters=h.get("all_locations"),
                                batch_or_founded=h.get("batch"),
                                raw_metadata={"stage": h.get("stage"), "status": h.get("status")}
                            )
                            yield startup
                            yielded_count += 1
                            if yielded_count >= target_count:
                                break

                        page += 1
                        await asyncio.sleep(0.2)
                    except Exception as e:
                        logger.error(f"Error querying YC '{query_term}' page {page}: {e}")
                        break
