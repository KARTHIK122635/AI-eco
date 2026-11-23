import sqlite3
import httpx
import asyncio
from collections import Counter

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Get 5 active jobs per source
c.execute("SELECT DISTINCT source_name FROM ai_jobs")
sources = [r[0] for r in c.fetchall()]

jobs_to_test = []
for s in sources:
    c.execute("SELECT job_id, company_name, source_name, application_url, vacancy_status, job_status, posted_at FROM ai_jobs WHERE vacancy_status = 'ACTIVE' AND source_name = ? LIMIT 5", (s,))
    jobs_to_test.extend([dict(r) for r in c.fetchall()])

conn.close()
print(f"Total jobs to probe: {len(jobs_to_test)}")

async def probe_jobs():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-Job-Audit/1.0"}
    results = []
    async with httpx.AsyncClient(timeout=12.0, headers=headers, follow_redirects=True) as client:
        for j in jobs_to_test:
            url = j["application_url"]
            code = None
            err = None
            accessible = False
            is_closed = False
            try:
                r = await client.get(url)
                code = r.status_code
                if code == 200:
                    text_lower = r.text.lower()
                    # Check for ATS closed indicators
                    if "this job is no longer available" in text_lower or "job posting has expired" in text_lower or "no longer accepting applications" in text_lower:
                        is_closed = True
                        accessible = True
                    else:
                        accessible = True
                elif code in (404, 410):
                    accessible = False
                    is_closed = True
                else:
                    accessible = False
            except Exception as e:
                err = type(e).__name__
                accessible = False
            
            results.append({
                "job_id": j["job_id"],
                "company_name": j["company_name"],
                "source_name": j["source_name"],
                "url": url,
                "http_status": code,
                "error": err,
                "accessible": accessible,
                "is_closed": is_closed
            })
    
    acc_count = sum(1 for r in results if r["accessible"] and not r["is_closed"])
    closed_count = sum(1 for r in results if r["is_closed"])
    inacc_count = sum(1 for r in results if not r["accessible"] and not r["is_closed"])
    print(f"Probe Results across {len(results)} jobs:")
    print(f"  Active/Accessible: {acc_count} ({acc_count/len(results)*100:.1f}%)")
    print(f"  Closed/Expired:    {closed_count} ({closed_count/len(results)*100:.1f}%)")
    print(f"  Inaccessible:      {inacc_count} ({inacc_count/len(results)*100:.1f}%)")
    return results

if __name__ == "__main__":
    asyncio.run(probe_jobs())
