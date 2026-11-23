import sqlite3
import httpx
import asyncio

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT DISTINCT source_name FROM ai_jobs")
sources = [r[0] for r in c.fetchall()]

sample_jobs = []
for s in sources:
    c.execute("SELECT job_id, company_name, source_name, application_url, vacancy_status FROM ai_jobs WHERE source_name = ? LIMIT 2", (s,))
    sample_jobs.extend([dict(r) for r in c.fetchall()])
conn.close()

async def check_all_sources():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-Job-Audit/1.0"}
    async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
        for j in sample_jobs:
            url = j["application_url"]
            status = None
            err = None
            try:
                r = await client.head(url)
                if r.status_code == 405 or r.status_code == 403:
                    r = await client.get(url)
                status = r.status_code
            except Exception as e:
                err = type(e).__name__
            print(f"[{j['source_name'][:25]}] {j['job_id']} -> HTTP {status} (err={err})")

if __name__ == "__main__":
    asyncio.run(check_all_sources())
