import sqlite3

def analyze():
    conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
    c = conn.cursor()

    tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print("Database Tables:")
    for t in tables:
        cnt = c.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
        print(f'{t:45s}: {cnt:5d} rows')

    # Count unique (record_id, entity_type, field_name) keys across all enrichment tables
    all_keys = set()
    for t in tables:
        if 'enrichment' in t or 'review_queue' in t:
            try:
                for r in c.execute(f'SELECT DISTINCT record_id, entity_type, field_name FROM "{t}"').fetchall():
                    all_keys.add((r[0], r[1], r[2]))
            except Exception:
                pass

    print(f"\nTotal unique (record_id, entity_type, field_name) keys found across all tables: {len(all_keys)}")

    # Count unique attempt IDs across all log and result tables
    all_attempts = set()
    for t in tables:
        if 'logs' in t or 'results' in t or 'queue' in t:
            try:
                for r in c.execute(f'SELECT DISTINCT attempt_id FROM "{t}"').fetchall():
                    if r[0]:
                        all_attempts.add(r[0])
            except Exception:
                pass
    print(f"Total unique attempt_ids found across all tables: {len(all_attempts)}")

if __name__ == '__main__':
    analyze()
