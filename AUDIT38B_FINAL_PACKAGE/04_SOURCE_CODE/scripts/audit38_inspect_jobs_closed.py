import sqlite3

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT job_id, company_name, job_title, job_status, vacancy_status, application_url, posted_at, collected_at FROM ai_jobs WHERE vacancy_status = 'CLOSED' OR job_status = 'CLOSED'")
for r in c.fetchall():
    print(dict(r))
conn.close()
