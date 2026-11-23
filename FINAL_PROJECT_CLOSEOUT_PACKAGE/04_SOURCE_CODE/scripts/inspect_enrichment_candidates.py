import sqlite3

conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
cur = conn.cursor()

tables = ['ai_startups', 'ai_products', 'ai_research_papers', 'ai_news', 'ai_jobs']
for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [r[1] for r in cur.fetchall()]
    cur.execute(f"SELECT count(*) FROM {t}")
    total = cur.fetchone()[0]
    print(f"=== {t} (total {total}) ===")
    for col in cols:
        cur.execute(f"SELECT count(*) FROM {t} WHERE {col} IS NULL OR {col} = '' OR {col} = '[]'")
        cnt = cur.fetchone()[0]
        if cnt > 0:
            pct = cnt / total * 100
            print(f"  {col:30s}: {cnt:5d} ({pct:5.1f}%)")

conn.close()
