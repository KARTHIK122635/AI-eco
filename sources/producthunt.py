import os
import asyncio
import re
import xml.etree.ElementTree as ET
from typing import AsyncGenerator, Dict, Any, List, Optional
import httpx
from bs4 import BeautifulSoup
from sources.base import BaseCollector
from core.models import StartupProductRecord, SourceAssessment


class ProductHuntCollector(BaseCollector):
    name = "producthunt"
    display_name = "Product Hunt"
    base_url = "https://www.producthunt.com/"
    default_rate_limit = 1.0
    max_concurrency = 2

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_token = self.config.get("api_token") or os.environ.get("PRODUCTHUNT_API_TOKEN")

    async def test_accessibility(self) -> SourceAssessment:
        async with httpx.AsyncClient(headers=self.headers, timeout=12.0) as client:
            # 1. robots.txt
            robots_status = "Unknown"
            try:
                r_rob = await client.get("https://www.producthunt.com/robots.txt")
                robots_status = f"HTTP {r_rob.status_code} (Disallows /search*, /auth/*, allows /sitemaps_v3/*)"
            except Exception as e:
                robots_status = f"Failed to fetch robots.txt: {e}"

            # 2. Test Feed vs Web Page
            r_feed = await client.get("https://www.producthunt.com/feed")
            feed_ok = (r_feed.status_code == 200)

            r_web = await client.get("https://www.producthunt.com/")
            cf_detected = (r_web.status_code == 403 or "challenge" in r_web.text.lower())

            collection_method = ""
            if self.api_token:
                collection_method = "Official Product Hunt GraphQL API v2 (Developer Token)"
            else:
                collection_method = "Permitted Public Atom/RSS Feed (https://www.producthunt.com/feed) with automated launch discovery"

            return SourceAssessment(
                source_name=self.display_name,
                directory_url=self.base_url,
                accessible=feed_ok or bool(self.api_token),
                status_code=r_feed.status_code,
                collection_method=collection_method,
                available_fields=[
                    "product_name", "company_name", "description (tagline & body)",
                    "original_source_url", "categories", "pricing_model (when stated in text)",
                    "votes_count (via API)", "published_at"
                ],
                missing_fields=["employee_count (Product Hunt does not track headcount)"],
                rate_limits_info="Public RSS feed: standard rate limit. GraphQL API: 500 requests per 15 minutes.",
                robots_txt_status=robots_status,
                bot_protection_detected=cf_detected,
                notes_and_alternatives=(
                    "The HTML root page uses Cloudflare Turnstile. The official Atom feed (/feed) is open and delivers 50 fresh launches per query. "
                    "For comprehensive historic bulk crawling, Product Hunt provides an official GraphQL API v2 with a free developer token."
                )
            )

    async def collect(self, limit: int = 50) -> AsyncGenerator[StartupProductRecord, None]:
        if self.api_token:
            async for rec in self._collect_graphql(limit):
                yield rec
        else:
            async for rec in self._collect_feed(limit):
                yield rec

    async def _collect_feed(self, limit: int) -> AsyncGenerator[StartupProductRecord, None]:
        url = "https://www.producthunt.com/feed"
        collected = 0

        async with httpx.AsyncClient(headers=self.headers, timeout=15.0) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return

            root = ET.fromstring(r.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)

            for entry in entries:
                if collected >= limit:
                    break

                title_el = entry.find("atom:title", ns)
                link_el = entry.find("atom:link", ns)
                content_el = entry.find("atom:content", ns)
                pub_el = entry.find("atom:published", ns)

                title = title_el.text.strip() if title_el is not None and title_el.text else "Unknown"
                source_url = link_el.attrib.get("href") if link_el is not None else self.base_url

                # Clean content HTML
                raw_content = content_el.text if content_el is not None and content_el.text else ""
                soup = BeautifulSoup(raw_content, "html.parser")
                clean_desc = soup.get_text(separator=" ").strip()

                # Infer pricing model if mentioned
                pricing = None
                desc_lower = clean_desc.lower()
                if "open-source" in desc_lower or "open source" in desc_lower:
                    pricing = "Open Source"
                elif "free trial" in desc_lower or "freemium" in desc_lower:
                    pricing = "Freemium"
                elif "100% free" in desc_lower or "completely free" in desc_lower:
                    pricing = "Free"
                elif "subscription" in desc_lower or "/month" in desc_lower or "$/mo" in desc_lower:
                    pricing = "Subscription"

                record = StartupProductRecord(
                    company_name=title,
                    product_name=title,
                    description=clean_desc,
                    employee_count=None,  # Not tracked on PH, do NOT invent
                    pricing_model=pricing,
                    company_website=None,
                    original_source_url=source_url,
                    source_directory=self.display_name,
                    categories=["Product Launch", "Tech"],
                    raw_metadata={"published_at": pub_el.text if pub_el is not None else None}
                )
                yield record
                collected += 1

    async def _collect_graphql(self, limit: int) -> AsyncGenerator[StartupProductRecord, None]:
        url = "https://api.producthunt.com/v2/api/graphql"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        query = """
        query GetPosts($first: Int) {
          posts(first: $first) {
            edges {
              node {
                name
                tagline
                description
                url
                votesCount
                pricingType
                website
                topics {
                  edges {
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        """
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, headers=headers, json={"query": query, "variables": {"first": limit}})
            if r.status_code == 200:
                posts = r.json().get("data", {}).get("posts", {}).get("edges", [])
                for edge in posts:
                    node = edge.get("node", {})
                    topics = [t.get("node", {}).get("name") for t in node.get("topics", {}).get("edges", [])]
                    record = StartupProductRecord(
                        company_name=node.get("name", "Unknown"),
                        product_name=node.get("name"),
                        description=f"{node.get('tagline', '')}. {node.get('description', '')}".strip(),
                        employee_count=None,
                        pricing_model=node.get("pricingType"),
                        company_website=node.get("website"),
                        original_source_url=node.get("url"),
                        source_directory=self.display_name,
                        categories=topics,
                        raw_metadata={"votes": node.get("votesCount")}
                    )
                    yield record
