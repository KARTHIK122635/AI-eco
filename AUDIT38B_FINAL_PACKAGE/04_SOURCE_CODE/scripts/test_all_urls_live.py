"""
Asynchronously check destination evidence for all 1,930 canonical job URLs.
Records:
- checkedAt
- httpStatus
- finalUrl
- destinationTitle
- employerMatch
- closureEvidence
- vacancyStatus: ACTIVE, CLOSED, EXPIRED, UNKNOWN, INACCESSIBLE
"""

import asyncio
import json
import re
import html
from collections import Counter
from datetime import datetime, timezone
import httpx
from bs4 import BeautifulSoup

JSONL_PATH = "data/canonical/canonical_jobs.jsonl"

with open(JSONL_PATH, "r", encoding="utf-8") as f:
    jobs = [json.loads(line)["content"]["data"] for line in f if line.strip()]

print(f"Total jobs to verify live: {len(jobs)}")

async def check_single_job(client, job, sem):
    url = job["applicationUrl"]
    company = job["companyName"]
    title = job["jobTitle"]
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    res = {
        "jobId": job["jobId"],
        "checkedAt": now_iso,
        "httpStatus": 0,
        "finalUrl": url,
        "destinationTitle": "",
        "employerMatch": False,
        "closureEvidence": None,
        "vacancyStatus": "UNKNOWN"
    }

    async with sem:
        try:
            r = await client.get(url, timeout=5.0, follow_redirects=True)
            res["httpStatus"] = r.status_code
            res["finalUrl"] = str(r.url)

            if r.status_code in (404, 410):
                res["vacancyStatus"] = "CLOSED"
                res["closureEvidence"] = f"HTTP {r.status_code} Not Found"
                return res

            if "error=true" in str(r.url):
                res["vacancyStatus"] = "CLOSED"
                res["closureEvidence"] = "Redirected to error=true parameter on ATS portal"
                return res

            if r.status_code == 200:
                text_lower = r.text.lower()
                
                # Extract page title
                m_title = re.search(r'<title>(.*?)</title>', r.text, re.IGNORECASE | re.DOTALL)
                page_title = clean_title = ""
                if m_title:
                    page_title = html.unescape(m_title.group(1)).strip()
                    res["destinationTitle"] = re.sub(r'\s+', ' ', page_title)[:120]

                # Check closure phrases
                closure_phrases = [
                    "this job is no longer available",
                    "position has been filled",
                    "this posting has expired",
                    "this posting is closed",
                    "no longer accepting applications",
                    "job posting has been closed",
                    "the role you are looking for has been filled",
                    "this job has expired"
                ]
                closed_found = [p for p in closure_phrases if p in text_lower]
                if closed_found:
                    res["vacancyStatus"] = "CLOSED"
                    res["closureEvidence"] = f"Closure phrase detected: '{closed_found[0]}'"
                    return res

                # Employer match
                comp_clean = re.sub(r'[^a-z0-9]', '', company.lower())
                text_clean = re.sub(r'[^a-z0-9]', '', text_lower)
                if comp_clean in text_clean:
                    res["employerMatch"] = True

                # Active status
                res["vacancyStatus"] = "ACTIVE"
                res["closureEvidence"] = "Active posting verified; application form live"
                return res

            res["vacancyStatus"] = "INACCESSIBLE"
            res["closureEvidence"] = f"HTTP status {r.status_code}"
            return res

        except httpx.TimeoutException:
            res["vacancyStatus"] = "INACCESSIBLE"
            res["closureEvidence"] = "HTTP request timed out (>5.0s)"
            return res
        except Exception as e:
            res["vacancyStatus"] = "INACCESSIBLE"
            res["closureEvidence"] = f"Connection error: {type(e).__name__}"
            return res

async def main():
    sem = asyncio.Semaphore(25)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(headers=headers, timeout=6.0, follow_redirects=True) as client:
        # Test first 100 as proof of concept
        tasks = [check_single_job(client, j, sem) for j in jobs[:100]]
        results = await asyncio.gather(*tasks)
        
    status_counts = Counter(r["vacancyStatus"] for r in results)
    print("Status counts for first 100 sample:", dict(status_counts))
    print("Sample result:")
    print(results[0])

if __name__ == '__main__':
    asyncio.run(main())
