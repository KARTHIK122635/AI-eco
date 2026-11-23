import httpx
import re
from datetime import datetime, timezone

# Test checking some URLs to see if any are 404 or redirected
urls_to_test = [
    # Live URL
    "https://job-boards.greenhouse.io/anthropic/jobs/5456619008",
    # Closed URLs
    "https://job-boards.greenhouse.io/anthropic/jobs/12345",
    "https://jobs.lever.co/palantir/00000000-0000-0000-0000-000000000000"
]

client = httpx.Client(timeout=5.0, follow_redirects=True, headers={"User-Agent": "AIEcosystemChecker/1.0"})
for u in urls_to_test:
    try:
        r = client.get(u)
        is_closed = (r.status_code in (404, 410)) or ("error=true" in str(r.url)) or ("no longer available" in r.text.lower())
        print(f"URL: {u[:50]}... -> status: {r.status_code}, closed: {is_closed}")
    except Exception as e:
        print(f"Error {u}: {e}")
