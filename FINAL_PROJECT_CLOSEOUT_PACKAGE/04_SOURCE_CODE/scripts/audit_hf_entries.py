import json
import httpx
from bs4 import BeautifulSoup
import pandas as pd

with open("data/canonical/canonical_news.jsonl", "r", encoding="utf-8") as f:
    all_news = [json.loads(line) for line in f]

hf_news = [n for n in all_news if n["content"]["data"]["sourceName"] == "Hugging Face Blog"]
print(f"Total Hugging Face Blog entries: {len(hf_news)}")

urls = [n["content"]["data"]["articleUrl"] for n in hf_news]
titles = [n["content"]["data"]["title"] for n in hf_news]
dates = [n["content"]["data"]["publishedAt"] for n in hf_news]

print(f"Unique URLs:   {len(set(urls))} / {len(urls)}")
print(f"Unique titles: {len(set(titles))} / {len(titles)}")
print(f"Min pub date:  {min(dates)}")
print(f"Max pub date:  {max(dates)}")

# Check for non-huggingface URLs
non_hf_urls = [u for u in urls if not u.startswith("https://huggingface.co/blog/")]
print(f"Non-HuggingFace URLs: {len(non_hf_urls)}")

# Check URL HTTP status & title match on a representative sample of 15 articles across years
sample_indices = [0, 5, 20, 50, 100, 200, 300, 400, 500, 600, 700, 800, 850, 900, 914]
print("\n--- Spot-Checking 15 Sample Articles across 2021-2026 ---")

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
with httpx.Client(headers=headers, timeout=10.0, follow_redirects=True) as client:
    for idx in sample_indices:
        item = hf_news[idx]["content"]["data"]
        url = item["articleUrl"]
        title = item["title"]
        pub = item["publishedAt"][:10]
        try:
            r = client.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            page_title = soup.title.string.strip() if soup.title else "No Title"
            print(f"[{idx:3d}] HTTP {r.status_code} | Date: {pub} | Stored: '{title[:40]}...' | Page: '{page_title[:40]}...'")
        except Exception as e:
            print(f"[{idx:3d}] Error checking {url}: {e}")
