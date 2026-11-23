import httpx
from bs4 import BeautifulSoup

client = httpx.Client(timeout=6.0, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

# Check a couple of URLs
test_urls = [
    "https://job-boards.greenhouse.io/anthropic/jobs/5456619008",
    "https://job-boards.greenhouse.io/anthropic/jobs/1111111111", # Non-existent / closed
    "https://jobs.lever.co/palantir/6ed76ce8-4156-4b60-b120-403538bd66cd",
    "https://jobs.lever.co/palantir/00000000-0000-0000-0000-000000000000" # Non-existent / closed
]

for u in test_urls:
    try:
        r = client.get(u)
        print(f"URL: {u}")
        print(f"  Status code: {r.status_code}")
        print(f"  Final URL: {r.url}")
        is_closed = (r.status_code in (404, 410)) or ("no longer available" in r.text.lower()) or ("job not found" in r.text.lower())
        print(f"  Detected closed: {is_closed}")
    except Exception as e:
        print(f"Error {u}: {e}")
