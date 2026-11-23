import httpx
import feedparser

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

more_feeds = [
    ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss"),
    ("The Verge Full", "https://www.theverge.com/rss/index.xml"),
    ("Google DeepMind", "https://deepmind.google/blog/rss.xml"),
    ("ZDNet AI", "https://www.zdnet.com/topic/artificial-intelligence/rss.xml"),
    ("InfoQ AI", "https://feed.infoq.com/ai-ml-data-eng/news")
]

for name, url in more_feeds:
    try:
        r = httpx.get(url, headers=headers, follow_redirects=True, timeout=10.0)
        feed = feedparser.parse(r.text)
        print(f"{name:20} | HTTP {r.status_code} | Entries: {len(feed.entries)}")
    except Exception as e:
        print(f"{name:20} | Error: {e}")

# Test HN Algolia pagination
print("\nTesting HN Algolia pagination...")
r = httpx.get("https://hn.algolia.com/api/v1/search_by_date?tags=story&query=AI&hitsPerPage=100&page=0", timeout=10.0)
data = r.json()
print(f"HN page 0 hits: {len(data.get('hits', []))}, total pages: {data.get('nbPages')}")
