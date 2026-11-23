import sqlite3

w_db = 'data/working/rolling_ai_ecosystem.db'
conn = sqlite3.connect(w_db)
c = conn.cursor()

cols = [r[1] for r in c.execute("PRAGMA table_info(collection_logs)").fetchall()]
print("collection_logs columns:", cols)

rows = c.execute("SELECT * FROM collection_logs").fetchall()
print(f"Total rows in collection_logs: {len(rows)}")
for r in rows:
    print(" ", dict(zip(cols, r)))

conn.close()
