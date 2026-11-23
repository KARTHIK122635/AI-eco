import httpx
from datetime import datetime, timezone

client = httpx.Client(timeout=10.0, headers={"User-Agent": "AIEcosystemCollector/1.0"})

r = client.get("https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true")
if r.status_code == 200:
    jobs = r.json().get("jobs", [])
    deadlines = [j.get("application_deadline") for j in jobs if j.get("application_deadline")]
    print(f"Anthropic jobs with application_deadline: {len(deadlines)}")
    if deadlines:
        print("Sample deadlines:", deadlines[:5])

r_db = client.get("https://boards-api.greenhouse.io/v1/boards/databricks/jobs")
if r_db.status_code == 200:
    jobs_db = r_db.json().get("jobs", [])
    print(f"Databricks jobs: {len(jobs_db)}")
    deadlines_db = [j.get("application_deadline") for j in jobs_db if j.get("application_deadline")]
    print(f"Databricks with deadline: {len(deadlines_db)}")

# Check Arbeitnow
r_an = client.get("https://www.arbeitnow.com/api/job-board-api?page=8")
if r_an.status_code == 200:
    jobs_an = r_an.json().get("data", [])
    print(f"Arbeitnow page 8 jobs: {len(jobs_an)}")
    if jobs_an:
        print("Arbeitnow sample keys:", list(jobs_an[0].keys()))
        print("Arbeitnow sample created_at:", jobs_an[0].get("created_at"))
