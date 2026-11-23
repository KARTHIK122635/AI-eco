import httpx
import feedparser

r = httpx.get('https://huggingface.co/blog/feed.xml', follow_redirects=True, timeout=10.0)
feed = feedparser.parse(r.text)
print('Feed title:', feed.feed.get('title'))
print('Total entries in feed:', len(feed.entries))

for i in [0, 10, 50, 100, 300, 600, 900]:
    if i < len(feed.entries):
        e = feed.entries[i]
        print(f"[{i:3d}] Published: {e.get('published', '')[:20]:20} | Title: {e.get('title', '')[:50]} | Link: {e.get('link')}")
