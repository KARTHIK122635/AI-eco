import sqlite3
from collections import Counter

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT count(*) FROM ai_jobs")
total_jobs = c.fetchone()[0]
print(f"Total jobs: {total_jobs}")

c.execute("SELECT job_status, count(*) FROM ai_jobs GROUP BY job_status")
print("job_status breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT vacancy_status, count(*) FROM ai_jobs GROUP BY vacancy_status")
print("vacancy_status breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT source_name, count(*) FROM ai_jobs GROUP BY source_name")
print("source_name breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT freshness_status, count(*) FROM ai_jobs GROUP BY freshness_status")
print("freshness_status breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

c.execute("SELECT in_rolling_window, count(*) FROM ai_jobs GROUP BY in_rolling_window")
print("in_rolling_window breakdown:")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

# Inspect the 33 records with missing job_status
c.execute("SELECT job_id, job_title, company_name, job_status, vacancy_status, application_url, source_name, posted_at, collected_at FROM ai_jobs WHERE job_status IS NULL OR job_status = ''")
missing_status = c.fetchall()
print(f"\nMissing job_status records count: {len(missing_status)}")
for r in missing_status[:10]:
    print(f"  {r['job_id']} | {r['company_name']} | {r['job_title']} | source={r['source_name']} | app_url={r['application_url']}")

# Inspect the 32 records outside the rolling window
c.execute("SELECT job_id, job_title, company_name, job_status, posted_at, freshness_status, in_rolling_window FROM ai_jobs WHERE in_rolling_window = 0 OR freshness_status = 'OUTSIDE_WINDOW'")
outside_window = c.fetchall()
print(f"\nOutside window jobs count: {len(outside_window)}")
for r in outside_window[:10]:
    print(f"  {r['job_id']} | {r['company_name']} | posted={r['posted_at']} | freshness={r['freshness_status']}")

conn.close()
