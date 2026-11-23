import sqlite3

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
c = conn.cursor()
c.execute("SELECT vacancy_status, count(*) FROM ai_jobs WHERE source_name = 'Arbeitnow API' GROUP BY vacancy_status")
print(c.fetchall())
conn.close()
