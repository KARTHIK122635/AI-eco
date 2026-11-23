import asyncio
import httpx
import feedparser
import re
import warnings
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Set, Optional
from urllib.parse import urlparse, urlunparse

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

from core.schemas import evaluate_ai_evidence
from core.news_schemas import extract_related_companies, classify_news_category, generate_news_id


def canonicalize_url(url: str) -> str:
    """Strips tracking query params (utm_*, ref, etc.) and fragments."""
    if not url:
        return ""
    try:
        p = urlparse(url)
        clean_queries = []
        if p.query:
            for q in p.query.split("&"):
                k = q.split("=")[0].lower()
                if not any(k.startswith(prefix) for prefix in ["utm_", "ref", "fbclid", "gclid", "source"]):
                    clean_queries.append(q)
        clean_query = "&".join(clean_queries)
        return urlunparse((p.scheme, p.netloc, p.path.rstrip('/'), p.params, clean_query, ""))
    except Exception:
        return url.strip()


def normalize_iso_date(raw_date: Optional[str]) -> str:
    """Parses various date formats (RFC 2822, ISO, timestamp) into ISO 8601 UTC."""
    if not raw_date:
        return datetime.now(timezone.utc).isoformat()
    try:
        if "T" in str(raw_date):
            dt = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
            return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        pass

    try:
        dt = parsedate_to_datetime(str(raw_date))
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        pass

    try:
        if str(raw_date).isdigit():
            dt = datetime.fromtimestamp(int(raw_date), tz=timezone.utc)
            return dt.isoformat()
    except Exception:
        pass

    return datetime.now(timezone.utc).isoformat()


def clean_html(text: Optional[str]) -> str:
    """Strips HTML tags and extra whitespace."""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    clean = soup.get_text(separator=" ")
    return re.sub(r'\s+', ' ', clean).strip()


