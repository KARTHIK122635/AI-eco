import httpx
import re
from bs4 import BeautifulSoup

client = httpx.Client(timeout=10.0, headers={"User-Agent": "AIEcosystemCollector/1.0"})

r = client.get("https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true")
if r.status_code == 200:
    jobs = r.json().get("jobs", [])
    print(f"Total Anthropic jobs: {len(jobs)}")
    salary_count = 0
    for j in jobs[:20]:
        html = j.get("content", "")
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ")
        # Search for salary pattern
        # e.g. $180,000 - $240,000 or $180k - $240k
        m = re.search(r'\$([0-9]{2,3}(?:,[0-9]{3})*)\s*(?:-|–|to)\s*\$([0-9]{2,3}(?:,[0-9]{3})*)', text)
        if m:
            salary_count += 1
            print(f"Job: {j.get('title')}")
            print(f"  Found salary: min={m.group(1)}, max={m.group(2)}")
    print(f"Sample 20 checked, found salaries in {salary_count}")
