import sqlite3

w_db = 'data/working/rolling_ai_ecosystem.db'
conn = sqlite3.connect(w_db)
c = conn.cursor()

print("ai_jobs source_name counts:")
for row in c.execute("SELECT source_name, count(*) FROM ai_jobs GROUP BY source_name").fetchall():
    print(" ", row)

print("\nai_jobs (source_name, job_status) counts:")
for row in c.execute("SELECT source_name, job_status, count(*) FROM ai_jobs GROUP BY source_name, job_status").fetchall():
    print(" ", row)

conn.close()