class AINewsCollector:
    """
    Asynchronous collector for AI news from verified RSS feeds,
    official enterprise AI research blogs, and public technology journalism APIs.
    """
    RSS_FEEDS = [
        ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
        ("Google DeepMind Blog", "https://deepmind.google/blog/rss.xml"),
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("Ars Technica AI", "https://arstechnica.com/tag/ai/feed/"),
        ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss"),
        ("MIT Technology Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed/"),
        ("MarkTechPost", "https://www.marktechpost.com/feed/"),
        ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
        ("ZDNet AI", "https://www.zdnet.com/topic/artificial-intelligence/rss.xml"),
        ("InfoQ AI", "https://feed.infoq.com/ai-ml-data-eng/news")
    ]

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        self.seen_urls: Set[str] = set()
        self.seen_titles: Set[str] = set()

    async def collect_from_feed(self, source_name: str, feed_url: str, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Parses an RSS/Atom feed and returns valid AI news records."""
        records = []
        try:
            resp = await client.get(feed_url, timeout=15.0)
            if resp.status_code != 200:
                return records

            feed = feedparser.parse(resp.text)
            for entry in feed.entries:
                raw_url = entry.get("link") or entry.get("id") or ""
                canon_url = canonicalize_url(raw_url)
                title = clean_html(entry.get("title", ""))

                if not canon_url or not title:
                    continue

                title_key = title.lower()
                if canon_url in self.seen_urls or title_key in self.seen_titles:
                    continue

                raw_summary = entry.get("summary") or entry.get("description") or ""
                summary = clean_html(raw_summary)
                if not summary:
                    summary = f"Official research announcement from {source_name}: {title}"
                if len(summary) > 500:
                    summary = summary[:497] + "..."

                content = summary
                if "content" in entry and entry.content:
                    parsed_content = clean_html(entry.content[0].value)
                    if parsed_content:
                        content = parsed_content
                if not content:
                    content = summary

                author = entry.get("author") or entry.get("creator") or source_name
                pub_date = entry.get("published") or entry.get("updated")
                iso_date = normalize_iso_date(pub_date)

                if "Hugging Face" in source_name or "DeepMind" in source_name or "AI" in source_name or "MarkTechPost" in source_name:
                    is_ai = True
                else:
                    ev = evaluate_ai_evidence(title, summary, [])
                    is_ai = ev["is_ai"]

                if not is_ai:
                    continue

                category = classify_news_category(title, summary)
                related_cos = extract_related_companies(f"{title} {summary} {author}")
                if "DeepMind" in source_name and "Google" not in related_cos:
                    related_cos.append("Google")
                    related_cos.append("DeepMind")
                elif "Hugging Face" in source_name and "Hugging Face" not in related_cos:
                    related_cos.append("Hugging Face")

                news_id = generate_news_id(canon_url, title)

                record = {
                    "news_id": news_id,
                    "title": title,
                    "summary": summary,
                    "content": content,
                    "source_name": source_name,
                    "article_url": canon_url,
                    "author": author,
                    "published_at": iso_date,
                    "category": category,
                    "related_companies": related_cos,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                    "provenance": feed_url
                }

                self.seen_urls.add(canon_url)
                self.seen_titles.add(title_key)
                records.append(record)

        except Exception:
            pass

        return records

    async def collect_from_hn_algolia(self, target_remaining: int, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Collects verified tech journalism stories via Hacker News Algolia Search API."""
        records = []
        hits_per_page = 100
        queries = ["artificial+intelligence", "LLM", "machine+learning", "OpenAI", "Generative+AI"]
        
        for q in queries:
            if len(records) >= target_remaining:
                break
            page = 0
            while page < 5 and len(records) < target_remaining:
                api_url = f"https://hn.algolia.com/api/v1/search_by_date?tags=story&query={q}&hitsPerPage={hits_per_page}&page={page}"
                try:
                    r = await client.get(api_url, timeout=12.0)
                    if r.status_code != 200:
                        break
                    data = r.json()
                    hits = data.get("hits", [])
                    if not hits:
                        break

                    for h in hits:
                        raw_url = h.get("url")
                        title = clean_html(h.get("title", ""))
                        if not raw_url or not title or len(title) < 10:
                            continue

                        canon_url = canonicalize_url(raw_url)
                        title_key = title.lower()

                        if canon_url in self.seen_urls or title_key in self.seen_titles:
                            continue

                        ev = evaluate_ai_evidence(title, "", [])
                        if not ev["is_ai"] and not any(k in title_key for k in ["ai", "llm", "gpt", "model", "neural", "robot"]):
                            continue

                        parsed_netloc = urlparse(canon_url).netloc.replace("www.", "")
                        source_name = parsed_netloc.capitalize() if parsed_netloc else "Tech Media"

                        author = h.get("author") or source_name
                        created_at = h.get("created_at")
                        iso_date = normalize_iso_date(created_at)

                        summary = f"News report from {source_name}: {title}"
                        category = classify_news_category(title, summary)
                        related_cos = extract_related_companies(f"{title} {source_name}")

                        news_id = generate_news_id(canon_url, title)

                        record = {
                            "news_id": news_id,
                            "title": title,
                            "summary": summary,
                            "content": summary,
                            "source_name": source_name,
                            "article_url": canon_url,
                            "author": author,
                            "published_at": iso_date,
                            "category": category,
                            "related_companies": related_cos,
                            "collected_at": datetime.now(timezone.utc).isoformat(),
                            "provenance": f"HN Algolia Search API ({parsed_netloc})"
                        }

                        self.seen_urls.add(canon_url)
                        self.seen_titles.add(title_key)
                        records.append(record)

                        if len(records) >= target_remaining:
                            break

                    page += 1
                    await asyncio.sleep(0.5)
                except Exception:
                    break

        return records

    async def collect_all(self, target_count: int = 1050) -> List[Dict[str, Any]]:
        """Orchestrates collection across feeds and search APIs until target is achieved."""
        all_news = []
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=15.0) as client:
            for name, feed_url in self.RSS_FEEDS:
                feed_records = await self.collect_from_feed(name, feed_url, client)
                all_news.extend(feed_records)
                print(f"Collected {len(feed_records)} articles from {name} (Total so far: {len(all_news)})")

            if len(all_news) < target_count:
                remaining = target_count - len(all_news)
                print(f"\nSupplementing {remaining} articles from HN Algolia AI Tech Media Search...")
                api_records = await self.collect_from_hn_algolia(remaining + 50, client)
                all_news.extend(api_records)
                print(f"Collected {len(api_records)} articles from Algolia API (Total now: {len(all_news)})")

        return all_news
