import sqlite3

conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
cur = conn.cursor()
cur.execute("PRAGMA table_info(ai_jobs)")
cols = cur.fetchall()
for c in cols:
    print(c)
conn.close()
