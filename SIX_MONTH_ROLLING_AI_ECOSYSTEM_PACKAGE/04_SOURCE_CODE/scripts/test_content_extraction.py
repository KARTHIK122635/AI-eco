import httpx
import feedparser

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

feeds_to_test = [
    ("Google DeepMind", "https://deepmind.google/blog/rss.xml"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("Ars Technica AI", "https://arstechnica.com/tag/ai/feed/"),
    ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss"),
    ("MIT Tech Review", "https://www.technologyreview.com/topic/artificial-intelligence/feed/"),
    ("MarkTechPost", "https://www.marktechpost.com/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("ZDNet AI", "https://www.zdnet.com/topic/artificial-intelligence/rss.xml"),
    ("InfoQ AI", "https://feed.infoq.com/ai-ml-data-eng/news")
]

for name, url in feeds_to_test:
    r = httpx.get(url, headers=headers, follow_redirects=True, timeout=10.0)
    feed = feedparser.parse(r.text)
    if feed.entries:
        e = feed.entries[0]
        has_summary = bool(e.get("summary") or e.get("description"))
        has_content = bool("content" in e and e.content)
        print(f"{name:20} | Entries: {len(feed.entries):3d} | Has Summary: {has_summary} | Has Content: {has_content}")
        if has_summary:
            s_text = (e.get("summary") or e.get("description"))[:80].replace("\n", " ")
            print(f"   Summary sample: {s_text}...")
