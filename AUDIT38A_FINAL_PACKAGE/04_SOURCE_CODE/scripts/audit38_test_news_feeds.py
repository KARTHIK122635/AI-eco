import httpx
import feedparser
import asyncio
from datetime import datetime, timezone
import json

feeds = [
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
    ("Google DeepMind Blog", "https://deepmind.google/blog/rss.xml"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("Ars Technica AI", "https://arstechnica.com/tag/ai/feed/"),
    ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss")
]

async def check_feeds():
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-Ecosystem-Audit/1.0"}
    async with httpx.AsyncClient(timeout=15.0, headers=headers, follow_redirects=True) as client:
        for s_name, feed_url in feeds:
            t0 = datetime.now(timezone.utc)
            status_code = None
            err = None
            entry_count = 0
            latest_pub = None
            try:
                r = await client.get(feed_url)
                status_code = r.status_code
                t1 = datetime.now(timezone.utc)
                latency_ms = int((t1 - t0).total_seconds() * 1000)
                if status_code == 200:
                    parsed = feedparser.parse(r.text)
                    entry_count = len(parsed.entries)
                    if parsed.entries:
                        latest_pub = parsed.entries[0].get("published") or parsed.entries[0].get("updated")
            except Exception as e:
                t1 = datetime.now(timezone.utc)
                latency_ms = int((t1 - t0).total_seconds() * 1000)
                err = str(e)
            
            results.append({
                "source_name": s_name,
                "feed_url": feed_url,
                "http_status": status_code,
                "latency_ms": latency_ms,
                "entry_count": entry_count,
                "latest_entry_pub": latest_pub,
                "retrieval_timestamp": t0.isoformat(),
                "error": err
            })
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(check_feeds())
