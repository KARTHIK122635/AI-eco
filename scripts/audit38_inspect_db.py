import sqlite3
import json

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in c.fetchall()]

info = {}
for t in tables:
    c.execute(f"SELECT count(*) FROM {t}")
    cnt = c.fetchone()[0]
    c.execute(f"PRAGMA table_info({t})")
    cols = [r[1] for r in c.fetchall()]
    info[t] = {'count': cnt, 'columns': cols}

print(json.dumps(info, indent=2))
conn.close()
