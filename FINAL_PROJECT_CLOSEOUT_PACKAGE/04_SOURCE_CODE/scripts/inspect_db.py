import sqlite3

conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print('Tables in ai_ecosystem.db:')
for t in tables:
    t_name = t[0]
    c.execute(f"PRAGMA table_info({t_name});")
    cols = [f"{row[1]} ({row[2]})" for row in c.fetchall()]
    c.execute(f"SELECT count(*) FROM {t_name};")
    cnt = c.fetchone()[0]
    print(f"\n--- {t_name} ({cnt} rows) ---")
    print(", ".join(cols))
conn.close()
