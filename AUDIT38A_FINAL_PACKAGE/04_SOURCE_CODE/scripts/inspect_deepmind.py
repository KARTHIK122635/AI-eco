import httpx
import feedparser

r = httpx.get("https://deepmind.google/blog/rss.xml", headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True, timeout=10.0)
feed = feedparser.parse(r.text)
e = feed.entries[0]
print("DeepMind entry keys:", e.keys())
print("Title:", e.get("title"))
print("Summary:", e.get("summary"))
print("Description:", e.get("description"))
if "content" in e:
    print("Content:", e.content)
