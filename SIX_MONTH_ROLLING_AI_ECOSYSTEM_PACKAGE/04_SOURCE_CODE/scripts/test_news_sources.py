import httpx
import feedparser
import asyncio

test_feeds = [
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge AI", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
    ("MIT Tech Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed/"),
    ("Unite.AI", "https://www.unite.ai/feed/"),
    ("MarkTechPost", "https://www.marktechpost.com/feed/"),
    ("Artificial Intelligence News", "https://www.artificialintelligence-news.com/feed/"),
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
    ("Ars Technica AI", "https://arstechnica.com/tag/ai/feed/")
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Testing RSS Feeds...")
for name, url in test_feeds:
    try:
        r = httpx.get(url, headers=headers, follow_redirects=True, timeout=10.0)
        feed = feedparser.parse(r.text)
        print(f"  {name:30} | HTTP {r.status_code} | Entries: {len(feed.entries)}")
        if feed.entries:
            e = feed.entries[0]
            print(f"    Sample: '{e.get('title', '')[:60]}' | Date: {e.get('published', '')}")
    except Exception as exc:
        print(f"  {name:30} | Error: {exc}")

print("\nTesting HN Algolia AI News Search API...")
try:
    hn_url = "https://hn.algolia.com/api/v1/search_by_date?tags=story&query=artificial+intelligence&hitsPerPage=50"
    r = httpx.get(hn_url, timeout=10.0)
    data = r.json()
    print(f"  HN Algolia AI Search | HTTP {r.status_code} | Hits returned: {len(data.get('hits', []))} | Total hits: {data.get('nbHits')}")
    if data.get('hits'):
        sample = data['hits'][0]
        print(f"    Sample: '{sample.get('title')}' | URL: {sample.get('url')}")
except Exception as exc:
    print(f"  HN Algolia Error: {exc}")
