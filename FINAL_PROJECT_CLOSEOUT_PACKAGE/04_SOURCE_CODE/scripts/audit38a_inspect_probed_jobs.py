import sqlite3

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT DISTINCT source_name FROM ai_jobs")
sources = [r[0] for r in c.fetchall()]

jobs_to_test = []
for s in sorted(sources):
    c.execute("SELECT job_id, company_name, source_name, application_url, vacancy_status, job_status, posted_at FROM ai_jobs WHERE vacancy_status = 'ACTIVE' AND source_name = ? LIMIT 5", (s,))
    rows = c.fetchall()
    print(f"Source '{s}': found {len(rows)} active jobs")
    jobs_to_test.extend([dict(r) for r in rows])

print(f"Total jobs to test: {len(jobs_to_test)}")
conn.close()
