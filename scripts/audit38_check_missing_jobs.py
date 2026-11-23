import sqlite3

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT job_id, company_name, job_title, source_name, vacancy_status, application_url, posted_at, collected_at FROM ai_jobs WHERE job_status IS NULL")
rows = c.fetchall()
print(f"Total rows with job_status IS NULL: {len(rows)}")
src_counts = {}
for r in rows:
    src_counts[r['source_name']] = src_counts.get(r['source_name'], 0) + 1
    print(f"{r['job_id']} :: {r['company_name'][:25]} :: {r['source_name']} :: vac={r['vacancy_status']} :: url={r['application_url']}")
print("\nSources breakdown:", src_counts)
conn.close()
